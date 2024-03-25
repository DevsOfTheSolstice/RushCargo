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
use time::{PrimitiveDateTime, Time, Date};
use rust_decimal::Decimal;
use anyhow::{Result, Error, anyhow};

#[derive(Debug, Clone, PartialEq)]
pub struct Package {
    pub tracking_num: i64,
    pub admin_verification: String,
    pub building_id: i64,
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

#[derive(Debug, Clone)]
pub struct Warehouse {
    id: i64
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
    id: i64,
    pub name: String,
    pub phone_prefix: String,
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