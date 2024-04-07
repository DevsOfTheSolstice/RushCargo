mod title;
mod settings;
mod login;
mod client;
mod pkgadmin;

use crossterm::event::{
    self,
    Event as CrosstermEvent,
    KeyEventKind,
    KeyCode,
    KeyEvent,
    KeyModifiers,
};
use std::{
    sync::{mpsc, Arc, Mutex, MutexGuard},
    thread,
    time::{Duration, Instant}
};
use anyhow::Result;
use crate::model::{
    app::App,
    app_list::ListType,
    app_table::TableType,
    common::{Popup, Screen, TimeoutType},
};

const SENDER_ERR: &'static str = "could not send terminal event";

#[derive(Debug)]
pub enum InputBlacklist {
    None,
    Money,
    Alphabetic,
    AlphanumericNoSpace,
    Alphanumeric,
    NoSpace,
    Numeric,
}

/// Terminal events
#[derive(Debug)]
pub enum Event {
    Quit,
    EnterScreen(Screen),
    EnterPopup(Option<Popup>),
    SwitchDiv,
    ToggleDisplayMsg,
    Resize,
    TimeoutTick(TimeoutType),
    KeyInput(KeyEvent, InputBlacklist),
    SwitchInput,
    NextInput,
    PrevInput,
    SwitchAction,
    SelectAction,

    NextListItem(ListType),
    PrevListItem(ListType),
    SelectListItem(ListType),

    NextTableItem(TableType),
    PrevTableItem(TableType),
    SelectTableItem(TableType),

    TryLogin,

    TryGetUserLocker(String, String),
    TryGetUserBranch(String, String),
    TryGetUserDelivery(String),
    PlaceOrderReq,

    UpdatePaymentInfo,
    PlaceOrder
}

#[derive(Debug)]
pub struct EventHandler {
    // Event sender channel
    #[allow(dead_code)]
    sender: mpsc::Sender<Event>,
    // Event receiver channel
    receiver: mpsc::Receiver<Event>,
    // Event handler thread
    #[allow(dead_code)]
    handler: thread::JoinHandle<()>
}

impl EventHandler {
    // Constructs a new instance of [`EventHandler`]
    pub fn new(tick_step: u16, app_arc: &Arc<Mutex<App>>) -> Self {
        let tick_rate = Duration::from_millis(tick_step as u64);
        let (sender, receiver) = mpsc::channel();
        let app_arc = Arc::clone(&app_arc);
        let handler = {
            let sender = sender.clone();
            thread::spawn(move || {
                let mut last_tick = Instant::now(); 
                loop {
                    if event::poll(Duration::from_millis(100)).unwrap() {
                        event_act(event::read().expect("unable to read event"), &sender, &app_arc);
                    }
                    
                    if last_tick.elapsed() >= tick_rate {
                        last_tick = Instant::now();
                        for (timeout_type, timer) in &app_arc.lock().unwrap().timeout {
                            if timer.last_update.elapsed() > timer.tick_rate {
                                sender.send(Event::TimeoutTick(*timeout_type)).expect(SENDER_ERR);
                            }
                        }
                    }
                }
            })
        };
        Self {
            sender,
            receiver,
            handler,
        }
    }

    /// Receive the next event from the handler thread
    ///
    /// This function will always block the current thread if
    /// there is no data available and it's possible for more data to be sent
    pub fn next(&self) -> Result<Event> {
        Ok(self.receiver.recv()?)
    }
}

fn event_act(event: CrosstermEvent, sender: &mpsc::Sender<Event>, app: &Arc<Mutex<App>>) {
    match event {
        CrosstermEvent::Key(key_event) => {
            if key_event.kind == KeyEventKind::Release { return; }

            {
                let app_lock = app.lock().unwrap();

                // Events common to all screens.
                match key_event.code {
                    KeyCode::Char('c') if key_event.modifiers == KeyModifiers::CONTROL => sender.send(Event::Quit),
                    _ if app_lock.display_msg => { sender.send(Event::ToggleDisplayMsg).expect(SENDER_ERR); return; },
                    _ => Ok(())
                }.expect(SENDER_ERR);
            }

            let curr_screen = app.lock().unwrap().active_screen.clone();

            // Screen-specific events.
            match curr_screen {
                Screen::Title => title::event_act(key_event, sender, app),
                Screen::Settings => settings::event_act(key_event, sender, app),
                Screen::Login => login::event_act(key_event, sender, app),
                Screen::Client(_) => client::event_act(key_event, sender, app),
                Screen::PkgAdmin(_) => pkgadmin::event_act(key_event, sender, app),
            }
        },
        CrosstermEvent::Resize(_, _) => {
            let mut app_lock = app.lock().unwrap();
            if !app_lock.timeout.contains_key(&TimeoutType::Resize) {
                app_lock.add_timeout(1, 250, TimeoutType::Resize);
                sender.send(Event::Resize).expect(SENDER_ERR);
            }
        },
        _ => {}
    }
}