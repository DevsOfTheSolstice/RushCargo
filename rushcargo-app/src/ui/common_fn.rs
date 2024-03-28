use ratatui::{
    layout::{Layout, Direction, Rect, Constraint},
    prelude::{Line, Frame},
    widgets::Clear,
};
use anyhow::{Result, anyhow, Error};

pub fn centered_rect(r: &Rect, width: u16, height: u16) -> Result<Rect> {
    let rect_padding_x = ((r.width.checked_sub(width).ok_or_else(|| anyhow!("")))? / 2) as u16;
    let rect_padding_y = ((r.height.checked_sub(height).ok_or_else(|| anyhow!("")))? / 2) as u16;
    let full_padding_x = r.x + rect_padding_x;
    let full_padding_y = r.y + rect_padding_y;
    Ok(Rect {
        x: full_padding_x,
        y: full_padding_y,
        width,
        height,
    })
}

pub fn wrap_text(width: usize, text: String) -> Vec<Line<'static>> {
    let mut ret: Vec<Line> = Vec::new();
    let remaining_text = text.split_whitespace();

    let mut line_text = String::new();
    for word in remaining_text {
        if word.len() + line_text.len() <= width {
            line_text.push_str(&(word.to_string() + " "));
        } else {
            if !line_text.is_empty() {
                line_text.pop();
                ret.push(Line::raw(line_text.clone()));
                line_text.clear();
                line_text.push_str(&(word.to_string() + " "));
            }
            else { return Vec::new(); }
        }
    }
    ret.push(Line::raw(line_text.clone()));

    ret
}

pub fn clear_chunks(f: &mut Frame, chunks: &std::rc::Rc<[Rect]>) {
    for chunk in chunks.iter() {
        f.render_widget(Clear, *chunk);
    }
}