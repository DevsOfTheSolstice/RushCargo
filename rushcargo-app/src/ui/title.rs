use ratatui::{
    layout::{Layout, Direction, Constraint},
    prelude::{Alignment, Frame, Modifier},
    style::{Color, Style},
    text::{Line, Span, Text},
    symbols::Marker,
    widgets::{
        canvas::{
            Canvas,
            Points
        },
        List,
        Block,
        BorderType,
        Borders,
        Paragraph,
    }
};
use anyhow::{Result, anyhow};
use std::sync::{Arc, Mutex};
use crate::{
    HELP_TEXT,
    model::{
        common::{Popup, Screen, InputMode, TimeoutType},
        app::App,
        title::{Dot, RenderDot},
    },
    ui::common_fn::centered_rect,
};

pub fn render(app: &mut Arc<Mutex<App>>, f: &mut Frame) -> Result<()> {
    let mut app_lock = app.lock().unwrap();

    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(8),
            Constraint::Length(2),
            Constraint::Length(10),
        ])
        .split(centered_rect(&f.size(), 80, 25)?);

    let lower_chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([
            Constraint::Percentage(15),
            Constraint::Percentage(25),
            Constraint::Percentage(5),
            Constraint::Percentage(55),
        ])
        .split(chunks[2]);

    let actions_chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(1),
            Constraint::Length(3),
            Constraint::Percentage(100),
        ])
        .split(lower_chunks[1]);

    let title_block = Block::default().borders(Borders::ALL).border_type(BorderType::QuadrantOutside);

    let title = Paragraph::new(Text::from(
        app_lock.title.as_ref().unwrap().text.clone()
    ))
    .block(title_block)
    .alignment(Alignment::Center);

    f.render_widget(title, chunks[0]);

    let actions = List::new(
        app_lock.list.actions.title.clone()
    ).highlight_style(Style::default().add_modifier(Modifier::REVERSED));

    f.render_stateful_widget(actions, actions_chunks[1], &mut app_lock.list.state.0);

    let width = lower_chunks[3].width;
    let height = lower_chunks[3].height;

    let mid_width = width / 2;
    let mid_height= height / 2;

    let canvas = Canvas::default()
        .marker(Marker::Dot)
        .paint(|ctx| {
            // Render space buffer. A 2D Vec with height equal to the space's height, and width equal to the space's width.
            let mut buffer: Vec<Vec<RenderDot>> = vec![vec![RenderDot::default(); width as usize]; height as usize];

            let cube = &app_lock.title.as_ref().unwrap().cube;

            // Cube's pair of vertices that must be joined in order to make the 12 edges.
            let edges = [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), (0,4), (1,5), (3,7), (2,6)];
            // Vectors that join each pair of vertices that make the edges.
            let mut edges_vecs: Vec<Box<dyn Fn(f64, char) -> Dot>> = Vec::new();

            // Populate the edges_vecs Vec.
            for edge in edges.iter() {
                let vec = get_vec(cube.rot_dot[edge.0], cube.rot_dot[edge.1]);
                edges_vecs.push(Box::new(vec));
            }

            /// Takes the render space buffer, and puts a vector's points into it (with 0 <= t <= 1).
            /// This function also performs a check on the buffer's Z values,
            /// and converts the vector's points coordinates in a cartesian system to the buffer's
            /// system with only positive x and y.
            fn add_to_buffer(vec: impl Fn(f64, char) -> Dot, buffer: &mut Vec<Vec<RenderDot>>, mid_height: u16, mid_width: u16, char: char) {
                for j in (0..20).map(|x| x as f64 * 0.05) {
                    let dot = vec(j, char);
                    let buffer_pos = &mut buffer[(mid_height as f64 + (dot.y/* * 10.0*/)) as usize][(mid_width as f64 + (dot.x /* * 10.0*/)) as usize];
                    if !(buffer_pos.zval <= dot.z - 0.5) {
                        buffer_pos.char = dot.char;
                        buffer_pos.zval = dot.z;
                    }
                }
            }

            // These variables contain the index of edges whose points must be joined in order to form a plane.
            // The points in the normal ones are a t:r join, while the ones on the inverted are a t:(1-r) join.
            let edges_joins_normal = [(8,10,'#'), (9,11,'$'), (8,9,'~'), (10,11,';')];
            let edges_joins_inverted = [(1,3,'.'), (4,6,'-')];

            // Create planes based on the normal joins.
            for edge_join in edges_joins_normal.iter() {
                let vec0 = &edges_vecs[edge_join.0];
                let vec1 = &edges_vecs[edge_join.1];
                for i in (0..20).map(|x| x as f64 * 0.05) {
                    let vec2 = get_vec(vec0(i, '*'), vec1(i, '*'));
                    add_to_buffer(vec2, &mut buffer, mid_height, mid_width, edge_join.2);
                }
            }
            
            // Create planes based on the inverted joins.
            for edge_join in edges_joins_inverted.iter() {
                let vec0 = &edges_vecs[edge_join.0];
                let vec1 = &edges_vecs[edge_join.1];
                for i in (0..20).map(|x| x as f64 * 0.05) {
                    let vec2 = get_vec(vec0(i, '*'), vec1(1.0 - i, '*'));
                    add_to_buffer(vec2, &mut buffer, mid_height, mid_width, edge_join.2);
                }
            }

            // Print the buffer's contents.
            for i in 0..height as usize {
                for j in 0..width as usize {
                    if buffer[i][j].zval != f64::MAX {
                        ctx.print(j as f64 - mid_width as f64, i as f64 - mid_height as f64, buffer[i][j].char.to_string());
                    }
                }
            } 
        })
        .x_bounds([-((width / 2) as f64), (width / 2) as f64])
        .y_bounds([-((height / 2) as f64), (height / 2) as f64])
        .block(Block::default().borders(Borders::NONE));

    f.render_widget(canvas, lower_chunks[3]);

    Ok(())
}

fn get_vec(dot0: Dot, dot1: Dot) -> impl Fn(f64, char) -> Dot {
    let ref_vec_x = dot1.x - dot0.x;
    let ref_vec_y = dot1.y - dot0.y;
    let ref_vec_z = dot1.z - dot0.z;
    move |t, char: char| {
        Dot {
            char,
            x: dot0.x + t * ref_vec_x,
            y: dot0.y + t * ref_vec_y,
            z: dot0.z + t * ref_vec_z,
        }
    }
}