use ratatui::{
    layout::{Constraint, Direction, Layout},
    prelude::{Alignment, Frame, Margin},
    style::{Color, Modifier, Style},
    text::{Line, Span, Text},
    widgets::{Block, BorderType, Borders, Clear, Paragraph}
};
use std::sync::{Arc, Mutex};
use crate::{
    HELP_TEXT,
    model::{
        common::{User, Screen, SubScreen, Popup, InputMode, TimeoutType},
        trucker::Trucker,
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
            percent_y(f, 1.7),
            f.size()));
    let trucker = app_lock.user.as_ref().map(|u| {
        match u {
            User::Trucker(trucker) => trucker,
            _=>panic!(),
        }
    }).unwrap();

    let trucker_data_block = Block::default().borders(Borders::ALL).border_type(BorderType::Rounded);

    let trucker_data = Paragraph::new(
        Line::from(vec![
            Span::raw(" Trucker "),
            Span::styled(trucker.trucker.username.clone(), Style::default().add_modifier(Modifier::BOLD).fg(Color::LightYellow)),
            Span::raw(format!(": {} {}", trucker.trucker.username.clone(), trucker.trucker.truck.clone()))
        ])
    ).block(trucker_data_block);
    f.render_widget(trucker_data, chunks[0]);

    let help_block = Block::default().borders(Borders::TOP);

    match app_lock.active_screen {
        Screen::Trucker(SubScreen::TruckerMain) => {
            let help = Paragraph::new(HELP_TEXT.trucker.main).block(help_block);
            f.render_widget(help, chunks[2]);

            let actions_chunks = Layout::default()
                .direction(Direction::Vertical)
                .constraints([
                    Constraint::Length(3),
                    Constraint::Length(3),
                ])
                .split(centered_rect(
                    percent_x(f, 1.0),
                    percent_y(f, 2.0),
                    chunks[1]
                ));
            let unsel_action_block = Block::default().borders(Borders::ALL).border_type(BorderType::Rounded);
            let sel_action_block = Block::default().borders(Borders::ALL).border_type(BorderType::Thick);
            
            let stats_action = 
                if let Some(0) = app_lock.action_sel {
                    Paragraph::new("View Statistics").centered().block(sel_action_block.clone()).style(Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD))
                } else {
                    Paragraph::new("View Statistics").centered().block(unsel_action_block.clone()).style(Style::default().fg(Color::DarkGray))
                };

            f.render_widget(stats_action, actions_chunks[0]);

            let management_action = 
                if let Some(1) = app_lock.action_sel {
                    Paragraph::new("View packages to accept").centered().block(sel_action_block.clone()).style(Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD))
                } else {
                    Paragraph::new("View packages to accept").centered().block(unsel_action_block.clone()).style(Style::default().fg(Color::DarkGray))
                };
            
            f.render_widget(management_action, actions_chunks[1]);

            let route_action = 
                if let Some(2) = app_lock.action_sel {
                    Paragraph::new("View route to make").centered().block(sel_action_block.clone()).style(Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD))
                } else {
                    Paragraph::new("View route to make").centered().block(unsel_action_block.clone()).style(Style::default().fg(Color::Yellow))
                };
            f.render_widget(route_action, actions_chunks[2]);
        }
        Screen::Trucker(SubScreen::TruckerStatistics) => {
            let help = Paragraph::new(HELP_TEXT.trucker.Statistics).block(help_block);
            f.render_widget(help, chunks[2]);

            let stats_table = Layout::default()
            .direction(Direction::Vertical)
            .constraints([
                Constraint::Percentage(100)
            ])
            .split(chunks[1].inner(&Margin::new(6,0)));
        }
        Screen::Trucker(SubScreen::TruckerManagementPackets) => {
            let help = Paragraph::new(HELP_TEXT.trucker.management_action).block(help_block);
            f.render_widget(help, chunks[2]);
        }
        Screen::Trucker(SubScreen::TruckerRoutes) => {
            let help = Paragraph::new(HELP_TEXT.trucker.route_action).block(help_block);
            f.render_widget(help, chunks[2]);
        }
        _ => {}
    } 
}