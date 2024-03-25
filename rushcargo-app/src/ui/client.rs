use ratatui::{
    layout::{Constraint, Direction, Layout},
    prelude::{Alignment, Frame, Margin},
    style::{Color, Modifier, Style},
    text::{Line, Span, Text},
    widgets::{Cell, Table, Row, Block, BorderType, Borders, Clear, Paragraph}
};
use rust_decimal::Decimal;
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
            percent_y(f, 1.9),
            f.size()));
    
    let client = app_lock.get_client_ref();

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

            let packages_chunks = Layout::default()
                .direction(Direction::Horizontal)
                .constraints([
                    Constraint::Percentage(65),
                    Constraint::Min(1),
                    Constraint::Percentage(35)
                ])
                .split(chunks[1].inner(&Margin::new(6, 0)));

            let header =
                Row::new(vec!["", "#", "Content"])
                .style(Style::default().fg(Color::Yellow).add_modifier(Modifier::REVERSED));
            
            let widths = [
                Constraint::Length(1),
                Constraint::Length(3),
                Constraint::Length(18),
            ];

            let rows: Vec<Row> =
                app_lock.get_packages_ref().viewing_packages
                .iter()
                .enumerate()
                .map(|(i, package)| {
                    Row::new(vec![
                        match &app_lock.get_packages_ref().selected_packages {
                            Some(selected_packages) if selected_packages.contains(package) => {
                                Text::styled("☑", Style::default().fg(Color::Yellow))
                            }
                            _ => Text::from("☐")
                        },
                        Text::from((app_lock.get_packages_ref().viewing_packages_idx + 1 - (app_lock.get_packages_ref().viewing_packages.len() - i) as i64).to_string()),
                        Text::from(wrap_text(18, package.content.clone())),
                    ])
                    .height(2)
                })
                .collect();
                
            let packages_table = Table::new(rows, widths)
                .column_spacing(3)
                .header(header.bottom_margin(1))
                .highlight_style(Style::default().fg(Color::LightYellow).add_modifier(Modifier::REVERSED))
                .highlight_symbol(vec![Line::raw(" █ "), Line::raw(" █ ")])//" ▶  ")
                .highlight_spacing(ratatui::widgets::HighlightSpacing::Always)
                .block(Block::default().borders(Borders::ALL).border_type(BorderType::Plain));

            f.render_stateful_widget(packages_table, packages_chunks[0], &mut app_lock.table.state);

            let package_view_block = Block::default().borders(Borders::ALL).border_type(BorderType::Double);

            let package_view_chunks = Layout::default()
                .direction(Direction::Vertical)
                .constraints([
                    Constraint::Min(2),
                    Constraint::Percentage(100)
                ])
                .split(packages_chunks[2].inner(&Margin::new(1, 1)));

            f.render_widget(package_view_block, packages_chunks[2]);
            
            if let Some(active_package) = &app_lock.packages.as_ref().unwrap().active_package {
                let package_title = Paragraph::new(vec![
                    Line::styled("Package ID:", Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD)),
                    Line::styled(active_package.tracking_num.to_string(), Style::default().fg(Color::LightYellow).add_modifier(Modifier::BOLD)),
                ]).centered();

                f.render_widget(package_title, package_view_chunks[0]);
                
                let weight = active_package.weight;
                let height = active_package.height;
                let width = active_package.width;
                let length = active_package.length;

                let package_description = Paragraph::new(vec![
                    Line::from(vec![Span::styled("* Arrival: ", Style::default().fg(Color::Cyan)), Span::raw(active_package.register_date.to_string())]),
                    Line::from(vec![
                        Span::styled("* Weight: ", Style::default().fg(Color::Cyan)),
                        Span::raw(if weight < Decimal::new(1000, 0) { weight.to_string() + "gr" } else { (weight / Decimal::new(1000, 0)).to_string() + "kg" })
                    ]),
                    Line::from(vec![Span::styled("* Dimensions: ", Style::default().fg(Color::Cyan))]),
                    Line::raw(format!("    Height: {}", dimensions_string(height))),
                    Line::raw(format!("    Width: {}", dimensions_string(width))),
                    Line::raw(format!("    Length: {}", dimensions_string(length))),
                ]);

                f.render_widget(package_description, package_view_chunks[1]);
            }
        }
        Screen::Client(SubScreen::ClientSentPackages) => {
            let help = Paragraph::new(HELP_TEXT.client.sent_packages).block(help_block);
            f.render_widget(help, chunks[2]);
        }
        _ => {}
    }
}

fn dimensions_string(val: Decimal) -> String {
    if val < Decimal::new(100, 0) {
        String::from(format!("{}cm", val))
    } else {
        String::from(format!("{}m", val / Decimal::new(100, 2)))
    }
}

fn wrap_text(width: usize, text: String) -> Vec<Line<'static>> {
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