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
        client::Client,
        common::{Bank, GetDBErr, InputMode, PaymentData, PaymentType, Popup, Screen, SubScreen, User},
        db_obj::{Branch, Locker, ShippingGuideType},
    },
};

pub async fn update(app: &mut Arc<Mutex<App>>, pool: &PgPool, event: Event) -> Result<()> {
    match event {
        Event::PlaceOrderReq
        => {
            place_order(app, pool, &event).await?;
            Ok(())
        }
        _ => panic!("An event of type {:?} was passed to the db::insert update function", event)
    }
}

async fn place_order(app: &mut Arc<Mutex<App>>, pool: &PgPool, event: &Event) -> Result<()> {
    let selection = app.lock().unwrap().list.state.0.selected(); 
    if let Some(bank) = selection {
        let bank = match bank {
            0 => Bank::PayPal,
            1 => Bank::AmazonPay,
            2 => Bank::BOFA,
            _ => panic!("bank is not in db::insert::place_order")
        };

        let mut app_lock = app.lock().unwrap();

        let transaction_id = Some(app_lock.input.0.to_string());

        let payment_type = {
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

        let payment_amount = {
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

        let next_shipping_id =
            sqlx::query("SELECT MAX(shipping_number) FROM shippings.shipping_guides")
                .fetch_one(pool)
                .await?
                .try_get::<i64,_ >("max").unwrap_or(-1) + 1;

        let next_payment_id =
            sqlx::query("SELECT MAX(id) FROM payments.payments")
                .fetch_one(pool)
                .await?
                .try_get::<i64, _>("max").unwrap_or(-1) + 1;

        match &app_lock.user {
            Some(User::Client(client_data)) => {
                let shipping_data = client_data.shipping.as_ref().unwrap();
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
                
                sqlx::query(
                    "
                        INSERT INTO shippings.shipping_guides
                        (shipping_number, client_from, client_to, locker_from, locker_to, branch_to, delivery_included)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                    "
                )
                .bind(next_shipping_id)
                .bind(shipping_data.client_from.username.clone())
                .bind(shipping_data.client_to.username.clone())
                .bind(locker_from)
                .bind(locker_to)
                .bind(branch_to)
                .bind(delivery_included)
                .execute(pool)
                .await?;

                let datetime = OffsetDateTime::now_utc();

                sqlx::query(
                    "
                        INSERT INTO payments.payments
                        (id, client, reference, platform, pay_type, pay_date, pay_hour, amount)
                        VALUES ($1, $2, $3, $4, 'Online', $5, $6, $7)
                    "
                )
                .bind(next_payment_id)
                .bind(client_data.info.username.clone())
                .bind(transaction_id)
                .bind(bank.to_string())
                .bind(datetime.date())
                .bind(datetime.time())
                .bind(payment_amount)
                .execute(pool)
                .await?;

                sqlx::query(
                    "
                        INSERT INTO payments.guide_payments
                        (pay_id, shipping_number)
                        VALUES ($1, $2)
                    "
                )
                .bind(next_payment_id)
                .bind(next_shipping_id)
                .execute(pool)
                .await?;

                let package_data = app_lock.get_packages_mut();
                let selected_packages = package_data.selected_packages.as_ref().unwrap();

                for package in selected_packages.iter() {
                    sqlx::query("UPDATE shippings.packages SET locker_id=NULL, holder=NULL, delivered=false, shipping_number=$1 WHERE tracking_number=$2")
                        .bind(next_shipping_id)
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
            _ => unimplemented!("db::insert::place_order for user {:?}", app_lock.user)
        }
    }
    Ok(())
}