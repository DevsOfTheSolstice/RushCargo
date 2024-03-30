use std::sync::{Arc, Mutex};
use crossterm::event::{Event as CrosstermEvent, KeyCode};
use tui_input::backend::crossterm::EventHandler;
use sqlx::{Row, PgPool};
use bcrypt::verify;
use anyhow::Result;
use crate::{
    HELP_TEXT,
    event::{Event, InputBlacklist},
    model::{
        common::{User, Popup, TimeoutType},
        client::{ClientData, Client},
        pkgadmin::{PkgAdminData, PkgAdmin},
        app::App,
    }
};

static USER_SEARCH_QUERIES: [&str; 4] = [
    "SELECT * FROM natural_clients WHERE username = $1",
    "SELECT * FROM legal_clients WHERE username = $1",
    "SELECT * FROM truck_drivers WHERE username = $1",
    "SELECT * FROM motorcyclists WHERE username = $1",
];

pub async fn update(app: &mut Arc<Mutex<App>>, pool: &PgPool, event: Event) -> Result<()> {
    match event {
        Event::TryLogin => {
            if app.lock().unwrap().failed_logins == 3 {
                return Ok(());
            }

            let username: String = app.lock().unwrap().input.0.value().to_string();
            let password: String = app.lock().unwrap().input.1.value().to_string();

            if let Some(res) = sqlx::query("SELECT * FROM users WHERE username = $1")
                .bind(&username)
                .fetch_optional(pool)
                .await?
            {
                let password_hash: String = res.try_get("user_password")?;

                if verify(&password, &password_hash).unwrap_or_else(|error| panic!("{}", error)) {
                    let mut app_lock = app.lock().unwrap();
                    for (i, query) in USER_SEARCH_QUERIES.iter().enumerate() {
                        if let Some(res) = sqlx::query(query)
                            .bind(&username)
                            .fetch_optional(pool)
                            .await?
                        {
                            app_lock.user =
                                match i {
                                    0 => {
                                        let first_name = res.try_get("client_name")?;
                                        let last_name = res.try_get("last_name")?;
                                        Some(User::Client(
                                            ClientData {
                                                info:
                                                    Client {
                                                        username,
                                                        first_name,
                                                        last_name
                                                    },
                                                viewing_lockers: None,
                                                viewing_lockers_idx: 0,
                                                active_locker: None,
                                                packages: None,
                                                send_to_locker: None,
                                                get_db_err: None,
                                                send_to_client: None,
                                                send_to_branch: None,
                                                getuser_fail_count: 0,
                                                send_payment: None,
                                                send_with_delivery: false,
                                            }
                                        ))
                                    }
                                    1 => todo!("legal client login"),
                                    2 => todo!("trucker login"),
                                    3 => todo!("motorcyclist login"),
                                    _ => panic!("Unexpected i value in TryLogin event.")
                                };
                            
                            app_lock.enter_popup(Some(Popup::LoginSuccessful), pool).await;
                            return Ok(());
                        }
                    }
                }
            }

            if let Some(res) = sqlx::query("SELECT * FROM root_users WHERE username=$1")
                .bind(&username)
                .fetch_optional(pool)
                .await?
            {
                let password_hash: String = res.try_get("user_password")?;

                if verify(&password, &password_hash).unwrap_or_else(|error| panic!("{}", error)) {
                    let admin_type: &str = res.try_get("type")?;
                    let mut app_lock = app.lock().unwrap();
                    app_lock.user =
                        match admin_type { 
                            "PkgAdmin" => Some(User::PkgAdmin(
                                PkgAdminData {
                                    info: PkgAdmin {
                                        username,
                                        warehouse_id: res.try_get("warehouse_id")?,
                                        first_name: res.try_get("first_name")?,
                                        last_name: res.try_get("last_name")?,
                                    },
                                    packages: None,
                                    shipping_guides: None,
                                    get_db_err: None,
                                }
                            )),
                            _ => panic!("unknown admin type: {}", admin_type),
                        };

                    app_lock.enter_popup(Some(Popup::LoginSuccessful), pool).await;
                    return Ok(())
                }
            }

            let mut app_lock = app.lock().unwrap();
            app_lock.failed_logins += 1;
            
            if app_lock.failed_logins == 3 {
                app_lock.add_timeout(30, 1000, TimeoutType::Login);
            }
            Ok(())
        },
        _ => panic!("An event of type {:?} was passed to the login update function", event)
    }
}