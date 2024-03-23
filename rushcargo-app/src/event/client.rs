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
    app_table::TableType
    },
};

pub fn event_act(key_event: KeyEvent, sender: &mpsc::Sender<Event>, app: &Arc<Mutex<App>>) {
    let mut app_lock = app.lock().unwrap();

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