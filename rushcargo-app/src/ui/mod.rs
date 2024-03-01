use std::sync::{Arc, Mutex};
use ratatui::prelude::Frame;
use crate::model::{common::Screen, app::App};

pub fn render(app: &mut Arc<Mutex<App>>, f: &mut Frame) {
    let curr_screen = app.lock().unwrap().active_screen.clone();

    match curr_screen {
        _ => {}
    }
}