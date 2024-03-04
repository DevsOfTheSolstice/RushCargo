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
    app_list::ListType,
    },
};

pub fn event_act(key_event: KeyEvent, sender: &mpsc::Sender<Event>, app: &Arc<Mutex<App>>) {
    match key_event.code {
        KeyCode::Esc
        => sender.send(Event::EnterScreen(Screen::Title)),

        KeyCode::Up | KeyCode::Char('k')
        => sender.send(Event::PrevListItem(ListType::Settings)),

        KeyCode::Down | KeyCode::Char('j')
        => sender.send(Event::NextListItem(ListType::Settings)),

        KeyCode::Enter
        => sender.send(Event::SelectAction(ListType::Settings)),

        _ => Ok(())
    }.expect(SENDER_ERR);
}