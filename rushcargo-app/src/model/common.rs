use std::{
    str::FromStr,
    time::{Duration, Instant},
};
use tui_input::Input;
use rust_decimal::Decimal;
use super::{
    client::{Client, ClientData},
    graph_reqs::WarehouseNode,
    db_obj::{Branch, Locker, Package, Payment, ShippingGuide, ShippingGuideType},
    pkgadmin::PkgAdminData
};

#[derive(Debug, Clone)]
pub enum Screen {
    Title,
    Settings,
    Login,
    Client(SubScreen),
    PkgAdmin(SubScreen),
}

#[derive(Debug, Clone)]
pub enum SubScreen {
    ClientMain,
    ClientLockers,
    ClientLockerPackages,
    ClientSentPackages,

    PkgAdminMain,
    PkgAdminGuides,
    PkgAdminGuideInfo,
    PkgAdminAddPackage(Div),
}

#[derive(Debug, Clone)]
pub enum Div {
    Left,
    Right
}

impl std::fmt::Display for Screen {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}",
            match self {
                Screen::Title => "Title",
                Screen::Settings => "Settings",
                Screen::Login => "Login",
                Screen::Client(_) => "Client",
                Screen::PkgAdmin(_) => "Package Admin",
            }
        )
    }
}

#[derive(Debug, Clone)]
pub enum Popup {
    Prev,
    OrderSuccessful,
    DisplayMsg,
    OnlinePayment,

    LoginSuccessful,
    ServerUnavailable,

    ClientOrderMain,
    ClientOrderLocker,
    ClientOrderBranch,
    ClientOrderDelivery,

    FieldExcess,
    SelectPayment,
    CashPayment,
    CardPayment,
}

#[derive(Debug)]
pub enum UserType {
    Client,
    PkgAdmin
}

#[derive(Debug)]
pub enum User {
    Client(ClientData),
    PkgAdmin(PkgAdminData),
}

#[derive(Clone)]
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
    GetUserDelivery,
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

impl std::default::Default for PackageData {
    fn default() -> Self {
        PackageData {
            viewing_packages: Vec::new(),
            viewing_packages_idx: 0,
            selected_packages: None,
            active_package: None,
        }
    }
}

#[derive(Debug)]
pub struct ShippingGuideData {
    pub viewing_guides: Vec<ShippingGuide>,
    pub viewing_guides_idx: i64,
    pub active_guide: Option<ShippingGuide>,
    pub active_guide_payment: Option<Payment>,
    pub active_guide_route: Option<Vec<WarehouseNode>>,
}

impl std::default::Default for ShippingGuideData {
    fn default() -> Self {
        ShippingGuideData {
            viewing_guides: Vec::new(),
            viewing_guides_idx: 0,
            active_guide: None,
            active_guide_payment: None,
            active_guide_route: None,
        }
    }
}

#[derive(Debug, Clone)]
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

#[derive(Debug, Clone)]
pub enum PaymentType {
    Online(Bank),
    Card,
    Cash
}

impl FromStr for PaymentType {
    type Err = std::fmt::Error;

    fn from_str(s: &str) -> std::prelude::v1::Result<Self, Self::Err> {
        match s {
            "Cash" => Ok(PaymentType::Cash),
            "Card" => Ok(PaymentType::Card),
            "Online: PayPal" => Ok(PaymentType::Online(Bank::PayPal)),
            "Online: AmazonPay" => Ok(PaymentType::Online(Bank::AmazonPay)),
            "Online: BOFA" => Ok(PaymentType::Online(Bank::BOFA)),
            _ => Err(std::fmt::Error),
        }
    }
}

impl std::fmt::Display for PaymentType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}",
            match self {
                Self::Cash => "Cash",
                Self::Card => "Card",
                Self::Online(bank) =>
                    match bank {
                        Bank::PayPal => "Online: PayPal",
                        Bank::AmazonPay => "Online: AmazonPay",
                        Bank::BOFA => "Online: BOFA"
                    }
            }
        )
    }
}
#[derive(Debug, Clone)]
pub struct PaymentData {
    pub amount: Decimal,
    pub transaction_id: Option<String>,
    pub payment_type: Option<PaymentType>,
}

#[derive(Debug)]
pub struct ShippingData {
    pub locker: Option<Locker>,
    pub branch: Option<Branch>,
    pub delivery: bool,
    pub client_from: Client,
    pub client_to: Client,
    pub shipping_type: ShippingGuideType,
}

#[derive(Debug, Clone)]
pub enum GetDBErr {
    LockerSameAsActive,
    InvalidUserLocker,
    LockerTooManyPackages,
    LockerWeightTooBig(Decimal),

    InvalidUserBranch,

    InvalidUserDelivery(u8),
    NoCompatBranchDelivery,
}