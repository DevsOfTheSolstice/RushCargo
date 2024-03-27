//use sqlx::{FromRow, PgPool};

//use sqlx::{PgPool, FromRow};
#[derive(Debug)]

pub struct Trucker {
    pub username: String,
    pub truck: String,
}
#[derive(Debug)]
pub struct TruckerData{
   pub trucker: Trucker,

}
/* TRUCKER-ROUTES
impl TruckerData {
    pub async fn get_route_by_driver(&mut self, pool: &PgPool) -> Result<()>{
        let query: &str = 
        "SELECT * FROM warehouse_transfer_order
        WHERE truck_driver = $1
        ORDER BY order_number DESC"; 
    }
}
*/