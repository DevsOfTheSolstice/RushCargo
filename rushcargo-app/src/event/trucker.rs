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
    common::{Popup, Screen, InputMode, SubScreen, User},
    app::App,
    },
};

pub fn event_act(key_event: KeyEvent, sender: &mpsc::Sender<Event>, app: &Arc<Mutex<App>>) {
    let mut app_lock = app.lock().unwrap();

    let subscreen: &SubScreen = 
        if let Screen::Trucker(sub) = &app_lock.active_screen {
            sub
        } else {
            panic!("active_screen in client event_act is: {}", &app_lock.active_screen);
        };
    match subscreen {
        SubScreen::TruckerMain => {
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
            }.expect(SENDER_ERR);
        }
        SubScreen::TruckerManagementPackets => {
            match key_event.code {
                KeyCode::Esc => {
                    sender.send(Event::EnterScreen(Screen::Trucker(SubScreen::TruckerMain)))
                }
                //KeyCode::Down => {
                    //THE TABLE TO ACCEPT PACKAGES SHOULD LET THE TRUCKER
                    //DOWN, UP AND ACCEPT
                //}
               _ =>Ok(())
            }.expect(SENDER_ERR);
        }
        SubScreen::TruckerStatistics => {
            match key_event.code {
                KeyCode::Esc => {
                    sender.send(Event::EnterScreen(Screen::Trucker(SubScreen::TruckerMain)))
                } //IN THE TABLE THE USER HOULD BE CAPABLE OF 
                //CHOSING THE KIND OF STAT THEY WANT TO SEE
                _ => Ok(())
            }.expect(SENDER_ERR);
        }
        SubScreen::TruckerRoutes => {
            match key_event.code {
                KeyCode::Esc => {
                    sender.send(Event::EnterScreen(Screen::Trucker(SubScreen::TruckerMain)))
                }
                //TABLE IN WHICH THE TRUCKER SEES THEIRS ROUTES
                _ => Ok(())
            }.expect(SENDER_ERR);
        }
        _ => {}
    }
}