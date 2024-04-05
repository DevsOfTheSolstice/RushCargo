use sqlx::{PgPool, Row, FromRow, postgres::PgRow};
use rust_decimal::Decimal;
use anyhow::{Result, anyhow};
use super::{
    common::{GetDBErr, PackageData, PaymentData, ShippingData}, db_obj::{Branch, Country, Locker, Warehouse}, graph_reqs::WarehouseNode
};

#[derive(Debug, Clone)]
pub struct Client {
    pub username: String,
    pub first_name: String,
    pub last_name: String,
    pub affiliated_branch: Branch,
}

impl<'r> FromRow<'r, PgRow> for Client {
    fn from_row(row: &'r PgRow) -> Result<Self, sqlx::Error> {
        Ok(Client {
            username: row.try_get("username")?,
            first_name: row.try_get("first_name")?,
            last_name: row.try_get("last_name")?,
            affiliated_branch: Branch::from_row(row)?,
        })
    }
}

#[derive(Debug)]
pub struct ClientData {
    pub info: Client,
    pub viewing_lockers: Option<Vec<Locker>>,
    pub viewing_lockers_idx: i64,
    pub active_locker: Option<Locker>,
    pub packages: Option<PackageData>,
    pub get_db_err: Option<GetDBErr>,
    pub send_route: Option<Vec<WarehouseNode>>,
    pub send_route_distance: Option<i64>,
    pub shipping: Option<ShippingData>,
    pub getuser_fail_count: u8,
    pub send_payment: Option<PaymentData>,
}

impl ClientData {
    pub async fn get_lockers_next(&mut self, pool: &PgPool) -> Result<()>{
        let query =
        "
            SELECT lockers.*, countries.*, warehouses.*,
            COUNT(packages.tracking_number) AS package_count FROM shippings.lockers AS lockers
            LEFT JOIN shippings.packages AS packages ON lockers.locker_id=packages.locker_id
            INNER JOIN locations.countries AS countries ON lockers.country=countries.country_id
            INNER JOIN locations.warehouses AS warehouses ON lockers.warehouse=warehouses.warehouse_id
            WHERE client=$1
            GROUP BY lockers.locker_id, countries.country_id, warehouses.warehouse_id
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
            SELECT lockers.*, countries.*, warehouses.*,
            COUNT(packages.tracking_number) AS package_count FROM shippings.lockers AS lockers
            LEFT JOIN shippings.packages AS packages ON lockers.locker_id=packages.locker_id
            INNER JOIN locations.countries AS countries ON lockers.country=countries.country_id
            INNER JOIN locations.warehouses AS warehouses ON lockers.warehouse=warehouses.warehouse_id
            WHERE client=$1
            GROUP BY lockers.locker_id, countries.country_id, warehouses.warehouse_id
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