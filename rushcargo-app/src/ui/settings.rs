use ratatui::{
    layout::{Layout, Direction, Constraint},
    prelude::{Alignment, Frame, Modifier},
    style::{Color, Style},
    text::{Line, Span, Text},
    widgets::{Block, BorderType, Borders, Paragraph, Clear, List, ListItem}
};
use std::sync::{Arc, Mutex};
use crate::{
    HELP_TEXT,
    model::{
        common::{Popup, InputMode, TimeoutType},
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
            Constraint::Length(3),
        ])
        .split(centered_rect(
            percent_x(f, 1.0),
            percent_y(f, 1.0),
            f.size()));
    
    let list_chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([
            Constraint::Percentage(80),
            Constraint::Percentage(20),
        ])
        .split(chunks[1]);
    
    let title_block = Block::default();

    let title = Paragraph::new(Text::from(
        "Settings"
    ))
    .block(title_block)
    .alignment(Alignment::Center);

    f.render_widget(title, chunks[0]);

    let settings = List::new(
        app_lock.list.actions.settings.clone()
    ).highlight_style(Style::default().add_modifier(Modifier::REVERSED));

    f.render_stateful_widget(settings, list_chunks[0], &mut app_lock.list.state.0);

    let settings_val = List::new(
        app_lock.settings.iter().map(|val|
            if !val {ListItem::new(Text::from("False"/*"✗"*/).alignment(Alignment::Right))}
            else {ListItem::new(Text::from("True"/*"✓"*/).alignment(Alignment::Right))})
            .collect::<Vec<ListItem>>()
    );

    f.render_stateful_widget(settings_val, list_chunks[1], &mut app_lock.list.state.0);
}