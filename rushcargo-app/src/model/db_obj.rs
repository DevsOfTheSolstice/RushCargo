use sqlx::{
    database::HasValueRef,
    postgres::{PgRow, PgTypeInfo},
    Postgres,
    PgPool,
    Row,
    FromRow,
    Decode,
    Type,
};
use std::str::FromStr;
use time::{PrimitiveDateTime, Time, Date};
use rust_decimal::Decimal;
use anyhow::{Result, Error, anyhow};
use super::{
    client::Client,
    common::PaymentType,
};

#[derive(Debug, Clone, PartialEq)]
pub struct Package {
    pub tracking_num: i64,
    pub admin_verification: String,
    pub building_id: i32,
    pub shipping_num: Option<i64>,
    pub locker_id: Option<i64>,
    pub register_date: Date,
    pub register_hour: Time,
    pub content: String,
    pub value: Decimal,
    pub weight: Decimal,
    pub length: Decimal,
    pub width: Decimal,
    pub height: Decimal,
    pub delivered: bool,
}

impl<'r> FromRow<'r, PgRow> for Package {
    fn from_row(row: &'r PgRow) -> Result<Self, sqlx::Error> {
        Ok(Package {
            tracking_num: row.try_get("tracking_number")?,
            admin_verification: row.try_get("admin_verification")?,
            building_id: row.try_get("building_id")?,
            shipping_num: row.try_get("shipping_number")?,
            locker_id: row.try_get("locker_id")?,
            register_date: row.try_get("register_date")?,
            register_hour: row.try_get("register_hour")?,
            content: row.try_get("content")?,
            value: row.try_get("package_value")?,
            weight: row.try_get("package_weight")?,
            length: row.try_get("package_lenght")?,
            width: row.try_get("package_width")?,
            height: row.try_get("package_height")?,
            delivered: row.try_get("delivered")?,
        })
    }
}

impl Package {
    pub fn get_id(&self) -> i64 {
        self.tracking_num
    }
}

#[derive(Debug, Clone)]
pub enum ShippingGuideType {
    LockerLocker,
    LockerBranch,
    LockerDelivery,
    InpersonLocker,
    InpersonBranch,
    InpersonDelivery,
}

#[derive(Debug, Clone)]
pub struct ShippingGuide {
    pub shipping_num: i64,
    pub package_count: i64,
    pub sender: Client,
    pub recipient: Client,
    pub delivery_included: bool,
    pub locker_sender: Option<i64>,
    pub branch_sender: Option<i32>,
    pub locker_receiver: Option<i64>,
    pub branch_receiver: Option<i32>,
    pub shipping_type: ShippingGuideType,
}

impl std::fmt::Display for ShippingGuideType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}",
            match self {
                Self::LockerLocker =>
                    "Locker->Locker",
                Self::LockerBranch =>
                    "Locker->Branch",
                Self::LockerDelivery =>
                    "Locker->Delivery",
                Self::InpersonLocker =>
                    "In-person->Locker",
                Self::InpersonBranch =>
                    "In-person->Branch",
                Self::InpersonDelivery =>
                    "In-person->Delivery",
            }
        )
    }
}

impl<'r> FromRow<'r, PgRow> for ShippingGuide {
    fn from_row(row: &'r PgRow) -> std::prelude::v1::Result<Self, sqlx::Error> {
        let locker_sender: Option<i64> = row.try_get("locker_from")?;
        let branch_sender: Option<i32> = row.try_get("branch_from")?;
        let locker_receiver: Option<i64> = row.try_get("locker_to")?;
        let branch_receiver: Option<i32> = row.try_get("branch_to")?;
        let shipping_type =
            if let Some(_) = locker_sender {
                if let Some(_) = locker_receiver {
                    ShippingGuideType::LockerLocker
                } else if let Some(_) = branch_receiver {
                    ShippingGuideType::LockerBranch 
                } else {
                    ShippingGuideType::LockerDelivery
                }
            } else {
                if let Some(_) = locker_receiver {
                    ShippingGuideType::InpersonLocker
                } else if let Some(_) = branch_receiver {
                    ShippingGuideType::InpersonBranch
                } else {
                    ShippingGuideType::InpersonDelivery
                }
            };

        Ok(ShippingGuide {
            shipping_num: row.try_get("shipping_number")?,
            package_count: row.try_get("package_count")?,
            sender: Client {
                username: row.try_get("sender_username")?,
                affiliated_branch: Branch {
                    id: Building {
                        id: row.try_get("sender_building_id")?,
                        city_id: row.try_get("sender_building_city_id")?,
                        name: row.try_get("sender_building_name")?,
                        address_description: row.try_get("sender_building_address_description")?,
                        gps_latitude: row.try_get("sender_building_gps_latitude")?,
                        gps_longitude: row.try_get("sender_building_gps_longitude")?,
                        phone: row.try_get("sender_building_phone")?,
                        email: row.try_get("sender_building_email")?,
                    },
                    warehouse: Warehouse {
                        id: row.try_get("sender_branch_warehouse_id")?,
                    },
                    route_distance: row.try_get("sender_branch_route_distance")?,
                },
                first_name: row.try_get("sender_first_name")?,
                last_name: row.try_get("sender_last_name")?,
            },
            recipient: Client {
                username: row.try_get("receiver_username")?,
                affiliated_branch: Branch {
                    id: Building {
                        id: row.try_get("receiver_building_id")?,
                        city_id: row.try_get("receiver_building_city_id")?,
                        name: row.try_get("receiver_building_name")?,
                        address_description: row.try_get("receiver_building_address_description")?,
                        gps_latitude: row.try_get("receiver_building_gps_latitude")?,
                        gps_longitude: row.try_get("receiver_building_gps_longitude")?,
                        phone: row.try_get("receiver_building_phone")?,
                        email: row.try_get("receiver_building_email")?,
                    },
                    warehouse: Warehouse {
                        id: row.try_get("receiver_branch_warehouse_id")?,
                    },
                    route_distance: row.try_get("receiver_branch_route_distance")?,
                },
                first_name: row.try_get("receiver_first_name")?,
                last_name: row.try_get("receiver_last_name")?,
            },
            delivery_included: row.try_get("delivery_included")?,
            locker_sender,
            branch_sender,
            locker_receiver,
            branch_receiver,
            shipping_type,
        })
    }
}

