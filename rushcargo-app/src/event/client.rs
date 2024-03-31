use crossterm::event::{
    self,
    Event as CrosstermEvent,
    KeyEventKind,
    KeyCode,
    KeyEvent,
    KeyModifiers
};
use std::{
    sync::{mpsc, Arc, Mutex, MutexGuard},
};
use crate::{
    event::{Event, InputBlacklist, SENDER_ERR},
    model::{
        app::App, common::{SubScreen, InputMode, Popup, Screen, User},
        app_list::ListType,
        app_table::TableType,
    },
};

pub fn event_act(key_event: KeyEvent, sender: &mpsc::Sender<Event>, app: &Arc<Mutex<App>>) {
    let app_lock = app.lock().unwrap();

    let subscreen =
        if let Screen::Client(sub) = &app_lock.active_screen {
            sub
        } else {
            panic!("active_screen in client event_act is: {}", &app_lock.active_screen);
        };
    
    match subscreen {
        SubScreen::ClientMain => {
            match key_event.code {
                KeyCode::Esc => {
                    sender.send(Event::EnterScreen(Screen::Login))
                }
                KeyCode::Tab => {
                    sender.send(Event::SwitchAction)
                }
                KeyCode::Enter => {
                    sender.send(Event::SelectAction)
                }
                _ => Ok(())
            }
        }
        SubScreen::ClientLockers => {
            match key_event.code {
                KeyCode::Esc => {
                    sender.send(Event::EnterScreen(Screen::Client(SubScreen::ClientMain)))
                }
                KeyCode::Down | KeyCode::Char('j') => {
                    sender.send(Event::NextTableItem(TableType::Lockers))
                }
                KeyCode::Up | KeyCode::Char('k') => {
                    sender.send(Event::PrevTableItem(TableType::Lockers))
                }
                KeyCode::Enter => {
                    sender.send(Event::SelectTableItem(TableType::Lockers))
                }
                _ => Ok(())
            }
        }
        SubScreen::ClientLockerPackages => {
            match app_lock.active_popup {
                None =>
                    match key_event.code {
                        KeyCode::Esc => {
                            sender.send(Event::EnterScreen(Screen::Client(SubScreen::ClientLockers)))
                        }
                        KeyCode::Down | KeyCode::Char('j') => {
                            sender.send(Event::NextTableItem(TableType::LockerPackages))
                        }
                        KeyCode::Up | KeyCode::Char('k') => {
                            sender.send(Event::PrevTableItem(TableType::LockerPackages))
                        }
                        KeyCode::Char('s') => {
                            sender.send(Event::SelectTableItem(TableType::LockerPackages))
                        }
                        KeyCode::Enter => {
                            if let Some(_) = app_lock.get_packages_ref().selected_packages {
                                sender.send(Event::EnterPopup(Some(Popup::ClientOrderMain)))
                            } else { Ok(()) }
                        }
                        _ => Ok(())
                    }
                Some(Popup::ClientOrderMain) =>
                    match key_event.code {
                        KeyCode::Esc => {
                            sender.send(Event::EnterPopup(None))
                        }
                        KeyCode::Tab => {
                            sender.send(Event::SwitchAction)
                        }
                        KeyCode::Enter => {
                            sender.send(Event::SelectAction)
                        }
                        _ => Ok(())
                    }
                Some(Popup::ClientOrderLocker) => {
                    match key_event.code {
                        KeyCode::Esc => {
                            sender.send(Event::EnterPopup(Some(Popup::ClientOrderMain)))
                        }
                        KeyCode::Tab => {
                            sender.send(Event::SwitchInput)
                        }
                        KeyCode::Enter => {
                            sender.send(Event::TryGetUserLocker(
                                app_lock.input.0.value().to_string(),
                                app_lock.input.1.value().to_string()
                            ))
                        }
                        _ => {
                            if let InputMode::Editing(0) = app_lock.input_mode {
                                sender.send(Event::KeyInput(key_event, InputBlacklist::NoSpace))
                            } else {
                                sender.send(Event::KeyInput(key_event, InputBlacklist::Numeric))
                            }
                        }
                    }
                }
                Some(Popup::ClientInputPayment) => {
                    match key_event.code {
                        KeyCode::Esc => {
                           sender.send(Event::EnterPopup(Some(Popup::ClientOrderMain)))
                        }
                        KeyCode::Tab => {
                            sender.send(Event::SwitchAction)
                        }
                        KeyCode::Enter => {
                            if let Some(_) = app_lock.get_client_ref().send_to_locker {
                                sender.send(Event::PlaceOrderLockerLocker)
                            } else if let Some(_) = app_lock.get_client_ref().send_to_branch {
                                sender.send(Event::PlaceOrderLockerBranch)
                            } else {
                                sender.send(Event::PlaceOrderLockerDelivery)
                            }
                        }
                        _ =>
                            match app_lock.action_sel {
                                Some(0) => sender.send(Event::KeyInput(key_event, InputBlacklist::Alphanumeric)),
                                Some(1) =>
                                    match key_event.code {
                                        KeyCode::Down | KeyCode::Char('j') => sender.send(Event::NextListItem(ListType::PaymentBanks)),
                                        KeyCode::Up | KeyCode::Char('k') => sender.send(Event::PrevListItem(ListType::PaymentBanks)),
                                        _ => Ok(())
                                    }
                                _ => Ok(())
                            }
                    }
                }
                Some(Popup::OrderSuccessful) => {
                    sender.send(Event::EnterPopup(None))
                }
                Some(Popup::ClientOrderBranch) => {
                    match key_event.code {
                        KeyCode::Esc => {
                            sender.send(Event::EnterPopup(Some(Popup::ClientOrderMain)))
                        }
                        KeyCode::Tab => {
                            sender.send(Event::SwitchInput)
                        }
                        KeyCode::Enter => {
                            sender.send(Event::TryGetUserBranch(
                                app_lock.input.0.value().to_string(),
                                app_lock.input.1.value().to_string()
                            ))
                        }
                        _ => {
                            if let InputMode::Editing(0) = app_lock.input_mode {
                                sender.send(Event::KeyInput(key_event, InputBlacklist::NoSpace))
                            } else {
                                sender.send(Event::KeyInput(key_event, InputBlacklist::Numeric))
                            }
                        }
                        _ => Ok(())
                    }
                }
                Some(Popup::ClientOrderDelivery) => {
                    match key_event.code {
                        KeyCode::Esc => {
                            sender.send(Event::EnterPopup(Some(Popup::ClientOrderMain)))
                        }
                        KeyCode::Enter => {
                            sender.send(Event::TryGetUserDelivery(app_lock.input.0.value().to_string()))
                        }
                        _ => {
                            sender.send(Event::KeyInput(key_event, InputBlacklist::Alphanumeric))
                        }
                    }
                }
                Some(Popup::DisplayMsg) => {
                    sender.send(Event::ToggleDisplayMsg)
                }
                _ => Ok(())
            }
        }
        SubScreen::ClientSentPackages => {
            match key_event.code {
                KeyCode::Esc => {
                    sender.send(Event::EnterScreen(Screen::Client(SubScreen::ClientMain)))
                }
                _ => Ok(())
            }
        }
        _ => Ok(())
    }.expect(SENDER_ERR);
}