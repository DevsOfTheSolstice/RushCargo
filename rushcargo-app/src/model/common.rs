use std::time::{Duration, Instant};
use tui_input::Input;
use rust_decimal::Decimal;
use super::{
    client::ClientData,
    common_obj::{Package, Locker},
};

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

#[derive(Debug, Clone)]
pub enum Popup {
    Prev,
    OrderSuccessful,

    LoginSuccessful,

    ClientOrderMain,
    ClientOrderLocker,
    ClientOrderBranch,
    ClientOrderDelivery,
    ClientInputPayment,
}

#[derive(Debug)]
pub enum User {
    Client(ClientData),
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

#[derive(Debug)]
pub struct PackageData {
    pub viewing_packages: Vec<Package>,
    pub viewing_packages_idx: i64,
    pub selected_packages: Option<Vec<Package>>,
    pub active_package: Option<Package>,
}

#[derive(Debug)]
pub enum Bank {
    PayPal,
    BOFA,
    AmazonPay,
}

impl std::fmt::Display for Bank {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            Bank::PayPal => write!(f, "PayPal"),
            Bank::BOFA => write!(f, "BOFA"),
            Bank::AmazonPay => write!(f, "AmazonPay"),
        }
    }
}

#[derive(Debug)]
pub struct PaymentData {
    pub amount: Decimal,
    pub transaction_id: String,
    pub bank: Bank,
}