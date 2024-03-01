use std::collections::HashMap;
use crate::{
    HELP_TEXT,
    model::{
        common::{Screen, TimeoutType, Timer}
    }
};

pub struct App {
    pub timeout: HashMap<TimeoutType, Timer>,
    pub active_screen: Screen,
    pub should_clear_screen: bool,
    pub should_quit: bool,
}

impl std::default::Default for App {
    fn default() -> Self {
        App {
            timeout: HashMap::new(),
            active_screen: Screen::Login,
            should_clear_screen: false,
            should_quit: false,
        }
    }
}

impl App {
    pub fn enter_screen(&mut self, screen: &Screen) {
        self.should_clear_screen = true;
        match screen {
            _ => {}
        }
    }
}