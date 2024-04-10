mod common;
mod list;
mod login;
//mod cleanup;

use std::sync::{Arc, Mutex};
use sqlx::{Pool, Postgres};
use anyhow::Result;
use crate::{
    event::Event,
    model::app::App,
};

pub async fn update(app: &mut Arc<Mutex<App>>, pool: &Pool<Postgres>, event: Event) -> Result<()> {
    match event {
        Event::Quit | Event::TimeoutStep(_) | Event::KeyInput(..) |
        Event::SwitchInput | Event::EnterScreen(_)
        => common::update(app, pool, event).await,

        Event::PrevListItem(_) | Event::NextListItem(_) | Event::SelectAction(_)
        => list::update(app, pool, event).await,

        Event::TryLogin
        => login::update(app, pool, event).await,

        Event::Resize
        => Ok(()),

        _ => panic!("received event {:?} without assigned function", event)
    }
}