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
        app::App, app_list::ListType, app_table::TableType, common::{Div, InputMode, Popup, Screen, SubScreen, User}, db_obj::ShippingGuideType
    },
};

pub fn event_act(key_event: KeyEvent, sender: &mpsc::Sender<Event>, app: &Arc<Mutex<App>>) {
    let app_lock = app.lock().unwrap();

    let subscreen =
        if let Screen::PkgAdmin(sub) = &app_lock.active_screen {
            sub
        } else {
            panic!("active_screen in client event_act is: {}", &app_lock.active_screen);
        };
 
    match subscreen {
        SubScreen::PkgAdminMain => {
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
        SubScreen::PkgAdminGuides => {
            match key_event.code {
                KeyCode::Esc => {
                    sender.send(Event::EnterScreen(Screen::PkgAdmin(SubScreen::PkgAdminMain)))
                }
                KeyCode::Down | KeyCode::Char('j') => {
                    sender.send(Event::NextTableItem(TableType::Guides))
                }
                KeyCode::Up | KeyCode::Char('k') => {
                    sender.send(Event::PrevTableItem(TableType::Guides))
                }
                KeyCode::Enter => {
                    sender.send(Event::SelectTableItem(TableType::Guides))
                }
                _ => Ok(())
            }
        }
        SubScreen::PkgAdminAddPackage(Div::Left) => {
            match key_event.code {
                KeyCode::Esc => {
                    sender.send(Event::EnterScreen(Screen::PkgAdmin(SubScreen::PkgAdminMain)))
                }
                KeyCode::Down => {
                    sender.send(Event::NextInput)
                }
                KeyCode::Up => {
                    sender.send(Event::PrevInput)
                }
                KeyCode::Enter => {
                    sender.send(Event::SwitchDiv)
                }
                _ => {
                    match app_lock.input_mode {
                        InputMode::Editing(0) => sender.send(Event::KeyInput(key_event, InputBlacklist::Alphanumeric)),
                        InputMode::Editing(1) | InputMode::Editing(2) | InputMode::Editing(3) |
                        InputMode::Editing(4) | InputMode::Editing(5) =>
                            sender.send(Event::KeyInput(key_event, InputBlacklist::Money)),
                        _ => Ok(())
                    }
                }
            }
        }
        SubScreen::PkgAdminAddPackage(Div::Right) => {
            match app_lock.active_popup {
                None =>
                    match key_event.code {
                        KeyCode::Esc => {
                            sender.send(Event::EnterScreen(Screen::PkgAdmin(SubScreen::PkgAdminAddPackage(Div::Left))))
                        }
                        KeyCode::Down => {
                            sender.send(Event::NextInput)
                        }
                        KeyCode::Up => {
                            sender.send(Event::PrevInput)
                        }
                        KeyCode::Enter => {
                            let add_package = app_lock.get_pkgadmin_ref().add_package.as_ref().unwrap();

                            let (locker_empty, branch_empty) = (add_package.locker.value().is_empty(), add_package.branch.value().is_empty());

                            if add_package.is_missing_attr() {
                                Ok(())
                            } else if !locker_empty && !branch_empty {
                                sender.send(Event::EnterPopup(Some(Popup::FieldExcess)))
                            } else if !locker_empty {
                                sender.send(Event::TryGetUserLocker(add_package.recipient.value().to_string(), add_package.locker.value().to_string()))
                            } else {
                                sender.send(Event::TryGetUserBranch(add_package.recipient.value().to_string(), add_package.branch.value().to_string()))
                            }
                        }
                        _ => {
                            match app_lock.input_mode {
                                InputMode::Editing(0) | InputMode::Editing(1) => sender.send(Event::KeyInput(key_event, InputBlacklist::Alphanumeric)),
                                InputMode::Editing(2) | InputMode::Editing(3) =>
                                    sender.send(Event::KeyInput(key_event, InputBlacklist::Numeric)),
                                _ => Ok(())
                            }
                        }
                    }
                Some(Popup::FieldExcess) | Some(Popup::OrderSuccessful) =>
                    match key_event.code {
                        _ => sender.send(Event::EnterPopup(None)),
                    },
                Some(Popup::SelectPayment) =>
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
                    },
                Some(Popup::OnlinePayment) => {
                    match key_event.code {
                        KeyCode::Esc => {
                            sender.send(Event::EnterPopup(Some(Popup::SelectPayment)))
                        }
                        KeyCode::Tab => {
                            sender.send(Event::SwitchAction)
                        }
                        KeyCode::Enter => {
                            if app_lock.input.0.value().is_empty() || app_lock.action_sel.is_none() {
                                Ok(())
                            } else {
                                sender.send(Event::UpdatePaymentInfo).expect(SENDER_ERR);
                                sender.send(Event::PlaceOrder)
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
                _ => Ok(())
            }
        }
        SubScreen::PkgAdminGuideInfo => {
            match app_lock.active_popup {
                None =>
                    match key_event.code {
                        KeyCode::Esc => {
                            sender.send(Event::EnterScreen(Screen::PkgAdmin(SubScreen::PkgAdminGuides)))
                        }
                        KeyCode::Down | KeyCode::Char('j') => {
                            sender.send(Event::NextTableItem(TableType::GuidePackages))
                        }
                        KeyCode::Up | KeyCode::Char('k') => {
                            sender.send(Event::PrevTableItem(TableType::GuidePackages))
                        }
                        KeyCode::Char('a') => {
                            sender.send(Event::PlaceOrder)
                        }
                        KeyCode::Char('r') => {
                            sender.send(Event::RejectOrderReq)
                        }
                        _ => Ok(())
                    },
                Some(Popup::OrderSuccessful) =>
                    match key_event.code {
                        _ => {
                            sender.send(Event::EnterPopup(None)).expect(SENDER_ERR);
                            sender.send(Event::EnterScreen(Screen::PkgAdmin(SubScreen::PkgAdminGuides)))
                        }
                    },
                _ => Ok(())
            }
        }
        _ => Ok(())
    }.expect(SENDER_ERR);
}