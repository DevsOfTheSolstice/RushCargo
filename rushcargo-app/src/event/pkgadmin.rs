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
        SubScreen::PkgAdminAddPackage => {
            match key_event.code {
                KeyCode::Esc => {
                    sender.send(Event::EnterScreen(Screen::PkgAdmin(SubScreen::PkgAdminMain)))
                }
                _ => Ok(())
            }
        }
        SubScreen::PkgAdminGuideInfo => {
            match key_event.code {
                KeyCode::Esc => {
                    sender.send(Event::EnterScreen(Screen::PkgAdmin(SubScreen::PkgAdminGuides)))
                }
                _ => Ok(())
            }
        }
        _ => Ok(())
    }.expect(SENDER_ERR);
}