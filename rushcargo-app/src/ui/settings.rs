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
}