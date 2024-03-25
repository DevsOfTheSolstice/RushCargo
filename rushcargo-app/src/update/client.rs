use std::sync::{Arc, Mutex};
use crossterm::event::{Event as CrosstermEvent, KeyCode};
use tui_input::backend::crossterm::EventHandler;
use sqlx::{Pool, Postgres};
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
        common::Screen,
    }
};

pub async fn update(app: &mut Arc<Mutex<App>>, pool: &Pool<Postgres>, event: Event) -> Result<()> {
    match event {
        Event::PlaceOrder => {
            Ok(())
        }
        _ => panic!("An event of type {:?} was passed to the list update function", event)
    }
}