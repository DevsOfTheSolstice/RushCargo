use std::sync::{Arc, Mutex};
use rust_decimal::Decimal;
use crossterm::event::{Event as CrosstermEvent, KeyCode};
use tui_input::backend::crossterm::EventHandler;
use sqlx::{pool, FromRow, PgPool, Row};
use anyhow::{Result, anyhow};
use time::{Date, OffsetDateTime, Time};
use crate::{
    event::{Event, InputBlacklist},
    model::{
        app::App, client::Client, common::{UserType, Bank, PaymentType, Popup, Screen, SubScreen, User}, db_obj::{Branch, BranchTransferOrderSmall, Locker, ShippingGuideType, Warehouse}, graph_reqs::WarehouseNode, pkgadmin
    },
};

pub async fn update(app: &mut Arc<Mutex<App>>, pool: &PgPool, event: Event) -> Result<()> {
    match event {
        Event::PlaceOrderReq => {
            place_order_req(app, pool, &event).await?;
            Ok(())
        }
        Event::PlaceOrder => {
            async fn insert_order(order_number: i64, prev_order_number: Option<i64>, datetime: &OffsetDateTime, pool: &PgPool) -> Result<()> {
                sqlx::query(
                    "
                        INSERT INTO orders.orders
                        (order_number, previous_order, generated_date, generated_hour)
                        VALUES ($1, $2, $3, $4)
                    "
                )
                .bind(order_number)
                .bind(prev_order_number)
                .bind(datetime.date())
                .bind(datetime.time())
                .execute(pool)
                .await?;

                Ok(())
            }

            async fn insert_auto_order(order_number: i64, username: &String, pool: &PgPool) -> Result<()> {
                sqlx::query(
                    "
                        INSERT INTO orders.automatic_orders
                        (order_number, admin_verification)
                        VALUES ($1, $2)
                    "
                )
                .bind(order_number)
                .bind(username)
                .execute(pool)
                .await?;

                Ok(())
            }

            async fn insert_branch_transfer_order(order: BranchTransferOrderSmall, pool: &PgPool) -> Result<()> {
                sqlx::query(
                    "
                        INSERT INTO orders.branch_transfer_order
                        (order_number, trucker, shipping_number, warehouse, branch, withdrawal, rejected)
                        VALUES ($1, $2, $3, $4, $5, $6, false)
                    "
                )
                .bind(order.order_number)
                .bind(order.trucker)
                .bind(order.shipping_number)
                .bind(order.warehouse.get_id())
                .bind(order.branch)
                .bind(order.withdrawal)
                .execute(pool)
                .await?;

                Ok(())
            }

            async fn get_free_trucker(warehouse_id: i32, blacklist_trucker: Option<String>, pool: &PgPool) -> Result<String> {
                Ok(
                    sqlx::query(
                        "
                            SELECT username
                            FROM (
                                SELECT  t.username,
                                        SUM(CASE WHEN ao.completed_date IS NULL OR wo.rejected OR bo.rejected THEN 0 ELSE 1 END) AS total_orders
                                FROM vehicles.truckers AS t
                                LEFT JOIN orders.warehouse_transfer_orders AS wo ON t.username=wo.trucker
                                LEFT JOIN orders.branch_transfer_order AS bo ON t.username=bo.trucker
                                LEFT JOIN orders.automatic_orders AS ao ON wo.order_number=ao.order_number OR bo.order_number=ao.order_number
                                WHERE t.affiliated_warehouse=$1 AND t.truck IS NOT NULL AND t.username!=$2
                                GROUP BY t.username
                            ) AS total_combined_orders
                            ORDER BY total_orders ASC
                            LIMIT 1
                        "
                    )
                    .bind(warehouse_id)
                    .bind(blacklist_trucker.unwrap_or(String::from("kaucrow")))
                    .fetch_one(pool)
                    .await?
                    .try_get::<String, _>("username")?
                )
            }

            async fn insert_route_orders(
                next_order_number: &mut i64, prev_order_number: &mut Option<i64>, shipping_number: i64, app: &Arc<Mutex<App>>, pool: &PgPool
            ) -> Result<()> {
                let app_lock = app.lock().unwrap();

                let (verification, route) =
                    match &app_lock.user {
                        Some(User::PkgAdmin(pkgadmin_data)) => {
                            (
                                &pkgadmin_data.info.username,
                                pkgadmin_data.add_package.as_ref().unwrap().route.as_ref().unwrap()
                            )
                        }
                        _ => unimplemented!()
                    };

                let datetime = OffsetDateTime::now_utc();
 
                for i in 0..route.len() - 1{
                    let warehouse_from = &route[i];
                    let warehouse_to = &route[i + 1];

                    let trucker = get_free_trucker(warehouse_from.id, None, pool).await?;

                    insert_order(*next_order_number, *prev_order_number, &datetime, pool).await?;

                    insert_auto_order(*next_order_number, verification, pool).await?;

                    sqlx::query(
                        "
                            INSERT INTO orders.warehouse_transfer_orders
                            (order_number, trucker, warehouse_from, warehouse_to, shipping_number, rejected)
                            VALUES ($1, $2, $3, $4, $5, false)
                        "
                    )
                    .bind(*next_order_number)
                    .bind(trucker)
                    .bind(warehouse_from.id)
                    .bind(warehouse_to.id)
                    .bind(shipping_number)
                    .execute(pool)
                    .await?;

                    *prev_order_number = Some(*next_order_number);
                    *next_order_number += 1;
                }
                Ok(())
            }

            async fn insert_transfer_orders_base(
                datetime: &OffsetDateTime, next_order_number: &mut i64, prev_order_number: &mut Option<i64>,
                app: &Arc<Mutex<App>>, pool: &PgPool
            ) -> Result<()> {
                let username =
                    match &app.lock().unwrap().user {
                        Some(User::Client(client_data)) => client_data.info.username.clone(),
                        Some(User::PkgAdmin(pkgadmin_data)) => pkgadmin_data.info.username.clone(),
                        _ => unimplemented!()
                    };

                insert_order(*next_order_number, *prev_order_number, &datetime, pool).await?;
                insert_auto_order(*next_order_number, &username, pool).await?;

                Ok(())
            }

            async fn insert_branch_transfer_first(
                datetime: &OffsetDateTime, next_order_number: &mut i64, prev_order_number: &mut Option<i64>,
                shipping_number: i64, app: &Arc<Mutex<App>>, pool: &PgPool
            ) -> Result<()> {
                insert_transfer_orders_base(datetime, next_order_number, prev_order_number, app, pool).await?;

                let app_lock = app.lock().unwrap();
                
                let branch =
                    match &app_lock.user {
                        Some(User::PkgAdmin(pkgadmin_data)) => &pkgadmin_data.info.branch,
                        _ => unimplemented!()
                    };
                
                let warehouse = &branch.warehouse;

                let trucker =
                    get_free_trucker(warehouse.get_id(), None, pool).await?;
                
                let order = BranchTransferOrderSmall {
                        order_number: *next_order_number,
                        trucker,
                        shipping_number,
                        warehouse: warehouse.clone(),
                        branch: branch.get_id(),
                        withdrawal: false,
                        rejected: false,
                    };

                insert_branch_transfer_order(order, pool).await?;

                *prev_order_number = Some(*next_order_number);
                *next_order_number += 1;

                Ok(()) 
            }

            async fn insert_branch_transfer_last(
                datetime: &OffsetDateTime, next_order_number: &mut i64, prev_order_number: &mut Option<i64>,
                shipping_number: i64, app: &Arc<Mutex<App>>, pool: &PgPool
            ) -> Result<()> {
                insert_transfer_orders_base(datetime, next_order_number, prev_order_number, app, pool).await?;

                let app_lock = app.lock().unwrap();

                let (shipping, last_warehouse) =
                    match &app_lock.user {
                        Some(User::PkgAdmin(pkgadmin_data)) => {
                            let add_package = pkgadmin_data.add_package.as_ref().unwrap();
                            (
                                add_package.shipping.as_ref().unwrap(),
                                add_package.route.as_ref().unwrap().last().unwrap()
                            )
                        }
                        _ => unimplemented!()
                    };
                
                let trucker =
                    get_free_trucker(last_warehouse.id, None, pool)
                    .await?;
                
                let order = BranchTransferOrderSmall {
                    order_number: *next_order_number,
                    trucker,
                    shipping_number,
                    warehouse: Warehouse::from_id(last_warehouse.id),
                    branch: shipping.branch.as_ref().unwrap().get_id(),
                    withdrawal: true,
                    rejected: false
                };

                insert_branch_transfer_order(order, pool).await?;

                *prev_order_number = Some(*next_order_number);
                *next_order_number += 1;

                Ok(())
            }

            let active_screen = app.lock().unwrap().active_screen.clone();

            let shipping_number = {
                match active_screen {
                    Screen::PkgAdmin(SubScreen::PkgAdminAddPackage(_)) => {
                        let next_shipping_num = get_next_shipping_number(pool).await?;
                        insert_shipping_guide(next_shipping_num, true, app, pool).await?;

                        let next_payment_id = get_next_payment_id(pool).await?;
                        insert_payment(next_payment_id, app, pool).await?;

                        insert_guide_payment(next_payment_id, next_shipping_num, pool).await?;

                        let app_lock = app.lock().unwrap();
                        let pkgadmin_data = app_lock.get_pkgadmin_ref();
                        let add_package = app_lock.get_pkgadmin_ref().add_package.as_ref().unwrap();

                        let next_tracking_number = get_next_tracking_number(pool).await?;

                        sqlx::query(
                            "
                                INSERT INTO shippings.package_descriptions
                                (tracking_number, content, package_value, package_weight, package_lenght, package_width, package_height)
                                VALUES ($1, $2, $3, $4, $5, $6, $7)
                            "
                        )
                        .bind(next_tracking_number)
                        .bind(add_package.content.value())
                        .bind(Decimal::from_str_exact(add_package.value.value())?)
                        .bind(Decimal::from_str_exact(add_package.weight.value())?)
                        .bind(Decimal::from_str_exact(add_package.length.value())?)
                        .bind(Decimal::from_str_exact(add_package.width.value())?)
                        .bind(Decimal::from_str_exact(add_package.height.value())?)
                        .execute(pool).await?;

                        let datetime = OffsetDateTime::now_utc();

                        sqlx::query(
                            "
                                INSERT INTO shippings.packages
                                (tracking_number, admin_verification, shipping_number, register_date, register_hour, delivered)
                                VALUES ($1, $2, $3, $4, $5, false)
                            "
                        )
                        .bind(next_tracking_number)
                        .bind(pkgadmin_data.info.username.clone())
                        .bind(next_shipping_num)
                        .bind(datetime.date())
                        .bind(datetime.time())
                        .execute(pool)
                        .await?;

                        next_shipping_num
                    }
                    _ => unimplemented!()
                }
            };

            let shipping_type = {
                let app_lock = app.lock().unwrap();
                let package = app_lock.get_pkgadmin_ref().add_package.as_ref().unwrap();
                package.shipping.as_ref().unwrap().shipping_type.clone()
            };

            let mut next_order_number = get_next_order_number(pool).await?;
            let mut prev_order_number = None;
            let datetime = OffsetDateTime::now_utc();

            if matches!(
                shipping_type,
                ShippingGuideType::InpersonBranch | ShippingGuideType::InpersonDelivery | ShippingGuideType::InpersonLocker
            ) 
            {
                insert_branch_transfer_first(
                    &datetime, &mut next_order_number, &mut prev_order_number, shipping_number, app, pool
                ).await?;
            }

            insert_route_orders(
                &mut next_order_number, &mut prev_order_number, shipping_number, app, pool
            ).await?;

            if matches!(
                shipping_type,
                ShippingGuideType::InpersonBranch | ShippingGuideType::InpersonDelivery |
                ShippingGuideType::LockerBranch | ShippingGuideType::LockerDelivery
            ) 
            {
                insert_branch_transfer_last(
                    &datetime, &mut next_order_number, &mut prev_order_number, shipping_number, app, pool
                ).await?;
            }

            app.lock().unwrap().enter_popup(Some(Popup::OrderSuccessful), pool).await;

            Ok(())
        }
        _ => panic!("An event of type {:?} was passed to the db::insert update function", event)
    }
}

