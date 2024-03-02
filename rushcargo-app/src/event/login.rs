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
    common::{Popup, Screen, InputMode},
    app::App,
    },
};

pub fn event_act(key_event: KeyEvent, sender: &mpsc::Sender<Event>, app: &Arc<Mutex<App>>) {
    let app_lock = app.lock().unwrap();

    match app_lock.active_popup {
        Some(Popup::LoginSuccessful) => {
            if let Some(user_type) = &app_lock.active_user {
                sender.send(Event::EnterScreen(Screen::Trucker))
            } else {
                Ok(())
            }.expect(SENDER_ERR);
        }
        None => {
            match key_event.code {
                KeyCode::Esc => sender.send(Event::Quit),
                KeyCode::Enter => sender.send(Event::TryLogin),
                KeyCode::Tab => sender.send(Event::SwitchInput),
                _ => sender.send(Event::KeyInput(key_event, InputBlacklist::NoSpace))
            }.expect(SENDER_ERR);
        }
    }
}