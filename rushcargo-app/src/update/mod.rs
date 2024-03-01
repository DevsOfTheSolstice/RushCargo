//mod common;
//mod list;
//mod client;
//mod admin;
//mod common_fn;
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
        _ => todo!()
        //_ => panic!("received event {:?} without assigned function", event)
    }
}