async fn place_order_req(app: &mut Arc<Mutex<App>>, pool: &PgPool, event: &Event) -> Result<()> {
    let user_type =
    match &app.lock().unwrap().user {
        Some(User::Client(_)) => UserType::Client,
        _ => unimplemented!()
    };

    match user_type {
        UserType::Client => {
            let next_shipping_num = get_next_shipping_number(pool).await?;

            insert_shipping_guide(next_shipping_num, false, app, pool).await?;
            
            let next_payment_id = get_next_payment_id(pool).await?;

            insert_payment(next_payment_id, app, pool).await?;

            insert_guide_payment(next_payment_id, next_shipping_num, pool).await?;
            
            let mut app_lock = app.lock().unwrap();

            let package_data = app_lock.get_packages_mut();
            let selected_packages = package_data.selected_packages.as_ref().unwrap();

            for package in selected_packages.iter() {
                sqlx::query("UPDATE shippings.packages SET locker_id=NULL, holder=NULL, delivered=false, shipping_number=$1 WHERE tracking_number=$2")
                    .bind(next_shipping_num)
                    .bind(package.get_id())
                    .execute(pool)
                    .await?;
                package_data.viewing_packages.remove(
                    package_data.viewing_packages.iter().position(|x| x == package).unwrap()
                );
            }

            package_data.selected_packages = None;

            app_lock.enter_popup(Some(Popup::OrderSuccessful), pool).await;
        }
        _ => unimplemented!("db::insert::place_order for user {:?}", app.lock().unwrap().user)
    }
    Ok(())
}

