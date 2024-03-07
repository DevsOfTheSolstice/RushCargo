use std::time::{Duration, Instant};
use tui_input::Input;

#[derive(Debug, Clone)]
pub enum Screen {
    Title,
    Settings,
    Login,
    Trucker,
}

impl std::fmt::Display for Screen {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}",
            match self {
                Screen::Title => "Title",
                Screen::Settings => "Settings",
                Screen::Login => "Login",
                Screen::Trucker => "Trucker"
            }
        )
    }
}

pub enum Popup {
    LoginSuccessful,
}

pub enum UserType {
    Trucker,
    MotorcycleCourier,
    NaturalClient,
    LegalClient,
}

pub enum InputMode {
    Normal,
    /// The value represents the InputField being edited
    Editing(u8),
}

pub struct InputFields(pub Input, pub Input);

#[derive(Eq, PartialEq, Hash, Debug, Clone, Copy)]
pub enum TimeoutType {
    Resize,
    CubeTick,
    Login,
}

pub struct Timer {
    pub counter: u8,
    pub tick_rate: Duration,
    pub last_update: Instant,
}