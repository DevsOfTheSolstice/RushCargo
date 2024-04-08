use ratatui::widgets::TableState;
use sqlx::{FromRow, query::Query, Postgres, PgPool};
use anyhow::{Result, anyhow};
use super::{
    app::App,
    common::{Screen, SubScreen, User},
    db_obj::{Package, ShippingGuide}, pkgadmin
};

#[derive(Debug)]
pub enum TableType {
    Lockers,
    LockerPackages,
    
    Guides,
    GuidePackages,

    ManagementPackages,
    TruckerRoutes,
    StatsYear,
    StatsMonth,
    StatsDay,
}

pub struct TableData {
    pub state: TableState,
}

impl std::default::Default for TableData {
    fn default() -> Self {
        TableData {
            state: TableState::default(),
        }
    }
}

const GUIDES_QUERY: &'static str =
"
    SELECT guides.*,
    sender.username AS sender_username, sender.first_name AS sender_first_name, sender.last_name AS sender_last_name,
    receiver.username AS receiver_username, receiver.first_name AS receiver_first_name, receiver.last_name AS receiver_last_name,
    sender_branch.branch_id AS sender_branch_id, sender_branch.route_distance AS sender_branch_route_distance, sender_branch.warehouse_id AS sender_branch_warehouse_id,
    sender_building.building_id AS sender_building_id, sender_building.building_name AS sender_building_name, sender_building.address_description AS sender_building_address_description,
    sender_building.gps_latitude AS sender_building_gps_latitude, sender_building.gps_longitude AS sender_building_gps_longitude,
    sender_building.email AS sender_building_email, sender_building.phone AS sender_building_phone, sender_building.city_id AS sender_building_city_id,
    receiver_branch.branch_id AS receiver_branch_id, receiver_branch.route_distance AS receiver_branch_route_distance, receiver_branch.warehouse_id AS receiver_branch_warehouse_id,
    receiver_building.building_id AS receiver_building_id, receiver_building.building_name AS receiver_building_name, receiver_building.address_description AS receiver_building_address_description,
    receiver_building.gps_latitude AS receiver_building_gps_latitude, receiver_building.gps_longitude AS receiver_building_gps_longitude,
    receiver_building.email AS receiver_building_email, receiver_building.phone AS receiver_building_phone, receiver_building.city_id AS receiver_building_city_id,
    COUNT(packages.tracking_number) AS package_count
    FROM shippings.shipping_guides AS guides
    LEFT JOIN shippings.packages AS packages ON guides.shipping_number=packages.shipping_number
    INNER JOIN users.natural_clients AS sender ON guides.client_from=sender.username
    INNER JOIN users.natural_clients AS receiver ON guides.client_to=receiver.username
    INNER JOIN locations.branches AS sender_branch ON sender.affiliated_branch=sender_branch.branch_id
    INNER JOIN locations.buildings AS sender_building ON sender_branch.branch_id=sender_building.building_id
    INNER JOIN locations.branches AS receiver_branch ON receiver.affiliated_branch=receiver_branch.branch_id
    INNER JOIN locations.buildings AS receiver_building ON receiver_branch.branch_id=receiver_building.building_id
    WHERE shipping_date IS NULL AND shipping_hour IS NULL
    GROUP BY guides.shipping_number, sender.username, receiver.username, sender_building.building_id, sender_branch_id, receiver_building.building_id, receiver_branch_id
    ORDER BY package_count DESC
    LIMIT 7
";

