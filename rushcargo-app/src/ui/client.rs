use ratatui::{
    layout::{Constraint, Direction, Layout},
    prelude::{Alignment, Frame, Margin},
    style::{Color, Modifier, Style},
    text::{Line, Span, Text},
    widgets::{Table, Row, Block, BorderType, Borders, Clear, Paragraph}
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
            percent_y(f, 1.7),
            f.size()));
    
    let client = app_lock.user.as_ref().map(|u| {
        match u {
            User::Client(client) => client,
            _ => panic!(),
        }
    }).unwrap();

    let client_data_block = Block::default().borders(Borders::ALL).border_type(BorderType::Rounded);

    let client_data = Paragraph::new(
        Line::from(vec![
            Span::raw(" User "),
            Span::styled(client.info.username.clone(), Style::default().add_modifier(Modifier::BOLD).fg(Color::Cyan)),
            Span::raw(format!(": {} {}", client.info.first_name.clone(), client.info.last_name.clone()))
        ])
    ).block(client_data_block);
    f.render_widget(client_data, chunks[0]);

    let help_block = Block::default().borders(Borders::TOP);

    match app_lock.active_screen {
        Screen::Client(SubScreen::ClientMain) => {
            let help = Paragraph::new(HELP_TEXT.client.main).block(help_block);
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

            let action_block = Block::default().borders(Borders::ALL).border_type(BorderType::Rounded);

            let lockers_action = 
                if let Some(0) = app_lock.action_sel {
                    Paragraph::new("View lockers").centered().block(action_block.clone()).style(Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD))
                } else {
                    Paragraph::new("View lockers").centered().block(action_block.clone()).style(Style::default().fg(Color::DarkGray))
                };

            f.render_widget(lockers_action, actions_chunks[0]);
 
            let sent_packages_action  =
                if let Some(1) = app_lock.action_sel {
                    Paragraph::new("View sent packages").centered().block(action_block).style(Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD))
                } else {
                    Paragraph::new("View sent packages").centered().block(action_block).style(Style::default().fg(Color::DarkGray))
                };

            f.render_widget(sent_packages_action, actions_chunks[1]);
            
        }
        Screen::Client(SubScreen::ClientLockers) => {
            let help = Paragraph::new(HELP_TEXT.client.lockers).block(help_block);
            f.render_widget(help, chunks[2]);

            let lockers_table_area = Layout::default()
                .direction(Direction::Vertical)
                .constraints([
                    Constraint::Percentage(100)
                ])
                .split(chunks[1].inner(&Margin::new(6, 0)));

            let header =
                Row::new(vec!["#", "Country", "Packages"])
                .style(Style::default().fg(Color::Yellow).add_modifier(Modifier::REVERSED));
            
            let widths = [
                Constraint::Length(3),
                Constraint::Length(10),
                Constraint::Length(8),
            ];

            let rows: Vec<Row> =
                client.viewing_lockers.as_ref().unwrap()
                .iter()
                .enumerate()
                .map(|(i, locker)| {
                    Row::new(vec![
                        (client.viewing_lockers_idx + 1 - (client.viewing_lockers.as_ref().unwrap().len() - i) as i64).to_string(),
                        locker.country.name.clone(),
                        locker.package_count.to_string(),
                    ])
                })
                .collect();
                
            let lockers_table = Table::new(rows, widths)
                .column_spacing(3)
                .header(header.bottom_margin(1))
                .highlight_style(Style::default().fg(Color::LightYellow).add_modifier(Modifier::REVERSED))
                .highlight_symbol(" ▶ ")
                .highlight_spacing(ratatui::widgets::HighlightSpacing::Always)
                .block(Block::default().borders(Borders::ALL).border_type(BorderType::Plain));

            f.render_stateful_widget(lockers_table, lockers_table_area[0], &mut app_lock.table.state);
        }
        Screen::Client(SubScreen::ClientLockerPackages) => {
            let help = Paragraph::new(HELP_TEXT.client.locker_packages).block(help_block);
            f.render_widget(help, chunks[2]);

            
        }
        Screen::Client(SubScreen::ClientSentPackages) => {
            let help = Paragraph::new(HELP_TEXT.client.sent_packages).block(help_block);
            f.render_widget(help, chunks[2]);
        }
        _ => {}
    }

}