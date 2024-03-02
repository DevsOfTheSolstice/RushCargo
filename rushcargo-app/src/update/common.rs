use std::sync::{Arc, Mutex};
use crossterm::event::{Event as CrosstermEvent};
use sqlx::{Pool, Postgres};
use anyhow::Result;
use crate::{
    HELP_TEXT,
    event::Event,
    model::app::App,
};

pub async fn update(app: &mut Arc<Mutex<App>>, pool: &Pool<Postgres>, event: Event) -> Result<()> {
    match event {
        Event::Quit => {
            app.lock().unwrap().should_quit = true;
            Ok(())
        },
        Event::TimeoutStep(timeout_type) => {
            app.lock().unwrap().update_timeout_counter(timeout_type);
            Ok(())
        }
        _ => panic!("An event of type {:?} was passed to the common update function", event)
    }
}