async fn insert_shipping_guide(shipping_num: i64, set_date: bool, app: &Arc<Mutex<App>>, pool: &PgPool) -> Result<()> {
    let app_lock = app.lock().unwrap();

    let (client_from, client_to, locker_from, locker_to, branch_from, branch_to, delivery_included) =
    match &app_lock.user {
        Some(User::Client(client_data)) => {
            let shipping = client_data.shipping.as_ref().unwrap();
            (
                shipping.client_from.username.clone(),
                shipping.client_to.username.clone(),
                Some(client_data.active_locker.as_ref().unwrap().get_id()),
                if let Some(locker) = &shipping.locker {
                    Some(locker.get_id())
                } else {
                    None
                },
                None,
                if let Some(branch) = &shipping.branch {
                    Some(branch.get_id())
                } else {
                    None
                },
                shipping.delivery
            )
        }
        Some(User::PkgAdmin(pkgadmin_data)) => {
            match app_lock.active_screen {
                Screen::PkgAdmin(SubScreen::PkgAdminAddPackage(_)) => {
                    let shipping = pkgadmin_data.add_package.as_ref().unwrap().shipping.as_ref().unwrap();
                    (
                        shipping.client_from.username.clone(),
                        shipping.client_to.username.clone(),
                        None,
                        if let Some(locker) = &shipping.locker {
                            Some(locker.get_id())
                        } else {
                            None
                        },
                        Some(pkgadmin_data.info.branch.get_id()),
                        if let Some(branch) = &shipping.branch {
                            Some(branch.get_id())
                        } else {
                            None
                        },
                        shipping.delivery
                    )
                }
                _ => unimplemented!()
            }
        }
        _ => unimplemented!()
    };

    let (shipping_date, shipping_hour) =
        if set_date {
            let datetime = OffsetDateTime::now_utc();
            (
                Some(datetime.date()),
                Some(datetime.time()),
            )
        } else {
            (None, None)
        };

    sqlx::query(
        "
            INSERT INTO shippings.shipping_guides
            (
                shipping_number, client_from, client_to,
                locker_from, locker_to, branch_from, branch_to,
                delivery_included, shipping_date, shipping_hour, shipping_type
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, 'Ground')
        "
    )
    .bind(shipping_num)
    .bind(client_from)
    .bind(client_to)
    .bind(locker_from)
    .bind(locker_to)
    .bind(branch_from)
    .bind(branch_to)
    .bind(delivery_included)
    .bind(shipping_date)
    .bind(shipping_hour)
    .execute(pool)
    .await?;

    Ok(())
}

