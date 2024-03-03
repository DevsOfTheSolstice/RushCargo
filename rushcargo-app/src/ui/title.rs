use ratatui::{
    layout::{Layout, Direction, Constraint},
    prelude::{Alignment, Frame, Modifier},
    style::{Color, Style},
    text::{Line, Span, Text},
    widgets::{List, Block, BorderType, Borders, Paragraph, Clear}
};
use std::sync::{Arc, Mutex};
use crate::{
    HELP_TEXT,
    model::{
        common::{Popup, Screen, InputMode, TimeoutType},
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
            Constraint::Length(10),
            Constraint::Length(3),
        ])
        .split(centered_rect(
            percent_x(f, 0.8),
            percent_y(f, 1.0),
            f.size()));

    let title_block = Block::default();

    let title = Paragraph::new(Text::from(
        "RushCargo"
    ))
    .block(title_block)
    .alignment(Alignment::Center);

    f.render_widget(title, chunks[0]);
    
    let actions = List::new(
        app_lock.list.actions.title.clone()
    ).highlight_style(Style::default().add_modifier(Modifier::REVERSED));

    f.render_stateful_widget(actions, chunks[1], &mut app_lock.list.state.0);
}