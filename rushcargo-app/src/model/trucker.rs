use sqlx::{PgPool, FromRow};
use rust_decimal::Decimal;
use anyhow::{Result, anyhow};
use super::{
    common::{AutomaticOrdersData, GetDBErr, ShippingData, ShippingGuideData}, db_obj::{Branch, Country, Locker, Order, Warehouse}, graph_reqs::WarehouseNode
};

#[derive(Debug)]

pub struct Trucker {
    pub username: String,
    pub truck: String,
    pub affiliated_warehouse: Warehouse,
}

#[derive(Debug)]
pub struct TruckerData {
    pub info: Trucker,
    pub viewing_routes: Option<Vec<Order>>,
    pub viewing_routes_idx: i64,
    pub get_db_err: Option<GetDBErr>,
    pub active_wh_route: Option<AutomaticOrdersData>,
    pub shipping_guides: Option<ShippingGuideData>,

}

impl TruckerData {
    pub async fn get_orders_next(&mut self, pool: &PgPool) -> Result<()>{

        let query = 
        "
        SELECT warehouse_routes.*, branch_routes.*
        FROM Orders.Warehouse_Transfer_Orders AS warehouse_routes
        FULL OUTER JOIN Orders.Branch_Transfer_Order AS branch_routes
        ON warehouse_routes.order_number = branch_routes.order_number
        WHERE warehouse_routes.trucker = $1
        OR branch_routes.trucker = $1
        LIMIT 7
        OFFSET $2
        ";

        let rows = 
            sqlx::query(query)
                .bind(&self.info.username)
                .bind(&self.viewing_routes_idx)
                .fetch_all(pool)
                .await?;

        if rows.is_empty() { return Err(anyhow!("")) }

        let rows_num = rows.len();

        self.viewing_routes = Some(
            rows
            .into_iter()
            .map(|row| Order::from_row(&row).expect("cold not build from row in get_orders_next"))
            .collect::<Vec<Order>>()
        );

        self.viewing_routes_idx += rows_num as i64;

        Ok(())
    }

    pub async fn get_orders_prev(&mut self, pool: &PgPool) -> Result<()> {
        let query =
        "
        SELECT warehouse_routes.*, branch_routes.*
        FROM Orders.Warehouse_Transfer_Orders AS warehouse_routes
        FULL OUTER JOIN Orders.Branch_Transfer_Order AS branch_routes
        ON warehouse_routes.order_number = branch_routes.order_number
        WHERE warehouse_routes.trucker = $1
        OR branch_routes.trucker = $1
        LIMIT 7
        OFFSET $2 - 7 * 2
        ";

        let rows = 
            sqlx::query(query)
                .bind(&self.info.username)
                .bind(&self.viewing_routes_idx)
                .fetch_all(pool)
                .await?;
        
        if rows.is_empty() { return Err(anyhow!("")) }

        self.viewing_routes_idx -= self.viewing_routes.as_ref().unwrap().len() as i64;

        self.viewing_routes = Some(
            rows
            .into_iter()
            .map(|row| Order::from_row(&row).expect("cold not build from row in get_orders_next"))
            .collect::<Vec<Order>>()
        );

        Ok(())
    }
}
/* 
#[derive(Debug)]
pub struct AddOrderData {
    pub 
} */
/* EXAMPLE FROM ADMIN PACKAGE DATA
#[derive(Debug)]
pub struct AddPkgData {
    pub content: Input,
    pub value: Input,
    pub weight: Input,
    pub length: Input,
    pub width: Input,
    pub height: Input,
    pub client: Input,
    pub locker: Input,
    pub branch: Input,
    pub payment: Option<PaymentData>,
    pub shipping: Option<ShippingData>,
    pub route: Option<Vec<WarehouseNode>>,
    pub route_distance: Option<i64>,
}

impl std::default::Default for AddPkgData {
    fn default() -> Self {
        AddPkgData {
            content: Input::default(),
            value: Input::default(),
            weight: Input::default(),
            length: Input::default(),
            width: Input::default(),
            height: Input::default(),
            client: Input::default(),
            locker: Input::default(),
            branch: Input::default(),
            payment: None,
            shipping: None,
            route: None,
            route_distance: None,
        }
    }
}

impl AddPkgData {
    pub fn is_missing_attr(&self) -> bool {
        self.content.value().is_empty() ||
        self.value.value().is_empty() ||
        self.weight.value().is_empty() ||
        self.length.value().is_empty() ||
        self.width.value().is_empty() ||
        self.height.value().is_empty() ||
        self.client.value().is_empty() ||
        (self.locker.value().is_empty() &&
        self.branch.value().is_empty())
    }
}
*/