async fn insert_payment(payment_id: i64, app: &Arc<Mutex<App>>, pool: &PgPool) -> Result<()> {
    let app_lock = app.lock().unwrap();

    let (client, transaction_id, pay_type, amount) =
    match &app_lock.user {
        Some(User::Client(client_data)) => {
            let payment = client_data.send_payment.as_ref().unwrap();
            (
                client_data.info.username.clone(),
                payment.transaction_id.as_ref().unwrap().clone(),
                payment.payment_type.as_ref().unwrap(),
                payment.amount
            )
        }
        Some(User::PkgAdmin(pkgadmin_data)) => {
            match app_lock.active_screen {
                Screen::PkgAdmin(SubScreen::PkgAdminAddPackage(_)) => {
                    let package = pkgadmin_data.add_package.as_ref().unwrap();
                    let shipping = package.shipping.as_ref().unwrap();
                    let payment = package.payment.as_ref().unwrap();
                    (
                        shipping.client_from.username.clone(),
                        payment.transaction_id.as_ref().unwrap().clone(),
                        payment.payment_type.as_ref().unwrap(),
                        payment.amount,
                    )
                }
                _ => unimplemented!()
            }
        }
        _ => unimplemented!()
    };

    let datetime = OffsetDateTime::now_utc();

    sqlx::query(
        "
            INSERT INTO payments.payments
            (id, client, reference, pay_type, pay_date, pay_hour, amount)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        "
    )
    .bind(payment_id)
    .bind(client)
    .bind(transaction_id)
    .bind(pay_type.to_string())
    .bind(datetime.date())
    .bind(datetime.time())
    .bind(amount)
    .execute(pool)
    .await?;
    Ok(())
}

