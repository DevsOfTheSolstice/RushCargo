mod login;
mod common_fn;

use std::sync::{Arc, Mutex};
use ratatui::prelude::Frame;
use crate::model::{common::Screen, app::App};

pub fn render(app: &mut Arc<Mutex<App>>, f: &mut Frame) {
    let curr_screen = app.lock().unwrap().active_screen.clone();

    match curr_screen {
        Screen::Login => login::render(app, f),
        _ => panic!("Screen {:?} was not found on the main render function.", curr_screen)
    }
}