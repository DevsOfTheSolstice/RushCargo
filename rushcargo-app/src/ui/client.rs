use ratatui::{
    layout::{Layout, Direction, Constraint},
    prelude::{Alignment, Frame},
    style::{Color, Style},
    text::{Line, Span, Text},
    widgets::{Block, BorderType, Borders, Paragraph, Clear}
};
use std::sync::{Arc, Mutex};
use crate::{
    HELP_TEXT,
    model::{
        common::{User, Screen, SubScreen, Popup, InputMode, TimeoutType},
        client::Client,
        app::App,
    },
    ui::common_fn::{
        centered_rect,
        percent_x,
        percent_y,
        clear_chunks,
    }
};

pub fn render(app: &mut Arc<Mutex<App>>, f: &mut Frame) {
    let mut app_lock = app.lock().unwrap();

    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3),
            Constraint::Percentage(90),
            Constraint::Length(3),
        ])
        .split(centered_rect(
            percent_x(f, 2.0),
            percent_y(f, 1.5),
            f.size()));
    
    let client = app_lock.user.as_ref().map(|u| {
        match u {
            User::Client(client) => client,
            _ => panic!(),
        }
    }).unwrap();

    let client_data_block = Block::default().borders(Borders::ALL).border_type(BorderType::Rounded);
    let client_data = Paragraph::new("".to_string() + &client.username.clone()).block(client_data_block);
    f.render_widget(client_data, chunks[0]);

    match app_lock.active_screen {
        Screen::Client(SubScreen::ClientMain) => {
        }
        _ => {}
    }

}