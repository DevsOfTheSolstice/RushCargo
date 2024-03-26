use std::sync::{Arc, Mutex};
use crossterm::event::{Event as CrosstermEvent, KeyCode};
use tui_input::backend::crossterm::EventHandler;
use sqlx::PgPool;
use ratatui::widgets::ListItem;
use ratatui::prelude::Style;
use std::io::Write;
use std::fs::File;
use anyhow::Result;
use crate::{
    HELP_TEXT,
    BIN_PATH,
    event::{Event, InputBlacklist},
    model::{
        app::App,
        app_list::ListType,
        app_table::TableType,
        common::{User, SubScreen, Screen},
    }
};

pub async fn update(app: &mut Arc<Mutex<App>>, pool: &PgPool, event: Event) -> Result<()> {
    match event {
        Event::NextTableItem(table_type) => {
            let mut app_lock = app.lock().unwrap();

            app_lock.next_table_item(table_type, pool).await;

            Ok(())
        }
        Event::PrevTableItem(table_type) => {
            let mut app_lock = app.lock().unwrap();

            app_lock.prev_table_item(table_type, pool).await;

            Ok(())
        }
        Event::SelectTableItem(table_type) => {
            let mut app_lock = app.lock().unwrap();

            match table_type {
                TableType::Lockers => {
                    if let Some(selection) = app_lock.table.state.selected().clone() {
                        let client = app_lock.get_client_mut();
                        client.active_locker = Some(client.viewing_lockers.as_ref().unwrap()[selection].clone());
                        app_lock.enter_screen(Screen::Client(SubScreen::ClientLockerPackages), pool).await;
                    }
                }
                TableType::LockerPackages => {
                    let packages = app_lock.get_client_packages_mut();
                    if let Some(active_package) = &packages.active_package {
                        match &mut packages.selected_packages {
                            Some(selected_packages) => {
                                if selected_packages.contains(&active_package) {
                                    selected_packages.remove(
                                        selected_packages.iter().position(|x| *x == *active_package
                                    ).expect("package not found in selection"));
                                } else {
                                    selected_packages.push(active_package.clone());
                                }
                            }
                            None => packages.selected_packages = Some(Vec::from([active_package.clone()]))
                        }
                    }
                }
            }
            Ok(())
        }
        _ => panic!("An event of type {:?} was passed to the table update function", event)
    }
}