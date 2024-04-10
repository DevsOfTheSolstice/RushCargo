mod title;
mod settings;
mod login;
mod common_fn;

use std::sync::{Arc, Mutex};
use ratatui::prelude::{Frame, Layout};
use crate::model::{common::Screen, app::App};

pub fn render(app: &mut Arc<Mutex<App>>, f: &mut Frame) {
    let curr_screen = app.lock().unwrap().active_screen.clone();

    { 
        let mut app_lock = app.lock().unwrap();
        if app_lock.should_clear_screen {
            common_fn::clear_chunks(f, &Layout::default().split(f.size()));
            app_lock.should_clear_screen = false;
        }
    }

    match curr_screen {
        Screen::Title
        => title::render(app, f),

        Screen::Settings
        => settings::render(app, f),

        Screen::Login
        => login::render(app, f),

        _ => panic!("Screen {:?} was not found on the main render function.", curr_screen)
    }
}