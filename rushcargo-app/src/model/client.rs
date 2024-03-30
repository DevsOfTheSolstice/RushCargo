use sqlx::{PgPool, FromRow};
use rust_decimal::Decimal;
use anyhow::{Result, anyhow};
use super::{
    common::{PackageData, PaymentData, GetDBErr},
    db_obj::{Branch, Country, Locker, Warehouse},
};

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
    pub packages: Option<PackageData>,
    pub get_db_err: Option<GetDBErr>,
    pub send_to_locker: Option<Locker>,
    pub send_to_client: Option<Client>,
    pub send_to_branch: Option<Branch>,
    pub getuser_fail_count: u8,
    pub send_payment: Option<PaymentData>,
    pub send_with_delivery: bool,
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