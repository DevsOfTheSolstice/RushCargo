use std::sync::{Arc, Mutex};
use crossterm::event::{Event as CrosstermEvent, KeyCode};
use tui_input::backend::crossterm::EventHandler;
use sqlx::{Pool, Postgres};
use ratatui::widgets::ListItem;
use ratatui::prelude::Style;
use anyhow::Result;
use crate::{
    HELP_TEXT,
    event::{Event, InputBlacklist},
    model::{
        app::App,
        app_list::ListType,
        common::Screen,
    }
};

pub async fn update(app: &mut Arc<Mutex<App>>, pool: &Pool<Postgres>, event: Event) -> Result<()> {
    match event {
        Event::PrevListItem(list_type) => {
            app.lock().unwrap().prev_list_item(list_type);
            Ok(())
        }
        Event::NextListItem(list_type) => {
            app.lock().unwrap().next_list_item(list_type);
            Ok(())
        }
        Event::SelectAction(list_type) => {
            let mut app_lock = app.lock().unwrap();
            let (list_state, actions) = match list_type {
                ListType::Title => (&app_lock.list.state.0, &app_lock.list.actions.title),
            };

            if let Some(selected) = list_state.selected() {
                let action = actions.get(selected).unwrap();

                match list_type {
                    ListType::Title => {
                        match *action {
                            "Login" => app_lock.enter_screen(&Screen::Login),
                            "Settings" => app_lock.enter_screen(&Screen::Settings),
                            "Quit" => app_lock.should_quit = true,
                            _ => {}
                        }
                    }
                }
            }
            Ok(())
        }
        _ => panic!("An event of type {:?} was passed to the list update function", event)
    }
}