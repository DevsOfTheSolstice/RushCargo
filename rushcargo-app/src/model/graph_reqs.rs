use std::sync::{Arc, Mutex};
use sqlx::{Row, postgres::PgPool};
use anyhow::Result;
use serde::Deserialize;
use url::Url;
use reqwest::Client;
use crate::GRAPH_URL;
use super::{
    app::App,
    db_obj::ShippingGuideType,
    common::{User, Screen, SubScreen},
};

#[derive(Debug, Deserialize)]
pub struct WarehouseNode {
    pub id: i32,
    pub building: String,
    pub city: String,
    pub country: String,
    pub region: String,
}

#[derive(Debug, Deserialize)]
struct GraphResponse {
    distance: i64,
    nodes: Vec<WarehouseNode>,    
}

impl App {
    pub async fn get_shortest_warehouse_path(&mut self, pool: &PgPool) -> Result<()> {
        let (warehouse_to, warehouse_from, add_dist_from, add_dist_to) =
        match &mut self.user {
            Some(User::PkgAdmin(pkgadmin_data)) => {
                match self.active_screen {
                    Screen::PkgAdmin(SubScreen::PkgAdminAddPackage(_)) => {
                        let add_package = pkgadmin_data.add_package.as_mut().unwrap();
                        let shipping = add_package.shipping.as_ref().unwrap();
                        match shipping.shipping_type {
                            ShippingGuideType::InpersonBranch => {
                                let branch_to = shipping.branch.as_ref().unwrap();
                                (
                                    branch_to.warehouse.get_id(),
                                    pkgadmin_data.info.branch.warehouse.get_id(),
                                    pkgadmin_data.info.branch.route_distance,
                                    branch_to.route_distance,
                                )
                            }
                            ShippingGuideType::InpersonLocker => {
                                let locker_to = shipping.locker.as_ref().unwrap();
                                (
                                    locker_to.warehouse.get_id(),
                                    pkgadmin_data.info.branch.warehouse.get_id(),
                                    pkgadmin_data.info.branch.route_distance,
                                    0,
                                ) 
                            }
                            _ => unimplemented!()
                        }
                    }
                    Screen::PkgAdmin(SubScreen::PkgAdminGuideInfo) => {
                        let guide = pkgadmin_data.shipping_guides.as_ref().unwrap().active_guide.as_ref().unwrap();

                        let warehouse_from =
                            sqlx::query(
                                "
                                    SELECT * FROM shippings.lockers WHERE locker_id=$1
                                "
                            )
                            .bind(guide.locker_sender.unwrap())
                            .fetch_one(pool)
                            .await?
                            .try_get::<i32, _>("warehouse")?;

                        let warehouse_to =
                            match guide.shipping_type {
                                ShippingGuideType::LockerBranch =>
                                    sqlx::query(
                                        "
                                            SELECT * FROM locations.branches WHERE branch_id=$1
                                        "
                                    )
                                    .bind(guide.branch_receiver.unwrap())
                                    .fetch_one(pool)
                                    .await?
                                    .try_get::<i32, _>("warehouse_id")?,
                                ShippingGuideType::LockerLocker =>
                                    sqlx::query(
                                        "
                                            SELECT * FROM shippings.lockers WHERE locker_id=$1
                                        "
                                    )
                                    .bind(guide.locker_receiver.unwrap())
                                    .fetch_one(pool)
                                    .await?
                                    .try_get::<i32, _>("warehouse")?,
                                _ => unimplemented!()
                            };
                        
                        (warehouse_to, warehouse_from, 0, 0)
                   }
                    _ => unimplemented!()
                }
            }
            Some(User::Client(client_data)) => {
                let shipping = client_data.shipping.as_ref().unwrap();
                match shipping.shipping_type {
                    ShippingGuideType::LockerBranch => {
                        let branch = shipping.branch.as_ref().unwrap();
                        (
                            branch.warehouse.get_id(),
                            client_data.active_locker.as_ref().unwrap().warehouse.get_id(),
                            0,
                            branch.route_distance,
                        )
                    }
                    ShippingGuideType::LockerLocker => {
                        let locker = shipping.locker.as_ref().unwrap();
                        (
                            locker.warehouse.get_id(),
                            client_data.active_locker.as_ref().unwrap().warehouse.get_id(),
                            0,
                            0,
                        )
                    }
                    _ => unimplemented!()
                }
            }
            _ => unimplemented!()
        };

        let distance: &mut Option<i64> = &mut None;

        let (route, distance) =
        match &mut self.user {
            Some(User::PkgAdmin(pkgadmin_data)) => {
                match self.active_screen {
                    Screen::PkgAdmin(SubScreen::PkgAdminAddPackage(_)) => {
                        let add_package = pkgadmin_data.add_package.as_mut().unwrap();
                        (
                            &mut add_package.route,
                            &mut add_package.route_distance,
                        )
                    }
                    Screen::PkgAdmin(SubScreen::PkgAdminGuideInfo) => {
                        (
                            &mut pkgadmin_data.shipping_guides.as_mut().unwrap().active_guide_route,
                            distance,
                        )
                    }
                    _ => unimplemented!()
                }
            }
            Some(User::Client(client_data)) => {
                (
                    &mut client_data.send_route,
                    &mut client_data.send_route_distance,
                )
            }
            _ => unimplemented!()
        };

        let response = get_server_response(warehouse_from, warehouse_to).await?;

        if response.status().is_success() {
            let data = response.json::<GraphResponse>().await?;
            *route = Some(Vec::new());
            if let Some(route) = route {
                route.extend(data.nodes);
            }
            *distance = Some(data.distance + add_dist_from + add_dist_to);
        }

        Ok(())
    }
}

async fn get_server_response(warehouse_from: i32, warehouse_to: i32) -> Result<reqwest::Response> {
    let mut url = Url::parse(&GRAPH_URL.lock().unwrap()).expect("Invalid GRAPH_URL");

    url.query_pairs_mut()
        .append_pair("fromId", &warehouse_from.to_string())
        .append_pair("toId", &warehouse_to.to_string());

    let client = Client::new();
    Ok(client.get(url).send().await?)
}