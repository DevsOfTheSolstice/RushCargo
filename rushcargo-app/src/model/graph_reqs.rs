use std::sync::{Arc, Mutex};
use sqlx::{Row, postgres::PgPool};
use anyhow::Result;
use serde::Deserialize;
use url::Url;
use reqwest::Client;
use crate::GRAPH_URL;
use super::{
    app::App,
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
    pub async fn get_shortest_branch_branch(&mut self, pool: &PgPool) -> Result<()> {
        let (branch_to, branch_from, route, distance) =
        if let Some(User::PkgAdmin(pkgadmin_data)) = &mut self.user {
            match self.active_screen {
                Screen::PkgAdmin(SubScreen::PkgAdminAddPackage(_)) => {
                    let add_package = pkgadmin_data.add_package.as_mut().unwrap();
                    (
                        add_package.branch.value().parse::<i32>().expect("could not parse branch_to in graph_reqs.rs"),
                        pkgadmin_data.info.branch_id,
                        &mut add_package.route,
                        &mut add_package.route_distance,
                    )
                }
                _ => unimplemented!("get_shortest_branch_branch() for {:?}", self.active_screen)
            }
        } else {
            panic!()
        };

        let (add_distance_from, warehouse_from) = {
            let res = sqlx::query("SELECT * FROM locations.branches WHERE branch_id=$1")
                .bind(19)
                //.bind(branch_from)
                .fetch_one(pool)
                .await?;
            (
                res.try_get::<i64, _>("route_distance")?, res.try_get::<i32, _>("warehouse_id")?
            )
        };

        let (add_distance_to, warehouse_to) = {
            let res = sqlx::query("SELECT * FROM locations.branches WHERE branch_id=$1")
                .bind(branch_to)
                .fetch_one(pool)
                .await?;
            (
                res.try_get::<i64, _>("route_distance")?, res.try_get::<i32, _>("warehouse_id")?
            )                                                                                           
        };

        let response = get_server_response(warehouse_from, warehouse_to).await?;
        if response.status().is_success() {
            let data = response.json::<GraphResponse>().await?;
            *route = Some(Vec::new());
            if let Some(route) = route {
                route.extend(data.nodes);
            }
            *distance = Some(data.distance + add_distance_from + add_distance_to);
        }

        Ok(())
    }

    pub async fn get_shortest_locker_locker(&mut self, pool: &PgPool) -> Result<()> {
        let (warehouse_from, warehouse_to, route, distance) =
        if let Some(User::Client(client_data)) = &mut self.user {
            match self.active_screen {
                Screen::Client(SubScreen::ClientLockerPackages) => {
                    (
                        client_data.active_locker.as_ref().unwrap().warehouse.get_id(),
                        client_data.send_to_locker.as_ref().unwrap().warehouse.get_id(),
                        &mut client_data.send_route,
                        &mut client_data.send_route_distance,
                    )
                }
                _ => panic!()
            }
        }
        else {
            panic!()
        };

        let response = get_server_response(warehouse_from, warehouse_to).await?;
        if response.status().is_success() {
            let data = response.json::<GraphResponse>().await?;
            *route = Some(Vec::new());
            if let Some(route) = route {
                route.extend(data.nodes);
            }
            *distance = Some(data.distance);
        }

        Ok(())
    }

    pub async fn get_shortest_locker_branch(&mut self, pool: &PgPool) -> Result<()> {
        let (warehouse_from, branch_to, route, distance) = {
            if let Some(User::Client(client_data)) = &mut self.user {
                match self.active_screen {
                    Screen::Client(SubScreen::ClientLockerPackages) => {
                        (
                            client_data.active_locker.as_ref().unwrap().warehouse.get_id(),
                            client_data.send_to_branch.as_ref().unwrap().get_id(),
                            &mut client_data.send_route,
                            &mut client_data.send_route_distance,
                        )
                    }
                    _ => panic!()
                }
            } else {
                panic!();
            }
        };

        

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