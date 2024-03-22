use std::sync::{Arc, Mutex};
use crossterm::event::{Event as CrosstermEvent, KeyCode};
use tui_input::backend::crossterm::EventHandler;
use sqlx::{Row, Pool, Postgres};
use bcrypt::verify;
use anyhow::Result;
use crate::{
    HELP_TEXT,
    event::{Event, InputBlacklist},
    model::{
        common::{User, Popup, UserType, TimeoutType},
        client::Client,
        app::App,
    }
};

static USER_SEARCH_QUERIES: [&str; 5] = [
    "SELECT * FROM natural_client WHERE username = $1",
    "SELECT * FROM legal_client WHERE username = $1",
    "SELECT * FROM truck_driver WHERE username = $1",
    "SELECT * FROM motocyclist WHERE username = $1",
    "SELECT * FROM root_user WHERE username = $1"
];

pub async fn update(app: &mut Arc<Mutex<App>>, pool: &Pool<Postgres>, event: Event) -> Result<()> {
    match event {
        Event::TryLogin => {
            if app.lock().unwrap().failed_logins == 3 {
                return Ok(());
            }

            let username: String = app.lock().unwrap().input.0.value().to_string();
            let password: String = app.lock().unwrap().input.0.value().to_string();

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
                                            Client {
                                                username,
                                                first_name,
                                                last_name
                                            }
                                        ))
                                    }
                                    1 => todo!("legal client login"),
                                    2 => todo!("trucker login"),
                                    3 => todo!("motorcyclist login"),
                                    4 => todo!("admin login"),
                                    _ => panic!("Unexpected i value in TryLogin event.")
                                };

                            app_lock.active_popup = Some(Popup::LoginSuccessful);
                            return Ok(());
                        }
                    }
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