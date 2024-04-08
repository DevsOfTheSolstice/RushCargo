use std::sync::{Arc, Mutex};
use rust_decimal::{prelude::FromPrimitive, Decimal};
use crossterm::event::{Event as CrosstermEvent, KeyCode};
use tui_input::backend::crossterm::EventHandler;
use sqlx::{pool, postgres::PgRow, FromRow, PgPool, Row};
use anyhow::{Result, anyhow};
use time::{Date, OffsetDateTime, Time};
use crate::{
    event::{Event, InputBlacklist},
    model::{
        app::App,
        client::{self, Client},
        common::{Bank, GetDBErr, InputMode, PaymentData, PaymentType, Popup, Screen, ShippingData, SubScreen, TimeoutType, User},
        db_obj::{Branch, Locker, ShippingGuideType}, pkgadmin,
    },
};

const PRICE_DIST_MULT: f64 = 0.00001;
const PRICE_WEIGHT_MULT: f64 = 0.0005;
const LOCKER_WEIGHT_MAX: i64 = 500000;
const LOCKER_PKG_NUM_MAX: i64 = 5;

pub async fn update(app: &mut Arc<Mutex<App>>, pool: &PgPool, event: Event) -> Result<()> {
    match event {
        Event::TryGetUserLocker(username, locker_id) => {
            async fn get_locker_row(pool: &PgPool, locker_id: i64) -> Result<PgRow> {
                Ok(
                    sqlx::query("
                        SELECT lockers.*, countries.*, warehouses.*,
                        COUNT(packages.tracking_number) AS package_count FROM shippings.lockers AS lockers
                        LEFT JOIN shippings.packages AS packages ON lockers.locker_id=packages.locker_id
                        INNER JOIN locations.countries AS countries ON lockers.country=countries.country_id
                        INNER JOIN locations.warehouses AS warehouses ON lockers.warehouse=warehouses.warehouse_id
                        WHERE lockers.locker_id=$1
                        GROUP BY lockers.locker_id, countries.country_id, warehouses.warehouse_id
                        ORDER BY package_count DESC
                    ").bind(locker_id).fetch_one(pool).await?
                )
            }

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
                        Some(User::Client(_)) => {
                            {
                                let client_data = app_lock.get_client_mut();

                                if locker_id == client_data.active_locker.as_mut().unwrap().get_id() {
                                    client_data.get_db_err = Some(GetDBErr::LockerSameAsActive);
                                    return Ok(())
                                }

                                if sqlx::query("SELECT COUNT(*) AS package_count FROM shippings.packages WHERE locker_id=$1")
                                    .bind(locker_id)
                                    .fetch_one(pool)
                                    .await?
                                    .get::<i64, _>("package_count") >= LOCKER_PKG_NUM_MAX
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

                                if locker_packages_weight + selected_packages_weight >= Decimal::new(LOCKER_WEIGHT_MAX, 0)
                                {
                                    client_data.get_db_err = Some(GetDBErr::LockerWeightTooBig(Decimal::new(LOCKER_WEIGHT_MAX, 0) - locker_packages_weight));
                                    return Ok(());
                                }

                                let locker_row = get_locker_row(pool, locker_id).await?;
                                let client_row = get_full_client_row(username.clone(), pool).await?;

                                client_data.shipping = Some(
                                    ShippingData {
                                        locker: Some(Locker::from_row(&locker_row)?),
                                        branch: None,
                                        delivery: false,
                                        shipping_type: ShippingGuideType::LockerLocker,
                                        client_from: client_data.info.clone(),
                                        client_to: Client::from_row(&client_row)?,
                                    }
                                );
                            }
                            app_lock.get_shortest_warehouse_path(pool).await?;

                            let client_data = app_lock.get_client_mut();

                            let selected_packages_weight =
                                    client_data.packages.as_ref().unwrap().selected_packages.as_ref().unwrap()
                                    .iter()
                                    .map(|package| package.weight)
                                    .sum::<Decimal>();

                            let amount_calc =
                                client_data.send_route_distance.unwrap() as f64 * PRICE_DIST_MULT +
                                f64::try_from(selected_packages_weight)? * PRICE_WEIGHT_MULT;

                            client_data.send_payment = Some(
                                PaymentData {
                                    amount:
                                        Decimal::from_f64(amount_calc)
                                        .expect("could not get payment amount from amount_calc")
                                        .round_dp_with_strategy(2, rust_decimal::RoundingStrategy::MidpointNearestEven),
                                    transaction_id: None,
                                    payment_type: None,
                                }
                            );

                            app_lock.enter_popup(Some(Popup::OnlinePayment), pool).await;
                        }
                        Some(User::PkgAdmin(_)) => {
                            {
                                let package = app_lock.get_pkgadmin_mut().add_package.as_mut().unwrap();

                                if sqlx::query("SELECT COUNT(*) AS package_count FROM shippings.packages WHERE locker_id=$1")
                                    .bind(package.locker.value().parse::<i32>().expect("could not parse locker value"))
                                    .fetch_one(pool)
                                    .await?
                                    .get::<i64, _>("package_count") >= LOCKER_PKG_NUM_MAX
                                {
                                    app_lock.get_pkgadmin_mut().get_db_err = Some(GetDBErr::LockerTooManyPackages);
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
                                    .unwrap_or(Decimal::new(0, 0)) +
                                    package_weight_decimal
                                    >
                                    Decimal::from_i64(LOCKER_WEIGHT_MAX).unwrap()
                                {
                                    app_lock.get_pkgadmin_mut().get_db_err = Some(GetDBErr::LockerWeightTooBig(Decimal::new(LOCKER_WEIGHT_MAX, 0) - package_weight_decimal));
                                    return Ok(())
                                }
                                
                                let locker_row = get_locker_row(pool, locker_id).await?;
                                let client_to_row = get_full_client_row(username, pool).await?;
                                let client_from_row = get_full_client_row(package.sender.value().to_string(), pool).await;

                                if let Ok(client_from_row) = client_from_row {
                                    package.shipping = Some(
                                        ShippingData {
                                            locker: Some(Locker::from_row(&locker_row)?),
                                            branch: None,
                                            delivery: false,
                                            shipping_type: ShippingGuideType::InpersonLocker,
                                            client_from: Client::from_row(&client_from_row)?,
                                            client_to: Client::from_row(&client_to_row)?,
                                        }
                                    );
                                } else {
                                    return Ok(());
                                }
                            }

                            app_lock.get_shortest_warehouse_path(pool).await?;

                            let package = app_lock.get_pkgadmin_mut().add_package.as_mut().unwrap();
                            package.payment = {
                                let amount_calc =
                                    package.route_distance.unwrap() as f64 * PRICE_DIST_MULT +
                                    package.weight.value().parse::<f64>().expect("could not parse weight as f64") * PRICE_WEIGHT_MULT;
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
                        } /* 
                        Some(User::Trucker(_)) => {
                            let order = app_lock.get_orders_mut().add_order.as_mut().unwrap();
                            //let package = app_lock.get_pkgadmin_mut().add_package.as_mut().unwrap();                            
                        } */
                        _ => {}
                    }
                    return Ok(());
                }
            }

            set_getdberr(app, GetDBErr::InvalidUserLocker);

            Ok(())
        }
        Event::TryGetUserBranch(username, branch_id) => {
            async fn get_branch_row(pool: &PgPool, branch_id: i32) -> Result<PgRow> {
                Ok(
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
                    .await?
                )
            }

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
                        Some(User::Client(_)) => {
                            {
                                let branch_row = get_branch_row(pool, branch_id).await?;
                                let client_row = get_full_client_row(username.clone(), pool).await?;

                                let client_data = app_lock.get_client_mut();
                                client_data.shipping = Some(
                                    ShippingData {
                                        locker: None,
                                        branch: Some(Branch::from_row(&branch_row)?),
                                        delivery: false,
                                        shipping_type: ShippingGuideType::LockerBranch,
                                        client_from: client_data.info.clone(),
                                        client_to: Client::from_row(&client_row)?,
                                    }
                                );
                            }
                            
                            app_lock.get_shortest_warehouse_path(pool).await?;
                            
                            let client_data = app_lock.get_client_mut();
                            let packages_weight =
                                client_data.packages.as_ref().unwrap().selected_packages.as_ref().unwrap()
                                .iter()
                                .map(|package| package.weight)
                                .sum::<Decimal>();

                            let amount_calc =
                                client_data.send_route_distance.unwrap() as f64 * PRICE_DIST_MULT +
                                f64::try_from(packages_weight)? * PRICE_WEIGHT_MULT;

                            client_data.send_payment = Some(
                                PaymentData {
                                    amount: Decimal::from_f64(amount_calc)
                                            .expect("could not get payment amount from amount_calc")
                                            .round_dp_with_strategy(2, rust_decimal::RoundingStrategy::MidpointNearestEven),
                                    transaction_id: None,
                                    payment_type: None,
                                }
                            );

                            app_lock.enter_popup(Some(Popup::OnlinePayment), pool).await;
                        }
                        Some(User::PkgAdmin(_)) => {
                            {
                                let branch_row = get_branch_row(pool, branch_id).await?;
                                let client_to_row = get_full_client_row(username, pool).await?;
                                
                                let package = app_lock.get_pkgadmin_mut().add_package.as_mut().unwrap();
                                let client_from_row = get_full_client_row(package.sender.value().to_string(), pool).await;

                                if let Ok(client_from_row) = client_from_row {
                                    package.shipping = Some(
                                        ShippingData {
                                            locker: None,
                                            branch: Some(Branch::from_row(&branch_row)?),
                                            delivery: false,
                                            shipping_type: ShippingGuideType::InpersonBranch,
                                            client_from: Client::from_row(&client_from_row)?,
                                            client_to: Client::from_row(&client_to_row)?,
                                        }
                                    )
                                } else {
                                    return Ok(());
                                }
                            }

                            app_lock.get_shortest_warehouse_path(pool).await?;

                            let package = app_lock.get_pkgadmin_mut().add_package.as_mut().unwrap();
                            package.payment = {
                                let amount_calc =
                                    package.route_distance.unwrap() as f64 * PRICE_DIST_MULT +
                                    package.weight.value().parse::<f64>().expect("could not parse weight as f64") * PRICE_WEIGHT_MULT;
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
                    let client_row = get_full_client_row(username.clone(), pool).await?;
                    let client_to = Client::from_row(&client_row)?;

                    match &mut app_lock.user {
                        Some(User::Client(client_data)) => {
                            client_data.shipping = Some(
                                ShippingData {
                                    locker: None,
                                    branch: Some(client_to.affiliated_branch.clone()),
                                    delivery: true,
                                    shipping_type: ShippingGuideType::LockerDelivery,
                                    client_from: client_data.info.clone(),
                                    client_to,
                                }
                            );
                            /*client_data.send_to_client = Some(
                                Client {
                                    username,
                                    affiliated_branch: Branch::from_row(&client_row)?,
                                    first_name: String::from(""),
                                    last_name: String::from(""),
                                }
                            );*/
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

pub async fn get_full_client_row(username: String, pool: &PgPool) -> Result<PgRow> {
    Ok(
        sqlx::query(
            "
            SELECT * FROM users.natural_clients AS clients
            INNER JOIN locations.branches AS branches ON clients.affiliated_branch=branches.branch_id
            INNER JOIN locations.buildings AS buildings ON branches.branch_id=buildings.building_id
            WHERE clients.username=$1
            "
        )
        .bind(username)
        .fetch_one(pool)
        .await?
    )
}
pub async fn get_full_trucker(username: String, pool: &PgPool) -> Result<PgRow> {
    Ok(
        sqlx::query(
            "
            SELECT * FROM Vehicles.Truckers AS truckers
            INNER JOIN Locations.Warehouses AS warehouse ON truckers.affiliated_warehouse=warehouse.warehouse_id
            WHERE truckers.username=$1            
            "
        )
        .bind(username)
        .fetch_one(pool)
        .await?
    )
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
            Some(User::Trucker(trucker_data)) => {
                &mut trucker_data.get_db_err
            }
            _ => unimplemented!("update::db::tryget::set_getdberr for user {:?}", app_lock.user)
        };
    
    *get_db_err = Some(err);
}