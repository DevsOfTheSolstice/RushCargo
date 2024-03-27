use ratatui::{
    layout::{Layout, Direction, Rect, Constraint},
    prelude::Frame,
    widgets::Clear,
};

pub fn centered_rect(r: &Rect, width: u16, height: u16) -> Rect {
    let rect_padding_x = ((r.width - width) / 2) as u16;
    let rect_padding_y = ((r.height - height) / 2) as u16;
    let full_padding_x = r.x + rect_padding_x;
    let full_padding_y = r.y + rect_padding_y;
    Rect {
        x: full_padding_x,
        y: full_padding_y,
        width,
        height,
    }
}

pub fn clear_chunks(f: &mut Frame, chunks: &std::rc::Rc<[Rect]>) {
    for chunk in chunks.iter() {
        f.render_widget(Clear, *chunk);
    }
}