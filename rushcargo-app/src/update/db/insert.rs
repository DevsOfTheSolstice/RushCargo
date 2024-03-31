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
        common::{GetDBErr, Bank, InputMode, PaymentData, Popup, Screen, SubScreen, User},
        db_obj::{Branch, Locker},
    },
};

pub async fn update(app: &mut Arc<Mutex<App>>, pool: &PgPool, event: Event) -> Result<()> {
    match event {
        Event::PlaceOrderLockerLocker | Event::PlaceOrderLockerBranch | Event::PlaceOrderLockerDelivery
        => {
            place_order(app, pool, &event).await?;
            Ok(())
        }
        _ => panic!("An event of type {:?} was passed to the db::insert update function", event)
    }
}

async fn place_order(app: &mut Arc<Mutex<App>>, pool: &PgPool, event: &Event) -> Result<()> {
    let mut app_lock = app.lock().unwrap();

    if let Some(bank) = app_lock.list.state.0.selected() {
        let bank = match bank {
            0 => Bank::PayPal,
            1 => Bank::AmazonPay,
            2 => Bank::BOFA,
            _ => panic!("bank is not in db::insert::place_order")
        };

        let payment_data =
            PaymentData {
                amount: Decimal::new(99, 0),
                transaction_id: app_lock.input.0.to_string(),
                bank,
            };
        
        let next_shipping_id =
            sqlx::query("SELECT MAX(shipping_number) FROM shipping_guides")
                .fetch_one(pool)
                .await?
                .try_get::<i64,_ >("max").unwrap_or(-1) + 1;

        let next_payment_id =
            sqlx::query("SELECT MAX(id) FROM payments")
                .fetch_one(pool)
                .await?
                .try_get::<i64, _>("max").unwrap_or(-1) + 1;

        match &app_lock.user {
            Some(User::Client(client_data)) => {
                let (locker_receiver, branch_receiver) =
                    match event {
                        Event::PlaceOrderLockerLocker => (Some(client_data.send_to_locker.as_ref().unwrap().get_id()), None),
                        Event::PlaceOrderLockerBranch => (None, Some(client_data.send_to_branch.as_ref().unwrap().get_id())),
                        Event::PlaceOrderLockerDelivery => (None, None),
                        _ => panic!()
                    };

                sqlx::query(
                    "
                        INSERT INTO shipping_guides
                        (shipping_number, client_from, client_to, locker_from, locker_to, branch_to, delivery_included)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                    "
                )
                .bind(next_shipping_id)
                .bind(client_data.info.username.clone())
                .bind(client_data.send_to_client.as_ref().unwrap().username.clone())
                .bind(client_data.active_locker.as_ref().unwrap().get_id())
                .bind(locker_receiver)
                .bind(branch_receiver)
                .bind(client_data.send_with_delivery)
                .execute(pool)
                .await?;

                let datetime = OffsetDateTime::now_utc();

                sqlx::query(
                    "
                        INSERT INTO payments
                        (id, client, reference, platform, pay_type, pay_date, pay_hour, amount)
                        VALUES ($1, $2, $3, $4, 'Online payment', $5, $6, $7)
                    "
                )
                .bind(next_payment_id)
                .bind(client_data.info.username.clone())
                .bind(payment_data.transaction_id)
                .bind(payment_data.bank.to_string())
                .bind(datetime.date())
                .bind(datetime.time())
                .bind(payment_data.amount)
                .execute(pool)
                .await?;

                sqlx::query(
                    "
                        INSERT INTO guide_payments
                        (pay_id, shipping_number)
                        VALUES ($1, $2)
                    "
                )
                .bind(next_payment_id)
                .bind(next_shipping_id)
                .execute(pool)
                .await?;

                let package_data = app_lock.get_client_packages_mut();
                let selected_packages = package_data.selected_packages.as_ref().unwrap();

                for package in selected_packages.iter() {
                    sqlx::query("UPDATE packages SET locker_id=NULL, holder=NULL, delivered=false, shipping_number=$1 WHERE tracking_number=$2")
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