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
    app::App, common::{InputMode, SubScreen, Popup, Screen, User}
    },
};

pub fn event_act(key_event: KeyEvent, sender: &mpsc::Sender<Event>, app: &Arc<Mutex<App>>) {
    let mut app_lock = app.lock().unwrap();

    match app_lock.active_popup {
        Some(Popup::LoginSuccessful) => {
            if let Some(user_type) = &app_lock.user {
                match user_type {
                    User::Client(_) => sender.send(Event::EnterScreen(Screen::Client(SubScreen::ClientMain))),
                    _ => todo!("enter screen of user type: {:?}", user_type),
                }.expect(SENDER_ERR);
                app_lock.enter_popup(&Popup::None);
            }
        }
        None => {
            match key_event.code {
                KeyCode::Esc => sender.send(Event::EnterScreen(Screen::Title)),
                KeyCode::Enter => sender.send(Event::TryLogin),
                KeyCode::Tab => sender.send(Event::SwitchInput),
                _ => sender.send(Event::KeyInput(key_event, InputBlacklist::NoSpace))
            }.expect(SENDER_ERR);
        }
        _ => {}
    }
}