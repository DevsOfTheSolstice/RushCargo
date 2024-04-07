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
        app::App,
        client::Client,
        common::{Bank, PaymentType, Popup, Screen, SubScreen, User},
        db_obj::{Branch, BranchTransferOrderSmall, Locker, ShippingGuideType}, pkgadmin,
    },
};

pub async fn update(app: &mut Arc<Mutex<App>>, pool: &PgPool, event: Event) -> Result<()> {
    match event {
        Event::PlaceOrderReq => {
            place_order_req(app, pool, &event).await?;
            Ok(())
        }
        Event::PlaceOrder => {
            let active_screen = app.lock().unwrap().active_screen.clone();

            match active_screen {
                Screen::PkgAdmin(SubScreen::PkgAdminAddPackage(_)) => {
                    let next_shipping_num = get_next_shipping_number(pool).await?;
                    insert_shipping_guide(next_shipping_num, app, pool).await?;

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
                }
                _ => unimplemented!()
            }

            let app_lock = app.lock().unwrap();
            let package = app_lock.get_pkgadmin_ref().add_package.as_ref().unwrap();
            let shipping = package.shipping.as_ref().unwrap();
            let route = package.route.as_ref().unwrap();

            async fn insert_order(order_number: i64, datetime: &OffsetDateTime, pool: &PgPool) -> Result<()> {
                sqlx::query(
                    "
                        INSERT INTO orders.orders
                        (order_number, generated_date, generated_hour)
                        VALUES ($1, $2, $3)
                    "
                )
                .bind(order_number)
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

            async fn get_free_trucker(warehouse_id: i32, pool: &PgPool) -> Result<String> {
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
                            WHERE t.affiliated_warehouse=4 AND t.truck IS NOT NULL AND t.username!='kaucrow'
                            GROUP BY t.username
                        ) AS total_combined_orders
                        ORDER BY total_orders DESC
                        LIMIT 1
                    "
                )
                Ok(String::from("joemama"))
            }

            let next_order_number =
            match shipping.shipping_type {
                ShippingGuideType::InpersonBranch => {
                    let next_order_number = get_next_order_number(pool).await?;
                    let datetime = OffsetDateTime::now_utc();

                    insert_order(next_order_number, &datetime, pool).await?;

                    insert_auto_order(next_order_number, &app_lock.get_pkgadmin_ref().info.username, pool).await?;

                    let trucker = sqlx::query("")
                    let order = BranchTransferOrderSmall {
                        order_number: next_order_number,

                    }
                    
                    next_order_number + 1
                }
                _ => todo!()
            };

            app.lock().unwrap().enter_popup(Some(Popup::OrderSuccessful), pool).await;

            Ok(())
        }
        _ => panic!("An event of type {:?} was passed to the db::insert update function", event)
    }
}

async fn place_order_req(app: &mut Arc<Mutex<App>>, pool: &PgPool, event: &Event) -> Result<()> {
    let selection = app.lock().unwrap().list.state.0.selected(); 
    if let Some(bank) = selection {
        let bank = match bank {
            0 => Bank::PayPal,
            1 => Bank::AmazonPay,
            2 => Bank::BOFA,
            _ => panic!("bank is not in db::insert::place_order")
        };

        //let mut app_lock = app.lock().unwrap();

        let transaction_id = Some(app.lock().unwrap().input.0.to_string());

        let payment_type = {
            let app_lock = app.lock().unwrap();
            Some(
                match app_lock.user {
                Some(User::Client(_)) =>
                    PaymentType::Online(bank.clone()),
                Some(User::PkgAdmin(_)) =>
                    match app_lock.active_popup {
                        Some(Popup::OnlinePayment) => PaymentType::Online(bank.clone()),
                        Some(Popup::CardPayment) => PaymentType::Card,
                        Some(Popup::CashPayment) => PaymentType::Cash,
                        _ => panic!()
                    }
                _ => unimplemented!()
                }
            )
        };

        {
            let mut app_lock = app.lock().unwrap();
            let payment = {
                match &app_lock.user {
                    Some(User::Client(_)) =>
                        app_lock.get_client_mut().send_payment.as_mut().unwrap(),
                    Some(User::PkgAdmin(_)) =>
                        app_lock.get_pkgadmin_mut().add_package.as_mut().unwrap().payment.as_mut().unwrap(),
                    _ => unimplemented!()
                }
            };

            payment.transaction_id = transaction_id.clone();
            payment.payment_type = payment_type;

            payment.amount
        };

        match &app.lock().unwrap().user {
            Some(User::Client(_)) => {
                /*let shipping_data = client_data.shipping.as_ref().unwrap();
                let (locker_from, locker_to, branch_to, delivery_included) =
                    (
                        client_data.active_locker.as_ref().unwrap().get_id(),
                        if let Some(locker) = &shipping_data.locker {
                            Some(locker.get_id())
                        } else {
                            None
                        },
                        if let Some(branch) = &shipping_data.branch {
                            Some(branch.get_id())
                        } else {
                            None
                        },
                        shipping_data.delivery,
                    );
                */
                let next_shipping_num = get_next_shipping_number(pool).await?;

                insert_shipping_guide(next_shipping_num, app, pool).await?;
                
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
    }
    Ok(())
}

async fn insert_shipping_guide(shipping_num: i64, app: &Arc<Mutex<App>>, pool: &PgPool) -> Result<()> {
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

    sqlx::query(
        "
            INSERT INTO shippings.shipping_guides
            (shipping_number, client_from, client_to, locker_from, locker_to, branch_from, branch_to, delivery_included)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
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