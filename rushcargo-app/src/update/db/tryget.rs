use std::sync::{Arc, Mutex};
use rust_decimal::Decimal;
use crossterm::event::{Event as CrosstermEvent, KeyCode};
use tui_input::backend::crossterm::EventHandler;
use sqlx::{Row, FromRow, PgPool};
use anyhow::{Result, anyhow};
use time::{Date, OffsetDateTime, Time};
use crate::{
    event::{Event, InputBlacklist},
    model::{
        app::App,
        client::{self, Client, GetDBErr},
        common::{Bank, InputMode, PaymentData, Popup, Screen, SubScreen, TimeoutType, User},
        db_obj::{Branch, Locker},
    },
};

pub async fn update(app: &mut Arc<Mutex<App>>, pool: &PgPool, event: Event) -> Result<()> {
    match event {
        Event::TryGetUserLocker(username, locker_id) => {
            if username.is_empty() || locker_id.is_empty() { return Ok(()); }

            let locker_id = locker_id.parse::<i64>().expect("could not parse locker_id in TryGetUserLocker event");

            if let Some(res) =
                sqlx::query("SELECT * FROM locker WHERE locker_id=$1")
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

                            if sqlx::query("SELECT COUNT(*) AS package_count FROM package WHERE locker_id=$1")
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
                                    SELECT SUM(package_weight) as weight_sum FROM package
                                    INNER JOIN package_description AS description
                                    ON package.tracking_number=description.tracking_number
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
                            }

                            let locker_row =
                                sqlx::query(
                                "
                                    SELECT locker.*, country.*, warehouse.*,
                                    COUNT(package.tracking_number) AS package_count FROM locker
                                    LEFT JOIN package ON locker.locker_id=package.locker_id
                                    INNER JOIN country ON locker.country_id=country.country_id
                                    INNER JOIN warehouse ON locker.warehouse_id=warehouse.warehouse_id
                                    WHERE locker.locker_id=$1
                                    GROUP BY locker.locker_id, country.country_id, warehouse.warehouse_id
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
                        
                            app_lock.enter_popup(Some(Popup::ClientInputPayment), pool).await;
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

            let branch_id = branch_id.parse::<i64>().expect("could not parse locker_id in TryGetUserLocker event");

            if let Some(res) =
                sqlx::query("SELECT * FROM natural_client WHERE username=$1")
                    .bind(&username)
                    .fetch_optional(pool)
                    .await?
            {
                if branch_id == res.get::<i64, _>("affiliated_branch") {
                    let mut app_lock = app.lock().unwrap();
                    match &mut app_lock.user {
                        Some(User::Client(client_data)) => {
                            let branch_res =
                                sqlx::query(
                                    "
                                        SELECT * FROM branch
                                        INNER JOIN warehouse ON branch.warehouse_connection=warehouse.warehouse_id
                                        INNER JOIN building ON branch.branch_id=building.building_id
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
                            
                            app_lock.enter_popup(Some(Popup::ClientInputPayment), pool).await;
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
                        SELECT * FROM natural_client
                        INNER JOIN motorcyclist ON natural_client.affiliated_branch=motorcyclist.assigned_branch
                        INNER JOIN vehicle ON motorcyclist.motorcycle=vehicle.vin_vehicle
                        WHERE natural_client.username=$1
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
                            app_lock.enter_popup(Some(Popup::ClientInputPayment), pool).await;
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

    match &mut app_lock.user {
        Some(User::Client(client_data)) => {
            client_data.get_db_err = Some(err);
        }
        _ => unimplemented!("update::db::tryget::set_getdberr for user {:?}", app_lock.user)
    }
}