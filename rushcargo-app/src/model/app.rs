use std::collections::HashMap;
use std::time::{Duration, Instant};
use tui_input::Input;
use crate::{
    HELP_TEXT,
    model::{
        common::{Popup, UserType, InputFields, InputMode, Screen, TimeoutType, Timer}
    }
};

pub struct App {
    pub input: InputFields,
    pub input_mode: InputMode,
    pub failed_logins: u8,
    pub timeout: HashMap<TimeoutType, Timer>,
    pub active_user: Option<UserType>,
    pub active_screen: Screen,
    pub active_popup: Option<Popup>,
    pub hold_popup: bool,
    pub should_clear_screen: bool,
    pub should_quit: bool,
}

impl std::default::Default for App {
    fn default() -> Self {
        App {
            input: InputFields(Input::default(), Input::default()),
            input_mode: InputMode::Normal,
            failed_logins: 0,
            timeout: HashMap::new(),
            active_user: None,
            active_screen: Screen::Login,
            active_popup: None,
            hold_popup: false,
            should_clear_screen: false,
            should_quit: false,
        }
    }
}

impl App {
    pub fn enter_screen(&mut self, screen: &Screen) {
        self.should_clear_screen = true;
        match screen {
            Screen::Login => {
                self.active_screen = Screen::Login;
                self.input_mode = InputMode::Editing(0);
                self.failed_logins = 0;
                self.active_user = None;
            }
            _ => {}
        }
    }

    /// The timeout tick rate here should be equal or greater to the EventHandler tick rate.
    /// This is important because the minimum update time perceivable is defined by the EventHandler tick rate.
    pub fn add_timeout(&mut self, counter: u8, tick_rate: u16, timeout_type: TimeoutType) {
        if self.timeout.contains_key(&timeout_type) {
            panic!("cannot add timeout {:?} to list of timeouts since it already exists", timeout_type);
        }

        let tick_rate = Duration::from_millis(tick_rate as u64);

        self.timeout.insert(timeout_type, Timer{
            counter,
            tick_rate,
            last_update: Instant::now(),
        });
    }

    pub fn update_timeout_counter(&mut self, timeout_type: TimeoutType) {
        let timer = self.timeout.get_mut(&timeout_type)
            .unwrap_or_else(|| panic!("tried to update a nonexistent timeout"));

        if timer.counter > 1 {
            timer.counter -= 1;
            timer.last_update = Instant::now();
        } else {
            match timeout_type {
                TimeoutType::Login => self.failed_logins = 0,
                _ => {}
            }
            self.timeout.remove(&timeout_type);
        }
    }
}