impl App {
    pub async fn next_table_item(&mut self, table_type: TableType, pool: &PgPool) {
        match table_type {
            TableType::Lockers => {
                let i = match self.table.state.selected() {
                    Some(i) => {
                        let client = self.get_client_mut();
                        if i >= client.viewing_lockers.as_ref().unwrap().len() - 1 {
                            if let Ok(()) = client.get_lockers_next(pool).await {
                                0
                            } else {
                                return;
                            }
                        } else {
                            i + 1
                        }
                    }
                    None => 0,
                };
                self.table.state.select(Some(i));
            }
            TableType::LockerPackages | TableType::GuidePackages => {
                let i = match self.table.state.selected() {
                    Some(i) => {
                        if i >= self.get_packages_ref().viewing_packages.len() - 1 {
                            if let Ok(()) = self.get_packages_next(table_type, pool).await {
                                0
                            } else {
                                return;
                            }
                        } else {
                            i + 1
                        }
                    }
                    None => 0
                };
                self.table.state.select(Some(i));

                let packages = self.get_packages_mut();

                packages.active_package = Some(packages.viewing_packages[i].clone());
            }
            TableType::Guides => {
                let i = match self.table.state.selected() {
                    Some(i) => {
                        if i >= self.get_pkgadmin_guides_ref().viewing_guides.len() - 1 {
                            if let Ok(()) = self.get_guides_next(table_type, pool).await {
                                0
                            } else {
                                return;
                            }
                        } else {
                            i + 1
                        }
                    }
                    None => 0,
                };
                self.table.state.select(Some(i));
            }
            TableType::TruckerRoutes => {
                let i = match self.table.state.selected() {
                    Some(i) => {
                        if i >= self.get_trucker_guides_ref().viewing_guides.len() - 1 {
                            if let Ok(()) = self.get_guides_next(table_type, pool).await {
                                0
                            } else {
                                return;
                            }
                        } else {
                            i + 1
                        }
                    }
                    None => 0,
                };
                self.table.state.select(Some(i));
            }
            TableType::ManagementPackages => {
                let i = match self.table.state.selected() {
                    Some(i) => {
                        if i >= self.get_trucker_guides_ref().viewing_guides.len() - 1 {
                            if let Ok(()) = self.get_guides_next(table_type, pool).await {
                                0
                            } else {
                                return;
                            }
                        } else {
                            i + 1
                        }
                    }
                    None => 0,
                };
                self.table.state.select(Some(i));                
            }
            TableType::StatsYear => {

            }
            TableType::StatsMonth => {

            }
            TableType::StatsDay => {

            }
        }
    }
    pub async fn prev_table_item(&mut self, table_type: TableType, pool: &PgPool) {
        match table_type {
            TableType::Lockers => {
                let i = match self.table.state.selected() {
                    Some(i) => {
                        let client = self.get_client_mut();
                        if i == 0 {
                            if let Ok(()) = client.get_lockers_prev(pool).await {
                                7 - 1
                            } else {
                                return;
                            }
                        } else {
                            i - 1
                        }
                    }
                    None => 0,
                };
                self.table.state.select(Some(i));
            }
            TableType::LockerPackages | TableType::GuidePackages => {
                let i = match self.table.state.selected() {
                    Some(i) => {
                        if i == 0 {
                            if let Ok(()) = self.get_packages_prev(table_type, pool).await {
                                7 - 1
                            } else {
                                return;
                            }
                        } else {
                            i - 1
                        }
                    }
                    None => 0
                };
                self.table.state.select(Some(i));

                let packages = self.get_packages_mut();

                packages.active_package = Some(packages.viewing_packages[i].clone());
            }
            TableType::Guides => {
                let i = match self.table.state.selected() {
                    Some(i) => {
                        if i == 0 {
                            if let Ok(()) = self.get_guides_prev(table_type, pool).await {
                                7 - 1
                            } else {
                                return;
                            }
                        } else {
                            i - 1
                        }
                    }
                    None => 0,
                };
                self.table.state.select(Some(i));
            }
            TableType::TruckerRoutes => {
                let i = match self.table.state.selected() {
                    Some(i) => {
                        if i == 0 {
                            if let Ok(()) = self.get_guides_prev(table_type, pool).await {
                                7 - 1
                            } else {
                                return;
                            }
                        } else {
                            i - 1
                        }
                    }
                    None => 0,
                };
                self.table.state.select(Some(i));                
            }
            TableType::ManagementPackages => {
                let i = match self.table.state.selected() {
                    Some(i) => {
                        if i == 0 {
                            if let Ok(()) = self.get_guides_prev(table_type, pool).await {
                                7 - 1
                            } else {
                                return;
                            }
                        } else {
                            i - 1
                        }
                    }
                    None => 0,
                };
                self.table.state.select(Some(i));
            }
            TableType::StatsYear | TableType::StatsMonth | TableType::StatsDay => {
                
            }
        }
    }
    pub async fn get_packages_next(&mut self, table_type: TableType, pool: &PgPool) -> Result<()> {
        let query: Query<'_, Postgres, _> = match table_type {
            TableType::LockerPackages => {
                match self.active_screen {
                    Screen::Client(SubScreen::ClientLockerPackages) => {
                        let client = self.get_client_ref();
                        let base_query =
                            "
                                SELECT * FROM shippings.packages AS packages
                                INNER JOIN shippings.package_descriptions AS descriptions
                                ON packages.tracking_number=descriptions.tracking_number
                                WHERE delivered=true AND locker_id=$1
                                LIMIT 7
                                OFFSET $2
                            ";

                        let query: Query<'_, Postgres, _> =
                            sqlx::query(base_query)
                            .bind(client.active_locker.as_ref().unwrap().get_id())
                            .bind(self.get_packages_ref().viewing_packages_idx);

                        query
                    }
                    _ => panic!()
                }
            }
            TableType::GuidePackages => {
                match self.active_screen {
                    Screen::PkgAdmin(SubScreen::PkgAdminGuideInfo) => {
                        let guide = self.get_pkgadmin_guides_ref().active_guide.as_ref().unwrap();
                        let base_query =
                            "
                                SELECT * FROM shippings.packages AS packages
                                INNER JOIN shippings.package_descriptions AS descriptions
                                ON packages.tracking_number=descriptions.tracking_number
                                WHERE shipping_number=$1
                                LIMIT 7
                                OFFSET $2
                            ";

                        let query: Query<'_, Postgres, _> =
                            sqlx::query(base_query)
                            .bind(guide.get_id())
                            .bind(self.get_packages_ref().viewing_packages_idx);

                        query
                    }
                    _ => panic!()
                }
            }
            _ => panic!()
        };

