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
    app_list::ListType,
    common::{Popup, Screen, InputMode},
    app::App,
    },
};

pub fn event_act(key_event: KeyEvent, sender: &mpsc::Sender<Event>, app: &Arc<Mutex<App>>) {
    match key_event.code {
        KeyCode::Esc
        => sender.send(Event::Quit),

        KeyCode::Up | KeyCode::Char('k')
        => sender.send(Event::PrevListItem(ListType::Title)),

        KeyCode::Down | KeyCode::Char('j')
        => sender.send(Event::NextListItem(ListType::Title)),

        KeyCode::Enter
        => sender.send(Event::SelectAction(ListType::Title)),

        _ => Ok(())
    }.expect(SENDER_ERR);
}