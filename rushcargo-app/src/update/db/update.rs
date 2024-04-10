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
        app::App, client::Client, common::{Bank, PaymentType, Popup, Screen, SubScreen, User}, db_obj::{Branch, BranchTransferOrderSmall, Locker, ShippingGuideType, Warehouse}, graph_reqs::WarehouseNode, pkgadmin::{self, PkgAdmin}
    },
};

pub async fn update(app: &mut Arc<Mutex<App>>, pool: &PgPool, event: Event) -> Result<()> {
    match event {
        Event::RejectOrderReq => {
            let mut app_lock = app.lock().unwrap();

            let viewing_guides_len =
            if let Some(User::PkgAdmin(pkgadmin_data)) = &mut app_lock.user {
                let guide = pkgadmin_data.shipping_guides.as_mut().unwrap().active_guide.as_ref().unwrap();

                sqlx::query(
                    "
                        DELETE FROM payments.guide_payments WHERE shipping_number=$1
                    "
                )
                .bind(guide.get_id())
                .execute(pool)
                .await?;

                sqlx::query(
                    "
                        UPDATE shippings.packages
                        SET delivered=true, shipping_number=NULL, holder=$1,
                            locker_id=$2
                        WHERE shipping_number=$3
                    "
                )
                .bind(guide.sender.username.clone())
                .bind(guide.locker_sender.as_ref().unwrap())
                .bind(guide.get_id())
                .execute(pool)
                .await?;

                sqlx::query(
                    "
                        DELETE FROM shippings.shipping_guides WHERE shipping_number=$1
                    "
                )
                .bind(guide.get_id())
                .execute(pool)
                .await?;

                pkgadmin_data.shipping_guides.as_mut().unwrap().viewing_guides.len()
            } else {
                unimplemented!()
            };

            let guide_pos = app_lock.temp_val.unwrap() as usize;
            if guide_pos == viewing_guides_len {
                app_lock.temp_val =
                    if guide_pos > 0 { Some((guide_pos - 1) as i64) }
                    else { None }
            }
            app_lock.get_pkgadmin_mut().shipping_guides.as_mut().unwrap().viewing_guides.remove(guide_pos);

            app_lock.enter_screen(Screen::PkgAdmin(SubScreen::PkgAdminGuides), pool).await;

            Ok(())
        }
        _ => panic!("An event of type {:?} was passed to the db::insert update function", event)
    }
}