        let rows =
            query
            .fetch_all(pool)
            .await?;

        if rows.is_empty() { return Err(anyhow!("")) }

        let rows_num = rows.len();

        let packages = self.get_packages_mut();

        packages.viewing_packages =
            rows
            .into_iter()
            .map(|row| Package::from_row(&row).expect("could not build package from row in get_packages_next"))
            .collect::<Vec<Package>>();
        
        packages.viewing_packages_idx += rows_num as i64;

        Ok(())
    }
    pub async fn get_packages_prev(&mut self, table_type: TableType, pool: &PgPool) -> Result<()> {
        let query: Query<'_, Postgres, _> = match table_type {
            TableType::LockerPackages => {
                match self.active_screen {
                    Screen::Client(SubScreen::ClientLockerPackages) => {
                        let client = self.get_client_ref();
                        let base_query =
                            "
                                SELECT * FROM shippings.packages AS packages
                                INNER JOIN shippings.package_descriptions AS descriptions
                                ON packages.tracking_number=descriptions.tracking_number
                                WHERE delivered=true AND locker_id=$1
                                LIMIT 7
                                OFFSET $2 - 7 * 2
                            ";

                        let query: Query<'_, Postgres, _> =
                            sqlx::query(base_query)
                            .bind(client.active_locker.as_ref().unwrap().get_id())
                            .bind(self.get_packages_ref().viewing_packages_idx);

                        query
                    }
                    _ => panic!()
                }
            }
            TableType::GuidePackages => {
                match self.active_screen {
                    Screen::PkgAdmin(SubScreen::PkgAdminGuideInfo) => {
                        let guide = self.get_pkgadmin_guides_ref().active_guide.as_ref().unwrap();
                        let base_query =
                            "                                                                                  
                                SELECT * FROM shippings.packages AS packages
                                INNER JOIN shippings.package_descriptions AS descriptions
                                ON packages.tracking_number=descriptions.tracking_number
                                WHERE shipping_number=$1
                                LIMIT 7
                                OFFSET $2 - 7 * 2
                            ";

                        let query: Query<'_, Postgres, _> =
                            sqlx::query(base_query)
                            .bind(guide.get_id())
                            .bind(self.get_packages_ref().viewing_packages_idx);

                        query
                    }
                    _ => panic!()
                }
            }
            _ => panic!()
        };

        let rows =
            query
            .fetch_all(pool)
            .await?;

        if rows.is_empty() { return Err(anyhow!("")) }

        let packages = self.get_packages_mut();

        packages.viewing_packages_idx -= packages.viewing_packages.len() as i64;

        packages.viewing_packages =
            rows
            .into_iter()
            .map(|row| Package::from_row(&row).expect("could not build package from row in get_packages_next"))
            .collect::<Vec<Package>>();

        Ok(())
    }
    pub async fn get_guides_next(&mut self, table_type: TableType, pool: &PgPool) -> Result<()> {
        let base_query = match self.active_screen {
            Screen::PkgAdmin(SubScreen::PkgAdminGuides) =>
                GUIDES_QUERY.to_string() + " OFFSET $1",
            _ =>
                panic!()
        };

        let query: Query<'_, Postgres, _> = match table_type {
            TableType::Guides => {
                match self.active_screen {
                    Screen::PkgAdmin(SubScreen::PkgAdminGuides) => {
                        
                        let query: Query<'_, Postgres, _> =
                            sqlx::query(base_query.as_str())
                            .bind(self.get_pkgadmin_guides_ref().viewing_guides_idx);

                        let _ = base_query.clone();

                        query
                    }
                    _ => panic!()
                }
            }
            _ => panic!()
        };

        let rows =
            query
            .fetch_all(pool)
            .await.expect("get_guides_next() err");

        if rows.is_empty() { return Err(anyhow!("")) }

        let rows_num = rows.len();

        let guides = match self.user {
            Some(User::PkgAdmin(_)) => self.get_pkgadmin_guides_mut(),
            Some(User::Trucker(_)) => self.get_trucker_guides_mut(),
            _ => panic!()
        };

        guides.viewing_guides =
            rows
            .into_iter()
            .map(|row| ShippingGuide::from_row(&row).expect("could not build shipping guide from row in get_guides_next"))
            .collect::<Vec<ShippingGuide>>();

        guides.viewing_guides_idx += rows_num as i64;

        Ok(())
    }
    pub async fn get_guides_prev(&mut self, table_type: TableType, pool: &PgPool) -> Result<()> {
        let base_query = match self.active_screen {
            Screen::PkgAdmin(SubScreen::PkgAdminGuides) =>
                GUIDES_QUERY.to_string() + " OFFSET $1 - 7 * 2",
            _ =>
                panic!()
        };

        let query: Query<'_, Postgres, _> = match table_type {
            TableType::Guides => {
                match self.active_screen {
                    Screen::PkgAdmin(SubScreen::PkgAdminGuides) => {
                        let query: Query<'_, Postgres, _> =
                            sqlx::query(&base_query)
                            .bind(self.get_pkgadmin_guides_ref().viewing_guides_idx);

                        query
                    }
                    _ => panic!()
                }
            }
            _ => panic!()
        };

        let rows =
            query
            .fetch_all(pool)
            .await?;

        if rows.is_empty() { return Err(anyhow!("")) }

        let guides = match self.user {
            Some(User::PkgAdmin(_)) => self.get_pkgadmin_guides_mut(),
            Some(User::Trucker(_)) => self.get_trucker_guides_mut(),
            _ => panic!()
        };

        guides.viewing_guides_idx -= guides.viewing_guides.len() as i64;

        guides.viewing_guides =
            rows
            .into_iter()
            .map(|row| ShippingGuide::from_row(&row).expect("could not build package from row in get_guides_next"))
            .collect::<Vec<ShippingGuide>>();

        Ok(())
    }
}