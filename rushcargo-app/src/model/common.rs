use std::time::{Duration, Instant};
use tui_input::Input;
use rust_decimal::Decimal;
use super::{
    client::ClientData,
    common_obj::{Locker, Package},
    trucker::TruckerData
};


#[derive(Debug, Clone)]
pub enum Screen {
    Title,
    Settings,
    Login,
    Client(SubScreen),
    Trucker(SubScreen),
}

#[derive(Debug, Clone)]
pub enum SubScreen {
    ClientMain,
    ClientLockers,
    ClientLockerPackages,
    ClientSentPackages,


    TruckerMain,
    TruckerStatistics,
    TruckerManagementPackets,
    TruckerRoutes
}

impl std::fmt::Display for Screen {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}",
            match self {
                Screen::Title => "Title",
                Screen::Settings => "Settings",
                Screen::Login => "Login",
                Screen::Client(_) => "Client",
                Screen::Trucker(_) => "Trucker"
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
    Trucker(TruckerData),
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