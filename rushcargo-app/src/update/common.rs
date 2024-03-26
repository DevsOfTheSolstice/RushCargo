use std::sync::{Arc, Mutex};
use rust_decimal::Decimal;
use crossterm::event::{Event as CrosstermEvent, KeyCode};
use tui_input::backend::crossterm::EventHandler;
use sqlx::{Row, FromRow, PgPool};
use anyhow::{Result, anyhow};
use crate::{
    HELP_TEXT,
    event::{Event, InputBlacklist},
    model::{
        common::{Screen, Popup, SubScreen, User, InputMode},
        common_obj::Locker,
        client::GetLockerErr,
        app::App,
    }
};

use super::client;

pub async fn update(app: &mut Arc<Mutex<App>>, pool: &PgPool, event: Event) -> Result<()> {
    match event {
        Event::Quit => {
            app.lock().unwrap().should_quit = true;
            Ok(())
        },
        Event::TimeoutTick(timeout_type) => {
            app.lock().unwrap().update_timeout_counter(timeout_type);
            Ok(())
        }
        Event::EnterScreen(screen) => {
            app.lock().unwrap().enter_screen(screen, pool).await;
            Ok(())
        },
        Event::EnterPopup(popup) => {
            app.lock().unwrap().enter_popup(popup, pool).await;
            Ok(())
        },
        Event::SwitchInput => {
            let mut app_lock = app.lock().unwrap();

            if let InputMode::Editing(field) = app_lock.input_mode {
                if field == 0 { app_lock.input_mode = InputMode::Editing(1) }
                else { app_lock.input_mode = InputMode::Editing(0) }
            }
            Ok(())
        },
        Event::SwitchAction => {
            let mut app_lock = app.lock().unwrap();

            match app_lock.active_screen {
                Screen::Client(SubScreen::ClientMain) => {
                    match app_lock.action_sel {
                        Some(val) if val < 1 => app_lock.action_sel = Some(val + 1),
                        _ => app_lock.action_sel = Some(0),
                    }
                }
                Screen::Client(SubScreen::ClientLockerPackages) => {
                    match app_lock.active_popup {
                        Some(Popup::ClientOrderMain) => {
                            match app_lock.action_sel {
                                Some(val) if val < 2 => app_lock.action_sel = Some(val + 1),
                                _ => app_lock.action_sel = Some(0),
                            }
                        }
                        _ => {}
                    }
                }
                _ => {}
            }
            Ok(())
        },
        Event::SelectAction => {
            let mut app_lock = app.lock().unwrap();

            let subscreen = 
                match &app_lock.active_screen {
                    Screen::Client(sub) => Some(sub),
                    _ => None
                };

            match subscreen {
                Some(SubScreen::ClientMain) => {
                    match app_lock.action_sel {
                        Some(0) => app_lock.enter_screen(Screen::Client(SubScreen::ClientLockers), pool).await,
                        Some(1) => app_lock.enter_screen(Screen::Client(SubScreen::ClientSentPackages), pool).await,
                        _ => {}
                    }
                }
                Some(SubScreen::ClientLockerPackages) => {
                    match app_lock.action_sel {
                        Some(0) => app_lock.enter_popup(Some(Popup::ClientOrderLocker), pool).await,
                        Some(1) => app_lock.enter_popup(Some(Popup::ClientOrderBranch), pool).await,
                        Some(2) => app_lock.enter_popup(Some(Popup::ClientOrderDelivery), pool).await,
                        _ => {}
                    }
                }
                _ => unimplemented!("select action on screen: {:?}, subscreen: {:?}", app_lock.active_screen, subscreen)
            }
            Ok(()) 
        },
        Event::TryGetUserLocker(username, locker_id) => {
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
                                client_data.send_to_locker_err = Some(GetLockerErr::SameAsActive);
                                return Ok(())
                            }

                            if sqlx::query("SELECT COUNT(*) AS package_count FROM package WHERE locker_id=$1")
                                .bind(locker_id)
                                .fetch_one(pool)
                                .await?
                                .get::<i64, _>("package_count") >= 5
                            {
                                client_data.send_to_locker_err = Some(GetLockerErr::TooManyPackages);
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
                                .get::<Decimal, _>("weight_sum");
                            
                            let selected_packages_weight =
                                client_data.packages.as_ref().unwrap().selected_packages.as_ref().unwrap()
                                .iter()
                                .map(|package| package.weight)
                                .sum::<Decimal>();

                            if locker_packages_weight + selected_packages_weight >= Decimal::new(500000, 0)
                            {
                                client_data.send_to_locker_err = Some(GetLockerErr::WeightTooBig(Decimal::new(500000, 0) - locker_packages_weight));
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

                            app_lock.enter_popup(Some(Popup::ClientInputPayment), pool).await;
                        }
                        _ => {}
                    }
                }
            }
            else {
                let mut app_lock = app.lock().unwrap();
                match &mut app_lock.user {
                    Some(User::Client(client_data)) => {
                        client_data.send_to_locker_err = Some(GetLockerErr::Invalid);
                    }
                    _ => {}
                }
            }
            Ok(())
        },
        Event::KeyInput(key_event, blacklist) => {
            let mut app_lock = app.lock().unwrap();

            let field = match app_lock.input_mode {
                InputMode::Editing(field) => field,
                InputMode::Normal => panic!("KeyInput event fired when InputMode was normal")
            };

            if let KeyCode::Char(char) = key_event.code {
                match blacklist {
                    InputBlacklist::None => {}
                    InputBlacklist::Money => {
                        let input_value = {
                            if field == 0 {
                                app_lock.input.0.value()
                            } else {
                                app_lock.input.1.value()
                            }
                        };

                        if char != '.' {
                            if !char.is_numeric() {
                                return Ok(());
                            } else {
                                if let Some(dot_index) = input_value.find('.') {
                                    if input_value[dot_index + 1..].len() == 2 { return Ok(()) }
                                }
                            }
                        } else {
                            if app_lock.input.0.value().contains('.') {
                                return Ok(())
                            } 
                        }
                    }
                    InputBlacklist::Alphabetic => {
                        if !char.is_alphabetic() && char != ' ' {
                            return Ok(())
                        }
                    }
                    InputBlacklist::NoSpace => {
                        if char == ' ' {
                            return Ok(())
                        }
                    }
                    InputBlacklist::Numeric => {
                        if !char.is_numeric() {
                            return Ok(())
                        }
                    }
                }
            };
 
            if field == 0 { app_lock.input.0.handle_event(&CrosstermEvent::Key(key_event)); }
            else { app_lock.input.1.handle_event(&CrosstermEvent::Key(key_event)); }
            Ok(())
        },
        _ => panic!("An event of type {:?} was passed to the common update function", event)
    }
}