async fn insert_guide_payment(payment_id: i64, shipping_num: i64, pool: &PgPool) -> Result<()> {
    sqlx::query(
        "
            INSERT INTO payments.guide_payments
            (pay_id, shipping_number)
            VALUES ($1, $2)
        "
    )
    .bind(payment_id)
    .bind(shipping_num)
    .execute(pool)
    .await?;
    Ok(())
}

const NEXT_SHIPPING_NUMBER: &'static str = "SELECT MAX(shipping_number) FROM shippings.shipping_guides";
const NEXT_PAYMENT_ID: &'static str = "SELECT MAX(id) FROM payments.payments";
const NEXT_TRACKING_NUMBER: &'static str = "SELECT MAX(tracking_number) FROM shippings.package_descriptions";
const NEXT_ORDER_NUMBER: &'static str = "SELECT MAX(order_number) FROM orders.orders";

async fn get_next_id(query: &'static str, pool: &PgPool) -> Result<i64> {
    Ok(
        sqlx::query(query)
        .fetch_one(pool)
        .await?
        .try_get::<i64,_ >("max").unwrap_or(-1) + 1
    )
}

async fn get_next_shipping_number(pool: &PgPool) -> Result<i64> {
    Ok(get_next_id(NEXT_SHIPPING_NUMBER, pool).await?)
}

async fn get_next_payment_id(pool: &PgPool) -> Result<i64> {
    Ok(get_next_id(NEXT_PAYMENT_ID, pool).await?)
}

async fn get_next_tracking_number(pool: &PgPool) -> Result<i64> {
    Ok(get_next_id(NEXT_TRACKING_NUMBER, pool).await?)
}

async fn get_next_order_number(pool: &PgPool) -> Result<i64> {
    Ok(get_next_id(NEXT_ORDER_NUMBER, pool).await?)
}