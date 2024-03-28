use ratatui::{
    layout::{Constraint, Direction, Layout},
    prelude::{Alignment, Frame, Margin, Rect},
    style::{Color, Modifier, Style},
    widgets::{Block, BorderType, Borders, Clear, List, ListItem, Paragraph, Row, Table}
};
use anyhow::{Result, anyhow};
use std::sync::{Arc, Mutex};
use crate::{
    model::{
        help_text,
        common::{InputMode, Popup, Screen, SubScreen, TimeoutType, User},
        client::GetDBErr,
        app::App,
        client::Client,
    },
    ui::common_fn::{centered_rect, wrap_text},
    HELP_TEXT
};

pub fn render(app: &mut Arc<Mutex<App>>, f: &mut Frame) {
    let err_area = centered_rect(&f.size(), 21, 4).unwrap_or(Rect::default());

    let err_block = Block::default().borders(Borders::ALL).border_type(BorderType::Thick);

    let err =
        Paragraph::new(
            wrap_text(15, HELP_TEXT.common.render_err.to_string())
        )
        .block(err_block)
        .centered();

    f.render_widget(err, err_area);
}