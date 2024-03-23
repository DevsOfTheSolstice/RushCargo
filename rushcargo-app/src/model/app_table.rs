use ratatui::widgets::TableState;
use sqlx::PgPool;
use super::{
    app::App, common::User,
};

#[derive(Debug)]
pub enum TableType {
    Lockers,
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

impl App {
    pub async fn next_table_item(&mut self, table_type: TableType, pool: &PgPool) {
        match table_type {
            TableType::Lockers => {
                let client = self.user.as_mut().map(|u|
                    match u {
                        User::Client(client) => client,
                        _ => panic!()
                    }).unwrap();

                let i = match self.table.state.selected() {
                    Some(i) => {
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
        }
    }
    pub async fn prev_table_item(&mut self, table_type: TableType, pool: &PgPool) {
        match table_type {
            TableType::Lockers => {
                let client = self.user.as_mut().map(|u|
                    match u {
                        User::Client(client) => client,
                        _ => panic!()
                    }).unwrap();

                let i = match self.table.state.selected() {
                    Some(i) => {
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
        }
    }
}