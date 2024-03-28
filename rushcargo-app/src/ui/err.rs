use ratatui::{
    prelude::{Frame, Rect},
    widgets::{Block, BorderType, Borders, Paragraph}
};
use std::sync::{Arc, Mutex};
use crate::{
    model::app::App,
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