impl ShippingGuide {
    pub fn get_id(&self) -> i64 {
        self.shipping_num
    }
}


#[derive(Debug)]
pub struct Payment {
    id: i64,
    pub client: String,
    pub transaction_id: String,
    pub platform: String,
    pub pay_type: PaymentType,
    pub pay_date: Date,
    pub pay_hour: Time,
    pub amount: Decimal,
}

impl<'r> FromRow<'r, PgRow> for Payment {
    fn from_row(row: &'r PgRow) -> std::prelude::v1::Result<Self, sqlx::Error> {
        Ok(Payment {
            id: row.try_get("id")?,
            client: row.try_get("client")?,
            transaction_id: row.try_get("reference")?,
            platform: row.try_get("platform")?,
            pay_type: PaymentType::from_str(row.try_get::<&str, _>("pay_type")?).expect("could not parse PayType from str"),
            pay_date: row.try_get("pay_date")?,
            pay_hour: row.try_get("pay_hour")?,
            amount: row.try_get("amount")?,
        })
    }
}

#[derive(Debug, Clone)]
pub struct Building {
    id: i32,
    pub city_id: i32,
    pub name: String,
    pub address_description: Option<String>,
    pub gps_latitude: Option<Decimal>,
    pub gps_longitude: Option<Decimal>,
    pub phone: Option<i64>,
    pub email: Option<String>,
}

impl<'r> FromRow<'r, PgRow> for Building {
    fn from_row(row: &'r PgRow) -> std::prelude::v1::Result<Self, sqlx::Error> {
        Ok(Building {
            id: row.try_get("building_id")?,
            city_id: row.try_get("city_id")?,
            name: row.try_get("building_name")?,
            address_description: row.try_get("address_description")?,
            gps_latitude: row.try_get("gps_latitude")?,
            gps_longitude: row.try_get("gps_longitude")?,
            phone: row.try_get("phone")?,
            email: row.try_get("email")?,
        })
    }
}

impl Building {
    pub fn get_id(&self) -> i32 {
        self.id
    }
}

#[derive(Debug, Clone)]
pub struct Branch {
    id: Building,
    pub warehouse: Warehouse,
    pub route_distance: i64,
}

impl<'r> FromRow<'r, PgRow> for Branch {
    fn from_row(row: &'r PgRow) -> std::prelude::v1::Result<Self, sqlx::Error> {
        Ok(Branch {
            id: Building::from_row(row)?,
            warehouse: Warehouse::from_row(row)?,
            route_distance: row.try_get("route_distance")?,
        })
    }
}

impl Branch {
    pub fn get_id(&self) -> i32 {
        self.id.get_id()
    }
}

#[derive(Debug, Clone)]
pub struct Warehouse {
    id: i32
}

impl Warehouse {
    pub fn get_id(&self) -> i32 {
        self.id
    }
}

impl<'r> FromRow<'r, PgRow> for Warehouse {
    fn from_row(row: &'r PgRow) -> Result<Self, sqlx::Error> {
        Ok(Warehouse {
            id: row.try_get("warehouse_id")?
        })
    }
}

#[derive(Debug, Clone)]
pub struct Country {
    id: i16,
    pub name: String,
    pub phone_prefix: i16,
}

impl<'r> FromRow<'r, PgRow> for Country {
    fn from_row(row: &'r PgRow) -> Result<Self, sqlx::Error> {
        Ok(Country {
            id: row.try_get("country_id")?,
            name: row.try_get("country_name")?,
            phone_prefix: row.try_get("phone_prefix")?, 
        })
    }
}

#[derive(Debug, Clone)]
pub struct Locker {
    id: i64,
    pub package_count: i64,
    pub country: Country,
    pub warehouse: Warehouse,
}

impl<'r> FromRow<'r, PgRow> for Locker {
    fn from_row(row: &'r PgRow) -> Result<Self, sqlx::Error> {
        Ok(Locker {
            id: row.try_get("locker_id")?,
            package_count: row.try_get("package_count")?,
            country: Country::from_row(row)?,
            warehouse: Warehouse::from_row(row)?, 
        })
    }
}

impl Locker {
    pub fn get_id(&self) -> i64 {
        self.id
    }
}

pub struct BranchTransferOrderSmall {
    pub order_number: i64,
    pub trucker: String,
    pub shipping_number: i64,
    pub warehouse: Warehouse,
    pub branch: i64,
    pub withdrawal: bool,
    pub rejected: bool,
}