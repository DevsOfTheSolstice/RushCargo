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

use anyhow::{Result, Error, anyhow};

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

#[derive(Debug)]
pub struct Client {
    pub username: String,
    pub first_name: String,
    pub last_name: String,
}

#[derive(Debug)]
pub struct ClientData {
    pub info: Client,
    pub viewing_lockers: Option<Vec<Locker>>,
    pub viewing_lockers_idx: i64,
    pub active_locker: Option<Locker>,
}

impl ClientData {
    pub async fn get_lockers_next(&mut self, pool: &PgPool) -> Result<()>{
        let query =
        "
            SELECT locker.*, country.*, warehouse.*,
            COUNT(package.tracking_number) AS package_count FROM locker
            LEFT JOIN package ON locker.locker_id=package.locker_id
            INNER JOIN country ON locker.country_id=country.country_id
            INNER JOIN warehouse ON locker.warehouse_id=warehouse.warehouse_id
            WHERE client=$1
            GROUP BY locker.locker_id, country.country_id, warehouse.warehouse_id
            ORDER BY package_count DESC
            LIMIT 7
            OFFSET $2
        ";

        let rows = 
            sqlx::query(query)
                .bind(&self.info.username)
                .bind(&self.viewing_lockers_idx)
                .fetch_all(pool)
                .await?;

        if rows.is_empty() { return Err(anyhow!("")) }
    
        let rows_num = rows.len();

        self.viewing_lockers = Some(
            rows
            .into_iter()
            .map(|row| Locker::from_row(&row).expect("could not build locker from row in get_lockers_next"))
            .collect::<Vec<Locker>>()
        );

        self.viewing_lockers_idx += rows_num as i64;

        Ok(())
    }
    pub async fn get_lockers_prev(&mut self, pool: &PgPool) -> Result<()> {
        let query =
        "
            SELECT locker.*, country.*, warehouse.*,
            COUNT(package.tracking_number) AS package_count FROM locker
            LEFT JOIN package ON locker.locker_id=package.locker_id
            INNER JOIN country ON locker.country_id=country.country_id
            INNER JOIN warehouse ON locker.warehouse_id=warehouse.warehouse_id
            WHERE client=$1
            GROUP BY locker.locker_id, country.country_id, warehouse.warehouse_id
            ORDER BY package_count DESC
            LIMIT 7
            OFFSET $2 - 7 * 2
        ";

        let rows =
            sqlx::query(query)
                .bind(&self.info.username)
                .bind(&self.viewing_lockers_idx)
                .fetch_all(pool)
                .await?;

        if rows.is_empty() { return Err(anyhow!("")) }
    
        self.viewing_lockers_idx -= self.viewing_lockers.as_ref().unwrap().len() as i64;

        self.viewing_lockers = Some(
            rows
            .into_iter()
            .map(|row| Locker::from_row(&row).expect("could not build locker from row in get_lockers_next"))
            .collect::<Vec<Locker>>()
        );

        Ok(())
    }
}