use std::sync::{Arc, Mutex};
use rust_decimal::{prelude::FromPrimitive, Decimal};
use crossterm::event::{Event as CrosstermEvent, KeyCode};
use tui_input::backend::crossterm::EventHandler;
use sqlx::{Row, FromRow, PgPool};
use anyhow::{Result, anyhow};
use time::{Date, OffsetDateTime, Time};
use crate::{
    event::{Event, InputBlacklist},
    model::{
        app::App,
        client::{self, Client},
        common::{Bank, GetDBErr, InputMode, PaymentData, Popup, Screen, SubScreen, TimeoutType, User},
        db_obj::{Branch, Locker}, pkgadmin,
    },
};

pub async fn update(app: &mut Arc<Mutex<App>>, pool: &PgPool, event: Event) -> Result<()> {
    match event {
        Event::TryGetUserLocker(username, locker_id) => {
            if username.is_empty() || locker_id.is_empty() { return Ok(()); }

            let locker_id = locker_id.parse::<i64>().expect("could not parse locker_id in TryGetUserLocker event");

            if let Some(res) =
                sqlx::query("SELECT * FROM shippings.lockers WHERE locker_id=$1")
                    .bind(locker_id)
                    .fetch_optional(pool)
                    .await?
            {
                if username == res.get::<String, _>("client") {
                    let mut app_lock = app.lock().unwrap();
                    match &mut app_lock.user {
                        Some(User::Client(client_data)) => {
                            if locker_id == client_data.active_locker.as_mut().unwrap().get_id() {
                                client_data.get_db_err = Some(GetDBErr::LockerSameAsActive);
                                return Ok(())
                            }

                            if sqlx::query("SELECT COUNT(*) AS package_count FROM shippings.packages WHERE locker_id=$1")
                                .bind(locker_id)
                                .fetch_one(pool)
                                .await?
                                .get::<i64, _>("package_count") >= 5
                            {
                                client_data.get_db_err = Some(GetDBErr::LockerTooManyPackages);
                                return Ok(())
                            }

                            let locker_packages_weight =
                                sqlx::query(
                            "
                                    SELECT SUM(package_weight) as weight_sum FROM shippings.packages
                                    INNER JOIN shippings.package_descriptions AS descriptions
                                    ON packages.tracking_number=descriptions.tracking_number
                                    WHERE locker_id=$1
                                "
                                )
                                .bind(locker_id)
                                .fetch_one(pool)
                                .await?
                                .try_get::<Decimal, _>("weight_sum")
                                .unwrap_or(Decimal::new(0, 0));
                            
                            let selected_packages_weight =
                                client_data.packages.as_ref().unwrap().selected_packages.as_ref().unwrap()
                                .iter()
                                .map(|package| package.weight)
                                .sum::<Decimal>();

                            if locker_packages_weight + selected_packages_weight >= Decimal::new(500000, 0)
                            {
                                client_data.get_db_err = Some(GetDBErr::LockerWeightTooBig(Decimal::new(500000, 0) - locker_packages_weight));
                                return Ok(());
                            }

                            let locker_row =
                                sqlx::query(
                                "
                                    SELECT lockers.*, countries.*, warehouses.*,
                                    COUNT(packages.tracking_number) AS package_count FROM shippings.lockers AS lockers
                                    LEFT JOIN shippings.packages AS packages ON lockers.locker_id=packages.locker_id
                                    INNER JOIN locations.countries AS countries ON lockers.country=countries.country_id
                                    INNER JOIN locations.warehouses AS warehouses ON lockers.warehouse=warehouses.warehouse_id
                                    WHERE lockers.locker_id=$1
                                    GROUP BY lockers.locker_id, countries.country_id, warehouses.warehouse_id
                                    ORDER BY package_count DESC
                                ")
                                .bind(locker_id)
                                .fetch_one(pool)
                                .await?;

                            client_data.send_to_locker = Some(Locker::from_row(&locker_row).expect("could not build locker from row"));

                            client_data.send_to_client = Some(
                                Client {
                                    username: username.clone(),
                                    first_name: String::from(""),
                                    last_name: String::from(""),
                                }
                            );
                        
                            app_lock.enter_popup(Some(Popup::OnlinePayment), pool).await;
                        }
                        Some(User::PkgAdmin(pkgadmin_data)) => {
                            let package = pkgadmin_data.add_package.as_ref().unwrap();

                            if sqlx::query("SELECT COUNT(*) AS package_count FROM shippings.packages WHERE locker_id=$1")
                                .bind(package.locker.value().parse::<i32>().expect("could not parse locker value"))
                                .fetch_one(pool)
                                .await?
                                .get::<i64, _>("package_count") >= 5
                            {
                                pkgadmin_data.get_db_err = Some(GetDBErr::LockerTooManyPackages);
                                return Ok(())
                            }
                            
                            let package_weight_decimal = Decimal::from_str_exact(package.weight.value()).expect("could not parse package weight");
                            if sqlx::query(
                                    "
                                        SELECT SUM(package_weight) as weight_sum FROM shippings.packages AS packages
                                        INNER JOIN shippings.package_descriptions AS descriptions
                                        ON packages.tracking_number=descriptions.tracking_number
                                        WHERE locker_id=$1
                                    "
                                )
                                .bind(package.locker.value().parse::<i32>().expect("could not parse locker value"))
                                .fetch_one(pool)
                                .await?
                                .try_get::<Decimal, _>("weight_sum")
                                .unwrap_or(Decimal::new(0, 0))
                                >
                                package_weight_decimal
                            {
                                pkgadmin_data.get_db_err = Some(GetDBErr::LockerWeightTooBig(Decimal::new(500000, 0) - package_weight_decimal));
                                return Ok(());
                            }

                            app_lock.enter_popup(Some(Popup::SelectPayment), pool).await;
                        }
                        _ => {}
                    }
                    return Ok(());
                }
            }

            set_getdberr(app, GetDBErr::InvalidUserLocker);

            Ok(())
        }
        Event::TryGetUserBranch(username, branch_id) => {
            if username.is_empty() || branch_id.is_empty() { return Ok(()); }

            let branch_id = branch_id.parse::<i32>().expect("could not parse locker_id in TryGetUserLocker event");

            if let Some(res) =
                sqlx::query("SELECT * FROM users.natural_clients WHERE username=$1")
                    .bind(&username)
                    .fetch_optional(pool)
                    .await?
            {
                if branch_id == res.get::<i32, _>("affiliated_branch") {
                    let mut app_lock = app.lock().unwrap();
                    match &mut app_lock.user {
                        Some(User::Client(client_data)) => {
                            let branch_res =
                                sqlx::query(
                                    "
                                        SELECT * FROM locations.branches AS branches
                                        INNER JOIN locations.warehouses AS warehouses ON branches.warehouse_id=warehouses.warehouse_id
                                        INNER JOIN locations.buildings AS buildings ON branches.branch_id=buildings.building_id
                                        WHERE branch_id=$1
                                    "
                                )
                                .bind(branch_id)
                                .fetch_one(pool)
                                .await?;

                            client_data.send_to_branch = Some(Branch::from_row(&branch_res)?);

                            client_data.send_to_client = Some(
                                Client {
                                    username,
                                    first_name: String::from(""),
                                    last_name: String::from(""),
                                }
                            );
                            
                            app_lock.enter_popup(Some(Popup::OnlinePayment), pool).await;
                        }
                        Some(User::PkgAdmin(_)) => {
                            app_lock.get_shortest_branch_branch(pool).await?;

                            let pkgadmin_data = app_lock.get_pkgadmin_mut();
                            let package = pkgadmin_data.add_package.as_mut().unwrap();
                            package.payment = {
                                let amount_calc =
                                    package.route_distance.unwrap() as f64 * 0.00003 +
                                    package.weight.value().parse::<f64>().expect("could not parse weight as f64") * 0.0005;
                                Some(
                                    PaymentData {
                                        amount:
                                            Decimal::from_f64(amount_calc)
                                            .expect("could not get payment amount from amount_calc")
                                            .round_dp_with_strategy(2, rust_decimal::RoundingStrategy::MidpointNearestEven),
                                        transaction_id: None,
                                        payment_type: None
                                    }
                                )
                            };
                            
                            app_lock.enter_popup(Some(Popup::SelectPayment), pool).await;
                        }
                        _ => unimplemented!("Event::TryGetUserBranch for user {:?}", app_lock.user)
                    }
                }
            }

            set_getdberr(app, GetDBErr::InvalidUserBranch);

            Ok(())
        }
        Event::TryGetUserDelivery(username) => {
            if username.is_empty() { return Ok(()); }

            {
                let app_lock = app.lock().unwrap();
                match &app_lock.user {
                    Some(User::Client(client_data)) => {
                        if let Some(GetDBErr::InvalidUserDelivery(3)) = client_data.get_db_err { return Ok(()); }
                    }
                    _ => unimplemented!("Event::TryGetUserDelivery for user {:?}", app_lock.user)
                }
            }

            let motorcyclists =
                sqlx::query(
                    "
                        SELECT * FROM users.natural_clients
                        INNER JOIN vehicles.motorcyclists AS motorcyclists ON natural_clients.affiliated_branch=motorcyclists.affiliated_branch
                        INNER JOIN vehicles.vehicles AS vehicles ON motorcyclists.motorcycle=vehicles.vin_vehicle
                        WHERE natural_clients.username=$1
                    "
                )
                .bind(&username)
                .fetch_all(pool)
                .await?;

            if motorcyclists.is_empty() {
                let mut app_lock = app.lock().unwrap();
                if let Some(GetDBErr::InvalidUserDelivery(2)) = app_lock.get_client_ref().get_db_err {
                    app_lock.add_timeout(30, 1000, TimeoutType::GetUserDelivery);
                }
                match &mut app_lock.user {
                    Some(User::Client(client_data)) => {
                        client_data.get_db_err =
                            if let Some(GetDBErr::InvalidUserDelivery(val)) = client_data.get_db_err {
                                Some(GetDBErr::InvalidUserDelivery(val + 1))
                            } else {
                                Some(GetDBErr::InvalidUserDelivery(1))
                            }
                    }
                    _ => unimplemented!("Event::TryGetUserDelivery for user {:?}", app_lock.user)
                }
                app_lock.toggle_displaymsg();
                return Ok(());
            }

            let (packages_weight, packages_width, packages_height, packages_length) =
                {
                    let app_lock = app.lock().unwrap();

                    let (mut weight_count, mut width_count, mut height_count, mut length_count) =
                        (Decimal::new(0, 0), Decimal::new(0, 0), Decimal::new(0, 0), Decimal::new(0, 0));

                    match &app_lock.user {
                        Some(User::Client(client_data)) => {
                            for package in client_data.packages.as_ref().unwrap().selected_packages.as_ref().unwrap() {
                                weight_count += package.weight;
                                width_count += package.width;
                                height_count += package.height;
                                length_count += package.length;
                            }
                        }
                        _ => unimplemented!("Event::TryGetUserDelivery for user {:?}", app_lock.user)
                    }

                    (weight_count, width_count, height_count, length_count)
                };

            for motorcyclist in motorcyclists {
                if motorcyclist.get::<Decimal, _>("weight_capacity") >= packages_weight
                && motorcyclist.get::<Decimal, _>("width_capacity") >= packages_width
                && motorcyclist.get::<Decimal, _>("height_capacity") >= packages_height
                && motorcyclist.get::<Decimal, _>("length_capacity") >= packages_length
                {
                    let mut app_lock = app.lock().unwrap();

                    match &mut app_lock.user {
                        Some(User::Client(client_data)) => {
                            client_data.send_to_client = Some(
                                Client {
                                    username,
                                    first_name: String::from(""),
                                    last_name: String::from(""),
                                }
                            );
                            app_lock.enter_popup(Some(Popup::OnlinePayment), pool).await;
                        }
                        _ => unimplemented!("Event::TryGetUserDelivery for user {:?}", app_lock.user)
                    }

                    return Ok(());
                }
            }

            app.lock().unwrap().toggle_displaymsg();
            set_getdberr(app, GetDBErr::NoCompatBranchDelivery);

            Ok(())
        }
        _ => panic!("An event of type {:?} was passed to the db::tryget update function", event)
    }
}

fn set_getdberr(app: &mut Arc<Mutex<App>>, err: GetDBErr) {
    let mut app_lock = app.lock().unwrap();

    let get_db_err =
        match &mut app_lock.user {
            Some(User::Client(client_data)) => {
                &mut client_data.get_db_err
            }
            Some(User::PkgAdmin(pkgadmin_data)) => {
                &mut pkgadmin_data.get_db_err
            }
            _ => unimplemented!("update::db::tryget::set_getdberr for user {:?}", app_lock.user)
        };
    
    *get_db_err = Some(err);
}