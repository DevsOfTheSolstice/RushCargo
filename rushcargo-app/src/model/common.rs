use std::time::{Duration, Instant};
use tui_input::Input;
use super::client::ClientData;

#[derive(Debug, Clone)]
pub enum Screen {
    Title,
    Settings,
    Login,
    Client(SubScreen),
    Trucker,
}

#[derive(Debug, Clone)]
pub enum SubScreen {
    ClientMain,
    ClientLockers,
    ClientLockerPackages,
    ClientSentPackages,
}

impl std::fmt::Display for Screen {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}",
            match self {
                Screen::Title => "Title",
                Screen::Settings => "Settings",
                Screen::Login => "Login",
                Screen::Client(_) => "Client",
                Screen::Trucker => "Trucker"
            }
        )
    }
}

pub enum Popup {
    LoginSuccessful,
}

#[derive(Debug)]
pub enum User {
    Client(ClientData),
}

#[derive(Debug)]
pub enum UserType {
    NaturalClient,
    LegalClient,
    Trucker,
    Motorcyclist,
    OrderAdmin,
    ClientAdmin,
    PackageAdmin,
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