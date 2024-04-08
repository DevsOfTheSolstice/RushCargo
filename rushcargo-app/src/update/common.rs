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
        trucker::Trucker,
        common::{Bank, PaymentType, UserType, InputMode, PaymentData, Popup, Screen, SubScreen, Div, User},
    },
};

pub async fn update(app: &mut Arc<Mutex<App>>, pool: &PgPool, event: Event) -> Result<()> {
    match event {
        Event::Quit => {
            app.lock().unwrap().should_quit = true;
            Ok(())
        }
        Event::TimeoutTick(timeout_type) => {
            app.lock().unwrap().update_timeout_counter(timeout_type);
            Ok(())
        }
        Event::EnterScreen(screen) => {
            app.lock().unwrap().enter_screen(screen, pool).await;
            Ok(())
        }
        Event::EnterPopup(popup) => {
            app.lock().unwrap().enter_popup(popup, pool).await;
            Ok(())
        }
        Event::SwitchDiv => {
            let mut app_lock = app.lock().unwrap();

            let active_screen = app_lock.active_screen.clone();

            match active_screen {
                Screen::PkgAdmin(SubScreen::PkgAdminAddPackage(div)) =>
                    app_lock.enter_screen(Screen::PkgAdmin(SubScreen::PkgAdminAddPackage(
                        if let Div::Left = div { Div::Right }
                        else { Div::Left }
                    )
                ), pool)
                .await,
                _ => unimplemented!("div for screen {:?}", app_lock.active_screen)
            }
            Ok(())
        }
        Event::ToggleDisplayMsg => {
            app.lock().unwrap().toggle_displaymsg();
            Ok(())
        }
        Event::SwitchInput => {
            let mut app_lock = app.lock().unwrap();

            if let InputMode::Editing(field) = app_lock.input_mode {
                if field == 0 { app_lock.input_mode = InputMode::Editing(1) }
                else { app_lock.input_mode = InputMode::Editing(0) }
            }
            Ok(())
        }
        Event::NextInput => {
            let mut app_lock = app.lock().unwrap();

            if let InputMode::Editing(field) = app_lock.input_mode {
                let limit =
                    match app_lock.active_screen {
                        Screen::PkgAdmin(SubScreen::PkgAdminAddPackage(Div::Left)) => 5,
                        Screen::PkgAdmin(SubScreen::PkgAdminAddPackage(Div::Right)) => 3,
                        _ => unimplemented!("{:?} for {:?}", event, app_lock.active_screen)
                };
                app_lock.input_mode = InputMode::Editing(
                    if field < limit { field + 1 }
                    else { 0 }
                );
            }
            Ok(())
        }
        Event::PrevInput => {
            let mut app_lock = app.lock().unwrap();

            if let InputMode::Editing(field) = app_lock.input_mode {
                let limit =
                    match app_lock.active_screen {
                        Screen::PkgAdmin(SubScreen::PkgAdminAddPackage(Div::Left)) => 5,
                        Screen::PkgAdmin(SubScreen::PkgAdminAddPackage(Div::Right)) => 2,
                        _ => unimplemented!("{:?} for {:?}", event, app_lock.active_screen)
                };
                app_lock.input_mode = InputMode::Editing(
                    if field == 0 { limit }
                    else { field - 1 }
                );
            }
            Ok(())
        }
        Event::SwitchAction => {
            let mut app_lock = app.lock().unwrap();

            match app_lock.active_screen {
                Screen::Login => {
                    match app_lock.action_sel {
                        Some(val) if val < 1 => app_lock.action_sel = Some(val + 1),
                        _ => app_lock.action_sel = Some(0),
                    }
                }
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
                        Some(Popup::OnlinePayment) => {
                            match app_lock.action_sel {
                                Some(val) if val < 1 => {
                                    app_lock.action_sel = Some(val + 1);
                                    app_lock.input_mode = InputMode::Normal;
                                }
                                _ => {
                                    app_lock.action_sel = Some(0);
                                    app_lock.input_mode = InputMode::Editing(0);
                                }
                            }
                        }
                        _ => {}
                    }
                }
                Screen::PkgAdmin(SubScreen::PkgAdminMain) => {
                    match app_lock.action_sel {
                        Some(val) if val < 1 => app_lock.action_sel = Some(val + 1),
                        _ => app_lock.action_sel = Some(0),
                    }
                }
                Screen::PkgAdmin(SubScreen::PkgAdminAddPackage(_)) => {
                    match app_lock.active_popup {
                        Some(Popup::SelectPayment) => {
                            match app_lock.action_sel {
                                Some(val) if val < 2 => app_lock.action_sel = Some(val + 1),
                                _ => app_lock.action_sel = Some(0),
                            }
                        }
                        Some(Popup::OnlinePayment) => {
                            match app_lock.action_sel {
                                Some(val) if val < 1 => {
                                    app_lock.action_sel = Some(val + 1);
                                    app_lock.input_mode = InputMode::Normal;
                                }
                                _ => {
                                    app_lock.action_sel = Some(0);
                                    app_lock.input_mode = InputMode::Editing(0);
                                }
                            }
                        }
                        _ => {}
                    }
                }
                Screen::Trucker(SubScreen::TruckerMain) => {
                    match app_lock.action_sel {
                        Some(val) if val < 3 => app_lock.action_sel = Some(val + 1),
                        _ => app_lock.action_sel = Some(0),
                    }
                }
                _ => {}
            }
            Ok(())
        }
        Event::SelectAction => {
            let subscreen = {
                let app_lock = app.lock().unwrap();
                match &app_lock.active_screen {
                    Screen::Login => None,
                    Screen::Client(sub) => Some(sub.clone()),
                    Screen::PkgAdmin(sub) => Some(sub.clone()),
                    Screen::Trucker(sub) => Some(sub.clone()),
                    _ => None
                }
            };

            match subscreen {
                None => {
                    let action_sel = app.lock().unwrap().action_sel.clone();
                    match action_sel {
                        Some(0) => super::login::login_as(UserType::PkgAdmin, app, pool).await?,
                        Some(1) => app.lock().unwrap().enter_popup(None, pool).await,
                        _ => {}
                    }
                }
                Some(SubScreen::ClientMain) => {
                    let mut app_lock = app.lock().unwrap();
                    match app_lock.action_sel {
                        Some(0) => app_lock.enter_screen(Screen::Client(SubScreen::ClientLockers), pool).await,
                        Some(1) => app_lock.enter_screen(Screen::Client(SubScreen::ClientSentPackages), pool).await,
                        _ => {}
                    }
                }
                Some(SubScreen::ClientLockerPackages) => {
                    let mut app_lock = app.lock().unwrap();
                    match app_lock.action_sel {
                        Some(0) => app_lock.enter_popup(Some(Popup::ClientOrderLocker), pool).await,
                        Some(1) => app_lock.enter_popup(Some(Popup::ClientOrderBranch), pool).await,
                        Some(2) => app_lock.enter_popup(Some(Popup::ClientOrderDelivery), pool).await,
                        _ => {}
                    }
                }
                Some(SubScreen::PkgAdminMain) => {
                    let mut app_lock = app.lock().unwrap();
                    match app_lock.action_sel {
                        Some(0) => app_lock.enter_screen(Screen::PkgAdmin(SubScreen::PkgAdminGuides), pool).await,
                        Some(1) => app_lock.enter_screen(Screen::PkgAdmin(SubScreen::PkgAdminAddPackage(Div::Left)), pool).await,
                        _ => {}
                    }
                }
                Some(SubScreen::PkgAdminAddPackage(_)) => {
                    let mut app_lock = app.lock().unwrap();
                    match app_lock.action_sel {
                        Some(0) => app_lock.enter_popup(Some(Popup::OnlinePayment), pool).await,
                        Some(1) => app_lock.enter_popup(Some(Popup::CardPayment), pool).await,
                        Some(2) => app_lock.enter_popup(Some(Popup::CashPayment), pool).await,
                        _ => {}
                    }
                }
                Some(SubScreen::TruckerMain) => {
                    let mut app_lock = app.lock().unwrap();
                    match app_lock.action_sel {
                        Some(0) => app_lock.enter_screen(Screen::Trucker(SubScreen::TruckerStatistics), pool).await,
                        Some(1) => app_lock.enter_screen(Screen::Trucker(SubScreen::TruckerManagementPackages), pool).await,
                        Some(2) => app_lock.enter_screen(Screen::Trucker(SubScreen::TruckerRoutes), pool).await, 
                        _ => {}    
                    }
                }
                _ => unimplemented!("select action on screen: {:?}, subscreen: {:?}", app.lock().unwrap().active_screen, subscreen)
            }
            Ok(()) 
        }
        Event::KeyInput(key_event, blacklist) => {
            let mut app_lock = app.lock().unwrap();

            let field = match app_lock.input_mode {
                InputMode::Editing(field) => field,
                InputMode::Normal => panic!("KeyInput event fired when InputMode was normal")
            };

            let input_obj = match app_lock.active_screen {
                Screen::PkgAdmin(SubScreen::PkgAdminAddPackage(Div::Left)) => {
                    match app_lock.active_popup {
                        None => {
                            let add_package = app_lock.get_pkgadmin_mut().add_package.as_mut().unwrap();
                            match field {
                                0 => &mut add_package.content,
                                1 => &mut add_package.value,
                                2 => &mut add_package.weight,
                                3 => &mut add_package.length,
                                4 => &mut add_package.width,
                                5 => &mut add_package.height,
                                _ => unimplemented!("input field {} for screen {:?}, popup {:?}", field, app_lock.active_screen, app_lock.active_popup)
                            }
                        }
                        Some(Popup::OnlinePayment) => {
                            match field {
                                0 => &mut app_lock.input.0,
                                _ => unimplemented!("input field {} for screen {:?}, popup {:?}", field, app_lock.active_screen, app_lock.active_popup)
                            }
                        }
                        _ => panic!()
                    }
                }
                Screen::PkgAdmin(SubScreen::PkgAdminAddPackage(Div::Right)) => {
                    match app_lock.active_popup {
                        None => {
                            let add_package = app_lock.get_pkgadmin_mut().add_package.as_mut().unwrap();
                            match field {
                                0 => &mut add_package.recipient,
                                1 => &mut add_package.sender,
                                2 => &mut add_package.locker,
                                3 => &mut add_package.branch,
                                _ => unimplemented!("input field {} for screen {:?}, popup {:?}", field, app_lock.active_screen, app_lock.active_popup)
                            }
                        }
                        Some(Popup::OnlinePayment) => {
                            match field {
                                0 => &mut app_lock.input.0,
                                _ => unimplemented!("input field {} for screen {:?}, popup {:?}", field, app_lock.active_screen, app_lock.active_popup)
                            }
                        }
                        _ => panic!()
                    }
                }
                _ => {
                    match field {
                        0 => &mut app_lock.input.0,
                        1 => &mut app_lock.input.1,
                        _ => unimplemented!("input field {} for screen {:?}", field, app_lock.active_screen)
                    }
                }
            };

            if let KeyCode::Char(char) = key_event.code {
                match blacklist {
                    InputBlacklist::None => {}
                    InputBlacklist::Money => {
                        let input_value = input_obj.value();

                        if char != '.' {
                            if !char.is_numeric() {
                                return Ok(());
                            } else {
                                if let Some(dot_index) = input_value.find('.') {
                                    if input_value[dot_index + 1..].len() == 2 { return Ok(()) }
                                }
                            }
                        } else {
                            if input_value.contains('.') {
                                return Ok(())
                            } 
                        }
                    }
                    InputBlacklist::Alphabetic => {
                        if !char.is_alphabetic() && char != ' ' {
                            return Ok(())
                        }
                    }
                    InputBlacklist::AlphanumericNoSpace => {
                        if !char.is_alphanumeric() {
                            return Ok(())
                        }
                    }
                    InputBlacklist::Alphanumeric => {
                        if !char.is_alphanumeric() && char != ' ' {
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

            input_obj.handle_event(&CrosstermEvent::Key(key_event));
            
            Ok(())
        }
        Event::UpdatePaymentInfo => {
            let selection = app.lock().unwrap().list.state.0.selected(); 

            let bank =
                match selection.unwrap_or_else(|| panic!("executed UpdatePaymentInfo on selection value: {:?}", selection)) {
                    0 => Bank::PayPal,
                    1 => Bank::AmazonPay,
                    2 => Bank::BOFA,
                    _ => panic!("bank is not in UpdatePaymentInfo")
                };
            
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
            };
            Ok(())
        }
        _ => panic!("An event of type {:?} was passed to the common update function", event)
    }
}