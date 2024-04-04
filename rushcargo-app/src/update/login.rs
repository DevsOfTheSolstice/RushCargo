use std::sync::{Arc, Mutex};
use crossterm::event::{Event as CrosstermEvent, KeyCode};
use tui_input::backend::crossterm::EventHandler;
use sqlx::{Row, FromRow, PgPool};
use bcrypt::verify;
use anyhow::Result;
use crate::{
    event::{Event, InputBlacklist},
    model::{
        app::App,
        client::{self, Client, ClientData},
        db_obj::Branch,
        common::{Popup, TimeoutType, User, UserType},
        pkgadmin::{PkgAdmin, PkgAdminData}
    },
    GRAPH_URL,
    HELP_TEXT
};

static USER_SEARCH_QUERIES: [&str; 4] = [
    "SELECT * FROM users.natural_clients WHERE username = $1",
    "SELECT * FROM users.legal_clients WHERE username = $1",
    "SELECT * FROM vehicles.truckers WHERE username = $1",
    "SELECT * FROM vehicles.motorcyclists WHERE username = $1",
];

pub async fn update(app: &mut Arc<Mutex<App>>, pool: &PgPool, event: Event) -> Result<()> {
    match event {
        Event::TryLogin => {
            if app.lock().unwrap().failed_logins == 3 {
                return Ok(());
            }

            let username: String = app.lock().unwrap().input.0.value().to_string();
            let password: String = app.lock().unwrap().input.1.value().to_string();

            if let Some(res) = sqlx::query("SELECT * FROM users.users WHERE username = $1")
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
                                        let first_name = res.try_get("first_name")?;
                                        let last_name = res.try_get("last_name")?;
                                        let client_row = super::db::tryget::get_full_client(username.clone(), pool).await?;

                                        Some(User::Client(
                                            ClientData {
                                                info:
                                                    Client {
                                                        username,
                                                        affiliated_branch: Branch::from_row(&client_row)?,
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
                                                send_route: None,
                                                send_route_distance: None,
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

            if let Some(res) = sqlx::query("SELECT * FROM users.root_users WHERE username=$1")
                .bind(&username)
                .fetch_optional(pool)
                .await?
            {
                let password_hash: String = res.try_get("user_password")?;

                if verify(&password, &password_hash).unwrap_or_else(|error| panic!("{}", error)) {
                    let admin_type: &str = res.try_get("user_type")?;
                    match admin_type {
                        "PkgAdmin" => {
                            let client = reqwest::Client::new();
                            if !client.get(
                                GRAPH_URL.lock().unwrap().clone()
                            )
                            .send()
                            .await.is_ok()
                            {
                                app.lock().unwrap().temp_row = Some(res);
                                app.lock().unwrap().enter_popup(Some(Popup::ServerUnavailable), pool).await;
                                return Ok(());
                            }
                            app.lock().unwrap().temp_row = Some(res);
                            login_as(UserType::PkgAdmin, app, pool).await?;
                        }
                        _ => panic!("unknown admin type: {}", admin_type),
                    }
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

pub async fn login_as(user: UserType, app: &mut Arc<Mutex<App>>, pool: &PgPool) -> Result<()> {
    let mut app_lock = app.lock().unwrap();
    let row = app_lock.temp_row.as_ref().unwrap();
    match user {
        UserType::PkgAdmin => {
            app_lock.user = Some(User::PkgAdmin(
                PkgAdminData {
                    info: PkgAdmin {
                        username: row.try_get("username")?,
                        branch_id: row.try_get("branch_id")?,
                        first_name: row.try_get("first_name")?,
                        last_name: row.try_get("last_name")?,
                    },
                    shipping_guides: None,
                    packages: None,
                    add_package: None,
                    get_db_err: None,
                }
            ));
        }
        _ => unimplemented!("fn login_as() for user {:?}", user)
    }
    app_lock.temp_row = None;
    app_lock.enter_popup(Some(Popup::LoginSuccessful), pool).await;
    Ok(())
}