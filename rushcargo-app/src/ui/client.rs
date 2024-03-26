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
    model::{
        app::App, client::Client, common::{InputMode, Popup, Screen, SubScreen, TimeoutType, User}, help_text
    }, ui::common_fn::{
        centered_rect, clear_chunks, percent_x, percent_y
    }, HELP_TEXT
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

            let unsel_action_block = Block::default().borders(Borders::ALL).border_type(BorderType::Rounded);
            let sel_action_block = Block::default().borders(Borders::ALL).border_type(BorderType::Thick);

            let lockers_action = 
                if let Some(0) = app_lock.action_sel {
                    Paragraph::new("View lockers").centered().block(sel_action_block.clone()).style(Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD))
                } else {
                    Paragraph::new("View lockers").centered().block(unsel_action_block.clone()).style(Style::default().fg(Color::DarkGray))
                };

            f.render_widget(lockers_action, actions_chunks[0]);
 
            let sent_packages_action  =
                if let Some(1) = app_lock.action_sel {
                    Paragraph::new("View sent packages").centered().block(sel_action_block).style(Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD))
                } else {
                    Paragraph::new("View sent packages").centered().block(unsel_action_block).style(Style::default().fg(Color::DarkGray))
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
                app_lock.get_client_packages_ref().viewing_packages
                .iter()
                .enumerate()
                .map(|(i, package)| {
                    Row::new(vec![
                        match &app_lock.get_client_packages_ref().selected_packages {
                            Some(selected_packages) if selected_packages.contains(package) => {
                                Text::styled("☑", Style::default().fg(Color::Yellow))
                            }
                            _ => Text::from("☐")
                        },
                        Text::from((app_lock.get_client_packages_ref().viewing_packages_idx + 1 - (app_lock.get_client_packages_ref().viewing_packages.len() - i) as i64).to_string()),
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
            
            if let Some(active_package) = &app_lock.get_client_packages_ref().active_package {
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

            match app_lock.active_popup {
                None => {
                    let help = Paragraph::new(HELP_TEXT.client.locker_packages).block(help_block);
                    f.render_widget(help, chunks[2]);
                }
                Some(Popup::ClientOrderMain) => {
                    let help = Paragraph::new(HELP_TEXT.client.order_main).block(help_block);
                    f.render_widget(help, chunks[2]);

                    let popup_area = centered_rect(percent_x(f, 2.0), percent_y(f, 2.0), chunks[1]);

                    let popup_block = Block::default().borders(Borders::ALL).border_type(BorderType::Thick);

                    f.render_widget(Clear, popup_area);
                    f.render_widget(popup_block, popup_area);

                    let actions_chunks = Layout::default()
                        .direction(Direction::Vertical)
                        .constraints([
                            Constraint::Percentage(100),
                            Constraint::Min(2),
                            Constraint::Min(1),
                            Constraint::Min(2),
                            Constraint::Min(1),
                            Constraint::Min(2),
                        ])
                        .split(popup_area.inner(&Margin::new(1, 1)));
                    
                    let sel_style = Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD);
                    let unsel_style = Style::default().fg(Color::White);

                    let locker_action = Paragraph::new("Send sel. packages to locker")
                        .style(if let Some(0) = app_lock.action_sel { sel_style } else { unsel_style })
                        .centered();

                    let branch_action = Paragraph::new("Send sel. packages to branch")
                        .style(if let Some(1) = app_lock.action_sel { sel_style } else { unsel_style })
                        .centered();

                    let delivery_action = Paragraph::new("Send sel. packages as delivery")
                        .style(if let Some(2) = app_lock.action_sel { sel_style } else { unsel_style })
                        .centered();

                    f.render_widget(locker_action, actions_chunks[1]);
                    f.render_widget(branch_action, actions_chunks[3]);
                    f.render_widget(delivery_action, actions_chunks[5]);
                }
                Some(Popup::ClientOrderLocker) => {
                    let help = Paragraph::new(HELP_TEXT.client.order_locker).block(help_block);
                    f.render_widget(help, chunks[2]);

                    let popup_area = centered_rect(percent_x(f, 2.0), percent_y(f, 2.0), chunks[1]);

                    let popup_block = Block::default().borders(Borders::ALL).border_type(BorderType::Thick).title(Line::styled("Recipient", Style::default().fg(Color::Cyan))).title_alignment(Alignment::Center);

                    f.render_widget(Clear, popup_area);
                    f.render_widget(popup_block, popup_area);

                    let input_chunks = Layout::default()
                        .direction(Direction::Vertical)
                        .constraints([
                            Constraint::Percentage(100),
                            Constraint::Min(2),
                            Constraint::Min(2),
                            Constraint::Min(1),
                        ])
                        .split(popup_area.inner(&Margin::new(3, 1)));

                    let width = input_chunks[1].width.max(3) - 3;
                    let name_scroll = app_lock.input.0.visual_scroll(width as usize - "* Username: ".len());
                    let locker_scroll = app_lock.input.1.visual_scroll(width as usize - "* Locker ID: ".len());
                    let mut name_style = Style::default();
                    let mut locker_style = Style::default();
                    
                    if let InputMode::Editing(field) = app_lock.input_mode {
                        if field == 0 {
                            locker_style = locker_style.fg(Color::DarkGray);
                            f.set_cursor(input_chunks[1].x
                                            + (app_lock.input.0.visual_cursor().max(name_scroll) - name_scroll) as u16
                                            + "* Username: ".len() as u16
                                            + 0,
                                            input_chunks[1].y + 0,
                                        );

                        } else {
                            name_style = name_style.fg(Color::DarkGray);
                            f.set_cursor(input_chunks[2].x
                                            + (app_lock.input.1.visual_cursor().max(locker_scroll) - name_scroll) as u16
                                            + "* Locker ID: ".len() as u16
                                            + 0,
                                            input_chunks[2].y + 0,
                                        );
                        }
                    }

                    let popup_help = Paragraph::new(HELP_TEXT.client.order_locker_popup_normal).centered();
                    f.render_widget(popup_help, input_chunks[3]);

                    let name_block = Block::default()
                        .borders(Borders::BOTTOM)
                        .border_type(BorderType::Rounded)
                        .border_style(name_style);

                    let input = Paragraph::new(Text::from(Line::from(vec![
                        Span::styled("* Username: ", Style::default().fg(Color::Yellow)),
                        Span::styled(app_lock.input.0.value(), name_style)
                    ])))
                    .block(name_block)
                    .scroll((0, name_scroll as u16));

                    f.render_widget(input, input_chunks[1]);

                    let locker_block = Block::default()
                        .borders(Borders::BOTTOM)
                        .border_type(BorderType::Rounded)
                        .border_style(locker_style);
                    
                    let input = Paragraph::new(Text::from(Line::from(vec![
                        Span::styled("* Locker ID: ", Style::default().fg(Color::Yellow)),
                        Span::styled(app_lock.input.1.value(), locker_style)
                    ])))
                    .block(locker_block)
                    .scroll((0, name_scroll as u16));

                    f.render_widget(input, input_chunks[2]);
                }
                Some(Popup::ClientInputPayment) => {
                    todo!("client input payment popup ui");
                }
                _ => {}
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