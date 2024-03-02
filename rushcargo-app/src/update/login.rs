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
        common::{Popup, UserType, TimeoutType},
        app::App,
    }
};

static USER_SEARCH_QUERIES: [&str;4] = [
    "SELECT * FROM camionero WHERE username = $1",
    "SELECT * FROM motorizado WHERE username = $1",
    "SELECT * FROM cliente_natural WHERE username = $1",
    "SELECT * FROM cliente_juridico WHERE username = $1"
];

pub async fn update(app: &mut Arc<Mutex<App>>, pool: &Pool<Postgres>, event: Event) -> Result<()> {
    match event {
        Event::TryLogin => {
            if app.lock().unwrap().failed_logins == 3 {
                return Ok(());
            }

            let username: String = app.lock().unwrap().input.0.value().to_string();
            let password: String = app.lock().unwrap().input.0.value().to_string();

            for(i, query) in USER_SEARCH_QUERIES.iter().enumerate() {
                if let Some(res) = sqlx::query(query)
                    .bind(&username)
                    .fetch_optional(pool)
                    .await? {
                        let password_hash: String = res.try_get("contrasena")?;

                        if verify(&password, &password_hash).unwrap_or_else(|error| panic!("{}", error)) {
                            let mut app_lock = app.lock().unwrap();

                            app_lock.active_user = Some(
                                match i {
                                    0 => UserType::Trucker,
                                    1 => UserType::MotorcycleCourier,
                                    2 => UserType::NaturalClient,
                                    3 => UserType::LegalClient,
                                    _ => panic!("Unexpected i value in TryLogin event.")
                                }
                            );

                            app_lock.active_popup = Some(Popup::LoginSuccessful);
                            return Ok(());
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