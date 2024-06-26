use ratatui::{
    layout::{Constraint, Direction, Layout},
    prelude::{Alignment, Frame, Margin, Rect},
    style::{Color, Modifier, Style},
    text::{Line, Span, Text},
    widgets::{Block, BorderType, Borders, Clear, List, ListItem, Paragraph, Row, Table}
};
use anyhow::{Result, anyhow};
use rust_decimal::Decimal;
use std::sync::{Arc, Mutex};
use crate::{
    model::{
        help_text,
        common::{InputMode, Popup, Screen, SubScreen, TimeoutType, User, GetDBErr},
        app::App,
        client::Client,
    },
    ui::common_fn::{centered_rect, wrap_text, dimensions_string},
    ui::common_render::online_payment,
    HELP_TEXT
};

use super::common_render::order_successful;

pub fn render(app: &mut Arc<Mutex<App>>, f: &mut Frame) -> Result<()> {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3),
            Constraint::Percentage(90),
            Constraint::Length(3),
        ])
        .split(centered_rect(&f.size(), 80, 18)?);

    let client_data_block = Block::default().borders(Borders::ALL).border_type(BorderType::Rounded);

    let client_data = {
        let app_lock = app.lock().unwrap();
        let client = app_lock.get_client_ref();
        Paragraph::new(
            Line::from(vec![
                Span::raw(" User "),
                Span::styled(client.info.username.clone(), Style::default().add_modifier(Modifier::BOLD).fg(Color::Cyan)),
                Span::raw(format!(": {} {}", client.info.first_name.clone(), client.info.last_name.clone()))
            ])
        ).block(client_data_block)
    };

    f.render_widget(client_data, chunks[0]);

    let help_block = Block::default().borders(Borders::TOP);

    let active_screen = app.lock().unwrap().active_screen.clone();
    match active_screen {
        Screen::Client(SubScreen::ClientMain) => {
            let help = Paragraph::new(HELP_TEXT.client.main).block(help_block);
            f.render_widget(help, chunks[2]);

            let actions_chunks = Layout::default()
                .direction(Direction::Vertical)
                .constraints([
                    Constraint::Length(3),
                    Constraint::Length(3),
                ])
                .split(centered_rect(&chunks[1], 25, 6)?);

            let unsel_action_block = Block::default().borders(Borders::ALL).border_type(BorderType::Rounded);
            let sel_action_block = Block::default().borders(Borders::ALL).border_type(BorderType::Thick);

            let lockers_action = {
                let app_lock = app.lock().unwrap();
                if let Some(0) = app_lock.action_sel {
                    Paragraph::new("View lockers").centered().block(sel_action_block.clone()).style(Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD))
                } else {
                    Paragraph::new("View lockers").centered().block(unsel_action_block.clone()).style(Style::default().fg(Color::DarkGray))
                }
            };

            f.render_widget(lockers_action, actions_chunks[0]);
 
            let sent_packages_action = {
                let app_lock = app.lock().unwrap();
                if let Some(1) = app_lock.action_sel {
                    Paragraph::new("View sent packages").centered().block(sel_action_block).style(Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD))
                } else {
                    Paragraph::new("View sent packages").centered().block(unsel_action_block).style(Style::default().fg(Color::DarkGray))
                }
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
                Row::new(vec!["#", "Country", "Packages", "Locker ID"])
                .style(Style::default().fg(Color::Yellow).add_modifier(Modifier::REVERSED));
            
            let widths = [
                Constraint::Length(3),
                Constraint::Length(10),
                Constraint::Length(8),
                Constraint::Length(10),
            ];

            let rows: Vec<Row> = {
                let app_lock = app.lock().unwrap();
                let client = app_lock.get_client_ref();
                client.viewing_lockers.as_ref().unwrap()
                .iter()
                .enumerate()
                .map(|(i, locker)| {
                    Row::new(vec![(
                        client.viewing_lockers_idx + 1 - (client.viewing_lockers.as_ref().unwrap().len() - i) as i64).to_string(),
                        locker.country.name.clone(),
                        locker.package_count.to_string(),
                        locker.get_id().to_string(),
                    ])
                })
                .collect()
            };
                
            let lockers_table = Table::new(rows, widths)
                .column_spacing(3)
                .header(header.bottom_margin(1))
                .highlight_style(Style::default().fg(Color::LightYellow).add_modifier(Modifier::REVERSED))
                .highlight_symbol(" ▶ ")
                .highlight_spacing(ratatui::widgets::HighlightSpacing::Always)
                .block(Block::default().borders(Borders::ALL).border_type(BorderType::Plain));

            f.render_stateful_widget(lockers_table, lockers_table_area[0], &mut app.lock().unwrap().table.state);
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

            let rows: Vec<Row> = {
                let app_lock = app.lock().unwrap();
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
                .collect()
            };
                
            let packages_table = Table::new(rows, widths)
                .column_spacing(3)
                .header(header.bottom_margin(1))
                .highlight_style(Style::default().fg(Color::LightYellow).add_modifier(Modifier::REVERSED))
                .highlight_symbol(vec![Line::raw(" █ "), Line::raw(" █ ")])
                .highlight_spacing(ratatui::widgets::HighlightSpacing::Always)
                .block(Block::default().borders(Borders::ALL).border_type(BorderType::Plain));

            f.render_stateful_widget(packages_table, packages_chunks[0], &mut app.lock().unwrap().table.state);

            let package_view_block = Block::default().borders(Borders::ALL).border_type(BorderType::Double);

            f.render_widget(package_view_block, packages_chunks[2]);

            let active_package = app.lock().unwrap().get_packages_ref().active_package.clone();
            if let Some(active_package) = active_package {
                let package_view_chunks = Layout::default()
                    .direction(Direction::Vertical)
                    .constraints([
                        Constraint::Min(2),
                        Constraint::Min(7),
                    ])
                    .split(packages_chunks[2].inner(&Margin::new(1, 1)));

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

            let active_popup = app.lock().unwrap().active_popup.clone();
            match active_popup {
                None => {
                    let help = Paragraph::new(HELP_TEXT.client.locker_packages).block(help_block);
                    f.render_widget(help, chunks[2]);
                }
                Some(Popup::ClientOrderMain) => {
                    let help = Paragraph::new(HELP_TEXT.client.order_main).block(help_block);
                    f.render_widget(help, chunks[2]);

                    let popup_area = centered_rect(&chunks[1], 40, 9)?;

                    let popup_block = Block::default().borders(Borders::ALL).border_type(BorderType::Thick);

                    f.render_widget(Clear, popup_area);
                    f.render_widget(popup_block, popup_area);

                    let actions_chunks = Layout::default()
                        .direction(Direction::Vertical)
                        .constraints([
                            Constraint::Min(1),
                            Constraint::Min(1),
                            Constraint::Min(1),
                            Constraint::Min(1),
                            Constraint::Min(1),
                            Constraint::Min(1),
                            Constraint::Min(1),
                        ])
                        .split(popup_area.inner(&Margin::new(1, 1)));

                    let sel_style = Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD);
                    let unsel_style = Style::default().fg(Color::White);

                    let locker_action = Paragraph::new("Send sel. packages to locker")
                        .style(if let Some(0) = app.lock().unwrap().action_sel { sel_style } else { unsel_style })
                        .centered();

                    let branch_action = Paragraph::new("Send sel. packages to branch")
                        .style(if let Some(1) = app.lock().unwrap().action_sel { sel_style } else { unsel_style })
                        .centered();

                    let delivery_action = Paragraph::new("Send sel. packages as delivery")
                        .style(if let Some(2) = app.lock().unwrap().action_sel { sel_style } else { unsel_style })
                        .centered();

                    f.render_widget(locker_action, actions_chunks[1]);
                    f.render_widget(branch_action, actions_chunks[3]);
                    f.render_widget(delivery_action, actions_chunks[5]);
                }
                Some(Popup::ClientOrderLocker) => {
                    let help = Paragraph::new(HELP_TEXT.client.order_recipient).block(help_block);
                    f.render_widget(help, chunks[2]);

                    let popup_area = centered_rect(&chunks[1], 40, 9)?;

                    let popup_block = Block::default()
                        .borders(Borders::ALL)
                        .border_type(BorderType::Thick)
                        .title(Line::styled("Recipient", Style::default().fg(Color::Cyan)))
                        .title_alignment(Alignment::Center);

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
                    let name_scroll = app.lock().unwrap().input.0.visual_scroll(width as usize - "* Username: ".len());
                    let locker_scroll = app.lock().unwrap().input.1.visual_scroll(width as usize - "* Locker ID: ".len());
                    let mut name_style = Style::default();
                    let mut locker_style = Style::default();
                        
                    let input_mode = app.lock().unwrap().input_mode.clone();
                    if let InputMode::Editing(field) = input_mode {
                        if field == 0 {
                            locker_style = locker_style.fg(Color::DarkGray);
                            f.set_cursor(input_chunks[1].x
                                            + (app.lock().unwrap().input.0.visual_cursor().max(name_scroll) - name_scroll) as u16
                                            + "* Username: ".len() as u16
                                            + 0,
                                            input_chunks[1].y + 0,
                                        );

                        } else {
                            name_style = name_style.fg(Color::DarkGray);
                            f.set_cursor(input_chunks[2].x
                                            + (app.lock().unwrap().input.1.visual_cursor().max(locker_scroll) - locker_scroll) as u16
                                            + "* Locker ID: ".len() as u16
                                            + 0,
                                            input_chunks[2].y + 0,
                                        );
                        }
                    }

                    let err_style = Style::default().fg(Color::Red);

                    let popup_help = Paragraph::new(
                        match app.lock().unwrap().get_client_ref().get_db_err {
                            None => Line::raw(""),
                            Some(GetDBErr::InvalidUserLocker) => Line::styled(HELP_TEXT.client.order_locker_popup_invalid.to_string(), err_style),
                            Some(GetDBErr::LockerSameAsActive) => Line::styled(HELP_TEXT.client.order_locker_popup_same_as_active.to_string(), err_style),
                            Some(GetDBErr::LockerTooManyPackages) => Line::styled(HELP_TEXT.client.order_locker_popup_locker_count_err.to_string(), err_style),
                            Some(GetDBErr::LockerWeightTooBig(max_weight)) => Line::styled(HELP_TEXT.client.order_locker_popup_locker_weight_err.to_string() + &max_weight.to_string(), err_style),
                            _ => panic!()
                        }
                    ).centered();

                    f.render_widget(popup_help, input_chunks[3]);

                    let name_block = Block::default()
                        .borders(Borders::BOTTOM)
                        .border_type(BorderType::Rounded)
                        .border_style(name_style);

                    let input =
                        Paragraph::new(Text::from(Line::from(vec![
                            Span::styled("* Username: ", Style::default().fg(Color::Yellow)),
                            Span::styled(app.lock().unwrap().input.0.value().to_string(), name_style)
                        ])))
                        .block(name_block)
                        .scroll((0, name_scroll as u16));

                    f.render_widget(input, input_chunks[1]);

                    let locker_block = Block::default()
                        .borders(Borders::BOTTOM)
                        .border_type(BorderType::Rounded)
                        .border_style(locker_style);
                    
                    let input =
                        Paragraph::new(Text::from(Line::from(vec![
                            Span::styled("* Locker ID: ", Style::default().fg(Color::Yellow)),
                            Span::styled(app.lock().unwrap().input.1.value().to_string(), locker_style)
                        ])))
                        .block(locker_block)
                        .scroll((0, locker_scroll as u16));

                    f.render_widget(input, input_chunks[2]);
                }
                Some(Popup::OnlinePayment) => {
                    online_payment(app, &chunks, f)?;
                }
                Some(Popup::OrderSuccessful) => {
                    order_successful(app, &chunks, f)?;
                }
                Some(Popup::ClientOrderBranch) => {
                    let help = Paragraph::new(HELP_TEXT.client.order_recipient).block(help_block);
                    f.render_widget(help, chunks[2]);

                    let popup_area = centered_rect(&chunks[1], 40, 9)?;

                    let popup_block = Block::default()
                        .borders(Borders::ALL)
                        .border_type(BorderType::Thick)
                        .title(Line::styled("Recipient", Style::default().fg(Color::Cyan)))
                        .title_alignment(Alignment::Center);

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
                    let name_scroll = app.lock().unwrap().input.0.visual_scroll(width as usize - "* Username: ".len());
                    let branch_scroll = app.lock().unwrap().input.1.visual_scroll(width as usize - "* Branch ID: ".len());
                    let mut name_style = Style::default();
                    let mut branch_style = Style::default();
                    
                    let input_mode = app.lock().unwrap().input_mode.clone();
                    if let InputMode::Editing(field) = input_mode {
                        if field == 0 {
                            branch_style = branch_style.fg(Color::DarkGray);
                            f.set_cursor(input_chunks[1].x
                                            + (app.lock().unwrap().input.0.visual_cursor().max(name_scroll) - name_scroll) as u16
                                            + "* Username: ".len() as u16
                                            + 0,
                                            input_chunks[1].y + 0,
                                        );

                        } else {
                            name_style = name_style.fg(Color::DarkGray);
                            f.set_cursor(input_chunks[2].x
                                            + (app.lock().unwrap().input.1.visual_cursor().max(branch_scroll) - branch_scroll) as u16
                                            + "* Branch ID: ".len() as u16
                                            + 0,
                                            input_chunks[2].y + 0,
                                        );
                        }
                    }

                    let err_style = Style::default().fg(Color::Red);

                    let popup_help = Paragraph::new(
                        match app.lock().unwrap().get_client_ref().get_db_err {
                            None => Line::raw(""),
                            Some(GetDBErr::InvalidUserBranch) => Line::styled(HELP_TEXT.client.order_branch_popup_invalid.to_string(), err_style),
                            _ => panic!()
                        }
                    ).centered();

                    f.render_widget(popup_help, input_chunks[3]);

                    let name_block = Block::default()
                        .borders(Borders::BOTTOM)
                        .border_type(BorderType::Rounded)
                        .border_style(name_style);

                    let input = Paragraph::new(Text::from(Line::from(vec![
                        Span::styled("* Username: ", Style::default().fg(Color::Yellow)),
                        Span::styled(app.lock().unwrap().input.0.value().to_string(), name_style)
                    ])))
                    .block(name_block)
                    .scroll((0, name_scroll as u16));

                    f.render_widget(input, input_chunks[1]);

                    let branch_block = Block::default()
                        .borders(Borders::BOTTOM)
                        .border_type(BorderType::Rounded)
                        .border_style(branch_style);
                    
                    let input = Paragraph::new(Text::from(Line::from(vec![
                        Span::styled("* Branch ID: ", Style::default().fg(Color::Yellow)),
                        Span::styled(app.lock().unwrap().input.1.value().to_string(), branch_style)
                    ])))
                    .block(branch_block)
                    .scroll((0, branch_scroll as u16));

                    f.render_widget(input, input_chunks[2]);
                }
                Some(Popup::ClientOrderDelivery) => {
                    let help = Paragraph::new(HELP_TEXT.client.order_recipient).block(help_block);
                    f.render_widget(help, chunks[2]);

                    let popup_area = centered_rect(&chunks[1], 40, 9)?;

                    let popup_block = Block::default()
                        .borders(Borders::ALL)
                        .border_type(BorderType::Thick)
                        .title(Line::styled("Recipient", Style::default().fg(Color::Cyan)))
                        .title_alignment(Alignment::Center);

                    f.render_widget(Clear, popup_area);
                    f.render_widget(popup_block, popup_area);

                    let input_chunks = Layout::default()
                        .direction(Direction::Vertical)
                        .constraints([
                            Constraint::Percentage(100),
                            Constraint::Min(2),
                            Constraint::Min(3),
                        ])
                        .split(popup_area.inner(&Margin::new(3, 1)));

                    let width = input_chunks[1].width.max(3) - 3;
                    let name_scroll = app.lock().unwrap().input.0.visual_scroll(width as usize - "* Username: ".len());
                    let name_style = Style::default();
                    
                    f.set_cursor(input_chunks[1].x
                                            + (app.lock().unwrap().input.0.visual_cursor().max(name_scroll) - name_scroll) as u16
                                            + "* Username: ".len() as u16
                                            + 0,
                                            input_chunks[1].y + 0,
                                        );

                    let name_block = Block::default()
                        .borders(Borders::BOTTOM)
                        .border_type(BorderType::Rounded)
                        .border_style(name_style);

                    let input = Paragraph::new(Text::from(Line::from(vec![
                        Span::styled("* Username: ", Style::default().fg(Color::Yellow)),
                        Span::styled(app.lock().unwrap().input.0.value().to_string(), name_style)
                    ])))
                    .block(name_block)
                    .scroll((0, name_scroll as u16));

                    f.render_widget(input, input_chunks[1]);
                    
                    let get_db_err = app.lock().unwrap().get_client_ref().get_db_err.clone();
                    if let Some(err) = get_db_err {
                        if app.lock().unwrap().display_msg {
                            let err_popup_area = centered_rect(&f.size(), 30, 6)?;

                            let err_popup_block = Block::default().borders(Borders::ALL).border_type(BorderType::Thick);

                            let err_popup = Paragraph::new(wrap_text(25,
                                match err {
                                        GetDBErr::InvalidUserDelivery(_) => {
                                            HELP_TEXT.client.order_delivery_popup_invalid.to_string()
                                        }
                                        GetDBErr::NoCompatBranchDelivery => {
                                            HELP_TEXT.client.order_delivery_no_compat.to_string()
                                        }
                                        _ => panic!()
                                    }
                                )
                            )
                            .centered()
                            .style(Style::default().fg(Color::Red))
                            .block(err_popup_block);

                            f.render_widget(Clear, err_popup_area);
                            f.render_widget(err_popup, err_popup_area);
                        }
                        else if let GetDBErr::InvalidUserDelivery(3) = err {
                            let err_text =
                                Line::styled(
                                    format!(
                                        "{}{}", HELP_TEXT.client.order_delivery_failed_attempts,
                                        app.lock().unwrap().timeout.get(&TimeoutType::GetUserDelivery).unwrap().counter
                                    ),
                                Style::default().fg(Color::Red)
                                );
                            
                            f.render_widget(err_text, input_chunks[2]);
                        }
                    }
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
    Ok(())
}