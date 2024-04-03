use ratatui::{
    layout::{Constraint, Direction, Layout, Offset},
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
        common::{InputMode, Popup, Screen, SubScreen, Div, TimeoutType, User, GetDBErr},
        db_obj::PayType,
        app::App,
        client::Client,
    },
    ui::{
        common_fn::{centered_rect, wrap_text, dimensions_string},
        common_render::online_payment,
    },
    HELP_TEXT
};

pub fn render(app: &mut Arc<Mutex<App>>, f: &mut Frame) -> Result<()> {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3),
            Constraint::Percentage(90),
            Constraint::Length(3),
        ])
        .split(centered_rect(&f.size(), 80, 18)?);

    let pkgadmin_data_block = Block::default().borders(Borders::ALL).border_type(BorderType::Rounded);
    
    let pkgadmin_data = {
        let app_lock = app.lock().unwrap();
        let pkgadmin = app_lock.get_pkgadmin_ref();
        Paragraph::new(
            Line::from(vec![
                Span::raw(" User "),
                Span::styled(pkgadmin.info.username.clone(), Style::default().add_modifier(Modifier::BOLD).fg(Color::Cyan)),
                Span::raw(format!(": {} {}", pkgadmin.info.first_name.clone(), pkgadmin.info.last_name.clone()))
            ])
        ).block(pkgadmin_data_block)
    };

    f.render_widget(pkgadmin_data, chunks[0]);

    let help_block = Block::default().borders(Borders::TOP);

    let active_screen = app.lock().unwrap().active_screen.clone();
    match active_screen {
        Screen::PkgAdmin(SubScreen::PkgAdminMain) => {
            let help = Paragraph::new(HELP_TEXT.pkgadmin.main).block(help_block);
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

            let order_reqs_action = 
                if let Some(0) = app.lock().unwrap().action_sel {
                    Paragraph::new("View order requests").centered().block(sel_action_block.clone()).style(Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD))
                } else {
                    Paragraph::new("View order requests").centered().block(unsel_action_block.clone()).style(Style::default().fg(Color::DarkGray))
                };

            f.render_widget(order_reqs_action, actions_chunks[0]);
 
            let add_package_action  =
                if let Some(1) = app.lock().unwrap().action_sel {
                    Paragraph::new("Add a package").centered().block(sel_action_block).style(Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD))
                } else {
                    Paragraph::new("Add a package").centered().block(unsel_action_block).style(Style::default().fg(Color::DarkGray))
                };

            f.render_widget(add_package_action, actions_chunks[1]);
        }
        Screen::PkgAdmin(SubScreen::PkgAdminGuides) => {
            let help = Paragraph::new(HELP_TEXT.pkgadmin.guides).block(help_block);
            f.render_widget(help, chunks[2]);

            let guides_table_area = chunks[1].inner(&Margin::new(6, 0));

            let header =
                Row::new(vec!["#", "Sender", "Type", "Packages"])
                .style(Style::default().fg(Color::Yellow).add_modifier(Modifier::REVERSED));

            let widths = [
                Constraint::Length(3),
                Constraint::Length(15),
                Constraint::Length(15),
                Constraint::Length(8),
            ];


            let rows: Vec<Row> = {
                let app_lock = app.lock().unwrap();
                let guides = app_lock.get_pkgadmin_guides_ref();
                guides.viewing_guides
                .iter()
                .enumerate()
                .map(|(i, guide)| {
                    Row::new(vec![(
                        guides.viewing_guides_idx + 1 - (guides.viewing_guides.len() - i) as i64).to_string(),
                        guide.sender.username.clone(),
                        guide.shipping_type.to_string(),
                        guide.package_count.to_string(),
                    ])
                })
                .collect()
            };

            let guides_table = Table::new(rows, widths)
                .column_spacing(3)
                .header(header.bottom_margin(1))
                .highlight_style(Style::default().fg(Color::LightYellow).add_modifier(Modifier::REVERSED))
                .highlight_symbol(" ▶ ")
                .highlight_spacing(ratatui::widgets::HighlightSpacing::Always)
                .block(Block::default().borders(Borders::ALL).border_type(BorderType::Plain));

            f.render_stateful_widget(guides_table, guides_table_area, &mut app.lock().unwrap().table.state);
        }
        Screen::PkgAdmin(SubScreen::PkgAdminGuideInfo) => {
            let help = Paragraph::new(HELP_TEXT.pkgadmin.guide_info).block(help_block);
            f.render_widget(help, chunks[2]);

            let guide_info_chunks = Layout::default()
                .direction(Direction::Horizontal)
                .constraints([
                    Constraint::Length(22),
                    Constraint::Length(35),
                    Constraint::Min(1),
                ])
                .split(chunks[1]);
            
            let clients_chunks = Layout::default()
                .direction(Direction::Vertical)
                .constraints([
                    Constraint::Percentage(50),
                    Constraint::Percentage(50),
                ]).split(guide_info_chunks[0]);
            
            let clients_block = Block::default().borders(Borders::ALL).border_type(BorderType::Plain);


            let sender = {
                let app_lock = app.lock().unwrap();
                let active_guide = app_lock.get_pkgadmin_guides_ref().active_guide.as_ref().unwrap_or_else(|| panic!("active guide was None on SubScreenPkgAdminGuideInfo"));
                Paragraph::new(Text::from(vec![
                    Line::default(),
                    Line::styled("Sender:", Style::default().fg(Color::Cyan)),
                    Line::raw(active_guide.sender.username.clone())
                ]))
                .centered()
                .block(clients_block.clone())
            };

            let recipient = {
                let app_lock = app.lock().unwrap();
                let active_guide = app_lock.get_pkgadmin_guides_ref().active_guide.as_ref().unwrap_or_else(|| panic!("active guide was None on SubScreenPkgAdminGuideInfo"));
                Paragraph::new(Text::from(vec![
                    Line::default(),
                    Line::styled("Recipient:", Style::default().fg(Color::Cyan)),
                    Line::raw(active_guide.recipient.username.clone())
                ]))
                .centered()
                .block(clients_block)
            };

            f.render_widget(sender, clients_chunks[0]);
            f.render_widget(recipient, clients_chunks[1]);

            let packages_chunks = Layout::default()
                .direction(Direction::Vertical)
                .constraints([
                    Constraint::Min(2),
                    Constraint::Length(3),
                ])
                .split(guide_info_chunks[1].inner(&Margin::new(1, 1)));
            
            let packages_area_block = Block::default().borders(Borders::ALL).border_type(BorderType::Plain);

            f.render_widget(packages_area_block, guide_info_chunks[1]);

            let header =
                Row::new(vec!["#", "Content"])
                .style(Style::default().fg(Color::Yellow).add_modifier(Modifier::REVERSED));

            let widths = [
                Constraint::Length(3),
                Constraint::Length(20),
            ];
            
            let rows: Vec<Row> = {
                let app_lock = app.lock().unwrap();
                let packages = app_lock.get_pkgadmin_ref().packages.as_ref().unwrap();
                packages.viewing_packages
                .iter()
                .enumerate()
                .map(|(i, package)| {
                    Row::new(vec![
                        Text::from((packages.viewing_packages_idx + 1 - (packages.viewing_packages.len() - i) as i64).to_string()),
                        Text::from(wrap_text(20, package.content.clone())),
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
                .highlight_spacing(ratatui::widgets::HighlightSpacing::Always);

            f.render_stateful_widget(packages_table, packages_chunks[0], &mut app.lock().unwrap().table.state);
            
            let payment_block = Block::default().borders(Borders::TOP);

            let payment_info = {
                let app_lock = app.lock().unwrap();
                let payment = app_lock.get_pkgadmin_guides_ref().active_guide_payment.as_ref().unwrap();
                Paragraph::new(Text::from(vec![
                    match payment.pay_type {
                        PayType::Online => {
                            Line::from(vec![
                                Span::styled(" ".to_string() + &payment.platform + ": ", Style::default().fg(Color::Cyan)),
                                Span::raw(payment.transaction_id.clone())
                            ])
                        }
                        PayType::Card | PayType::Cash => {
                            Line::from(Span::styled(" ".to_string() + &payment.pay_type.to_string(), Style::default().fg(Color::Cyan)))
                        }
                    },
                    Line::from(vec![
                        Span::styled(" -> Amount: ", Style::default().fg(Color::Cyan)),
                        Span::raw(payment.amount.to_string() + "$")
                    ]),
                ]))
                .block(payment_block)
            };

            f.render_widget(payment_info, packages_chunks[1]);
            
            let package_view_block = Block::default().borders(Borders::ALL).border_type(BorderType::Double);
            f.render_widget(package_view_block, guide_info_chunks[2]);

            let active_package = app.lock().unwrap().get_packages_ref().active_package.clone();
            if let Some(active_package) = active_package {
                let package_view_chunks = Layout::default()
                    .direction(Direction::Vertical)
                    .constraints([
                        Constraint::Min(2),
                        Constraint::Min(7),
                    ])
                    .split(guide_info_chunks[2].inner(&Margin::new(1, 1)));

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
        Screen::PkgAdmin(SubScreen::PkgAdminAddPackage(div)) => {
            let main_chunks = Layout::default()
                .direction(Direction::Vertical)
                .constraints([
                    Constraint::Min(3),
                    Constraint::Percentage(100),
                ])
                .split(chunks[1].inner(&Margin::new(6, 0)));

            let info_chunks = Layout::default()
                .direction(Direction::Horizontal)
                .constraints([
                    Constraint::Percentage(60),
                    Constraint::Percentage(40),
                ])
                .split(main_chunks[1]);

            let package_info_chunks = Layout::default()
                .direction(Direction::Vertical)
                .constraints([
                    Constraint::Length(1),
                    Constraint::Length(1),
                    Constraint::Length(1),
                    Constraint::Length(1),
                    Constraint::Length(1),
                    Constraint::Length(1),
                    Constraint::Length(1),
                ])
                .split(info_chunks[0].inner(&Margin::new(2, 1)));

            let title_block = Block::default().borders(Borders::ALL).border_type(BorderType::Rounded);

            let title =
                Paragraph::new("Add a package")
                .style(Style::default().fg(Color::Yellow))
                .centered()
                .block(title_block);
            
            f.render_widget(title, main_chunks[0].inner(&Margin::new(20, 0)));
            
            let (lstyle_title, rstyle_title, lstyle_highlight, rstyle_highlight, lstyle_normal, rstyle_normal) =
                match div {
                    Div::Left =>
                        (
                            Style::default().fg(Color::Yellow), Style::default().fg(Color::DarkGray),
                            Style::default().fg(Color::Cyan), Style::default().fg(Color::DarkGray),
                            Style::default().fg(Color::White), Style::default().fg(Color::DarkGray)
                        ),
                    Div::Right =>
                        (
                            Style::default().fg(Color::DarkGray), Style::default().fg(Color::Yellow),
                            Style::default().fg(Color::DarkGray), Style::default().fg(Color::Cyan),
                            Style::default().fg(Color::DarkGray), Style::default().fg(Color::White)
                        )
                };

            let package_info_block =
                Block::default()
                .borders(Borders::ALL)
                .border_type(BorderType::Rounded)
                .style(lstyle_normal);
            
            let width = (info_chunks[0].width.checked_sub(2).unwrap_or(3).max(3) - 3) as usize;

            let (content_text, value_text, weight_text, length_text, width_text, height_text) =
                ("Content: ", "Value: ", "Weight: ", "Length: ", "Width: ", "Height: ");
            
            let (content_scroll, value_scroll, weight_scroll, length_scroll, width_scroll, height_scroll) = {
                let app_lock = app.lock().unwrap();
                let package = app_lock.get_pkgadmin_ref().add_package.as_ref().unwrap();
                (
                    package.content.visual_scroll(width - content_text.len()),
                    package.value.visual_scroll(width - value_text.len()),
                    package.weight.visual_scroll(width - weight_text.len()),
                    package.length.visual_scroll(width - length_text.len()),
                    package.width.visual_scroll(width - weight_text.len()),
                    package.height.visual_scroll(width - height_text.len())
                )
            };

            let width = (info_chunks[1].width.checked_sub(2).unwrap_or(3).max(3) - 3) as usize;
            
            let (username_text, locker_text, branch_text) =
                ("Username: ", "Locker ID: ", "Branch ID: ");

            let (username_scroll, locker_scroll, branch_scroll) = {
                let app_lock = app.lock().unwrap();
                let package = app_lock.get_pkgadmin_ref().add_package.as_ref().unwrap();
                (
                    package.client.visual_scroll(width - username_text.len()),
                    package.locker.visual_scroll(width - locker_text.len()),
                    package.branch.visual_scroll(width - branch_text.len())
                )
            };

            let input_mode = app.lock().unwrap().input_mode.clone(); 
            match div {
                Div::Left =>
                    if let InputMode::Editing(field) = input_mode {
                        let package_info_area = info_chunks[0].inner(&Margin::new(2, 2));
                        let app_lock = app.lock().unwrap();
                        let package = app_lock.get_pkgadmin_ref().add_package.as_ref().unwrap();
                        f.set_cursor(
                            package_info_area.x +
                            match field {
                                0 =>
                                    (package.content.visual_cursor().max(content_scroll) - content_scroll) as u16
                                    + content_text.len() as u16,
                                1 =>
                                    (package.value.visual_cursor().max(value_scroll) - value_scroll) as u16
                                    + value_text.len() as u16,
                                2 =>
                                    (package.weight.visual_cursor().max(weight_scroll) - weight_scroll) as u16
                                    + weight_text.len() as u16,
                                3 =>
                                    (package.length.visual_cursor().max(length_scroll) - length_scroll) as u16
                                    + length_text.len() as u16,
                                4 =>
                                    (package.width.visual_cursor().max(width_scroll) - width_scroll) as u16
                                    + width_text.len() as u16,
                                5 =>
                                    (package.height.visual_cursor().max(height_scroll) - height_scroll) as u16
                                    + height_text.len() as u16,
                                _ =>
                                    panic!("unexpected value in InputMode::Editing()")
                            },
                            package_info_area.y + field as u16
                        );
                    },
                Div::Right => {
                    if let InputMode::Editing(field) = input_mode {
                        let package_info_area = info_chunks[1].inner(&Margin::new(2, 2));
                        let app_lock = app.lock().unwrap();
                        let package = app_lock.get_pkgadmin_ref().add_package.as_ref().unwrap();
                        let (offset_x, offset_y) =
                            match field {
                                0 =>
                                    ((package.client.visual_cursor().max(username_scroll) - username_scroll) as u16
                                    + username_text.len() as u16,
                                    1 + field as u16),
                                1 =>
                                    ((package.locker.visual_cursor().max(locker_scroll) - locker_scroll) as u16
                                    + locker_text.len() as u16,
                                    2 + field as u16),
                                2 =>
                                    ((package.branch.visual_cursor().max(branch_scroll) - branch_scroll) as u16
                                    + branch_text.len() as u16,
                                    2 + field as u16),
                                _ =>
                                    panic!("unexpected value in InputMode::Editing()")
                            };
                        f.set_cursor(package_info_area.x + offset_x, package_info_area.y + offset_y);
                    }
                }
            }

            let package_info_title = Paragraph::new(
                "Package Info"
            )
            .style(lstyle_title)
            .centered();

            let content_title = Line::styled(content_text, lstyle_highlight);
            let content = {
                let app_lock = app.lock().unwrap();
                let package = app_lock.get_pkgadmin_ref().add_package.as_ref().unwrap();
                Paragraph::new(
                    Line::styled(
                    package.content.value().to_string(), lstyle_normal
                    )
                )
                .scroll((0, content_scroll as u16))
            };
            
            let value_title = Line::styled(value_text, lstyle_highlight);
            let value = {
                let app_lock = app.lock().unwrap();
                let package = app_lock.get_pkgadmin_ref().add_package.as_ref().unwrap();
                    Paragraph::new(
                    Line::styled(
                        package.value.value().to_string(), lstyle_normal
                    )
                )
                .scroll((0, value_scroll as u16))
            };

            let weight_title = Line::styled(weight_text, lstyle_highlight);
            let weight = {
                let app_lock = app.lock().unwrap();
                let package = app_lock.get_pkgadmin_ref().add_package.as_ref().unwrap();
                Paragraph::new(
                    Line::styled(
                        package.weight.value().to_string(), lstyle_normal
                    )
                )
                .scroll((0, weight_scroll as u16))
            };

            let length_title = Line::styled(length_text, lstyle_highlight);
            let length = {
                let app_lock = app.lock().unwrap();
                let package = app_lock.get_pkgadmin_ref().add_package.as_ref().unwrap();
                Paragraph::new(
                    Line::styled(
                        package.length.value().to_string(), lstyle_normal
                    )
                )
                .scroll((0, length_scroll as u16))
            };

            let width_title = Line::styled(width_text, lstyle_highlight);
            let width = {
                let app_lock = app.lock().unwrap();
                let package = app_lock.get_pkgadmin_ref().add_package.as_ref().unwrap();
                Paragraph::new(
                    Line::styled(
                        package.width.value().to_string(), lstyle_normal
                    )
                )
                .scroll((0, width_scroll as u16))
            };
            
            let height_title = Line::styled(height_text, lstyle_highlight);
            let height = {
                let app_lock = app.lock().unwrap();
                let package = app_lock.get_pkgadmin_ref().add_package.as_ref().unwrap();
                Paragraph::new(
                    Line::styled(
                        package.height.value().to_string(), lstyle_normal
                    )
                )
                .scroll((0, height_scroll as u16))
            };

            f.render_widget(package_info_block, info_chunks[0]);
            f.render_widget(package_info_title, info_chunks[0].inner(&Margin::new(1, 1)));
            f.render_widget(content_title, package_info_chunks[1]);
            f.render_widget(content, package_info_chunks[1].offset(Offset { x: content_text.len() as i32, y: 0 }));
            f.render_widget(value_title, package_info_chunks[2]);
            f.render_widget(value, package_info_chunks[2].offset(Offset { x: value_text.len() as i32, y: 0 }));
            f.render_widget(weight_title, package_info_chunks[3]);
            f.render_widget(weight, package_info_chunks[3].offset(Offset { x: weight_text.len() as i32, y:0 }));
            f.render_widget(length_title, package_info_chunks[4]);
            f.render_widget(length, package_info_chunks[4].offset(Offset { x: length_text.len() as i32,y: 0 }));
            f.render_widget(width_title, package_info_chunks[5]);
            f.render_widget(width, package_info_chunks[5].offset(Offset { x: width_text.len() as i32, y: 0 }));
            f.render_widget(height_title, package_info_chunks[6]);
            f.render_widget(height, package_info_chunks[6].offset(Offset { x: height_text.len() as i32, y: 0 }));
            
            let recipient_info_chunks = Layout::default()
                .direction(Direction::Vertical)
                .constraints([
                    Constraint::Length(1),
                    Constraint::Length(1),
                    Constraint::Length(1),
                    Constraint::Length(1),
                    Constraint::Length(1),
                    Constraint::Length(1),
                ])
                .split(info_chunks[1].inner(&Margin::new(2, 1)));
            
            let recipient_info_block =
                Block::default()
                .borders(Borders::ALL)
                .border_type(BorderType::Rounded)
                .style(rstyle_normal);

            let recipient_info_title = Paragraph::new(
                "Recipient Info"
            )
            .style(rstyle_title).centered();
            
            let width = recipient_info_chunks[0].width as usize;

            let (username_scroll, locker_scroll, branch_scroll) = {
                let app_lock = app.lock().unwrap();
                let package = app_lock.get_pkgadmin_ref().add_package.as_ref().unwrap();
                (
                    package.client.visual_scroll(width - username_text.len()),
                    package.locker.visual_scroll(width - locker_text.len()),
                    package.branch.visual_scroll(width - branch_text.len()),
                )
            };

            let username_title = Line::styled(username_text, rstyle_highlight);
            let username = {
                let app_lock = app.lock().unwrap();
                let package = app_lock.get_pkgadmin_ref().add_package.as_ref().unwrap();
                Paragraph::new(
                    Line::styled(
                        package.client.value().to_string(), rstyle_normal
                    )
                )
                .scroll((0, username_scroll as u16))
            };

            let locker_title = Line::styled(locker_text, rstyle_highlight); 
            let locker = {
                let app_lock = app.lock().unwrap();
                let package = app_lock.get_pkgadmin_ref().add_package.as_ref().unwrap();
                Paragraph::new(
                    Line::styled(
                        package.locker.value().to_string(), rstyle_normal
                    )
                )
                .scroll((0, locker_scroll as u16))
            };

            let branch_title = Line::styled(branch_text, rstyle_highlight); 
            let branch = {
                let app_lock = app.lock().unwrap();
                let package = app_lock.get_pkgadmin_ref().add_package.as_ref().unwrap();
                Paragraph::new(
                    Line::styled(
                        package.branch.value().to_string(), rstyle_normal
                    )
                )
                .scroll((0, branch_scroll as u16))
            };
            
            f.render_widget(recipient_info_block.clone(), info_chunks[1]);
            f.render_widget(recipient_info_title, recipient_info_chunks[0]);
            f.render_widget(username_title, recipient_info_chunks[2]);
            f.render_widget(username, recipient_info_chunks[2].offset(Offset { x: username_text.len() as i32, y: 0 }));
            f.render_widget(locker_title, recipient_info_chunks[4]);
            f.render_widget(locker, recipient_info_chunks[4].offset(Offset { x: locker_text.len() as i32, y: 0 }));
            f.render_widget(branch_title, recipient_info_chunks[5]);
            f.render_widget(branch, recipient_info_chunks[5].offset(Offset { x: branch_text.len() as i32, y: 0 }));

            let active_popup = app.lock().unwrap().active_popup.clone();
            match active_popup {
                None => {
                    let help = Paragraph::new(
                        match div {
                            Div::Left => HELP_TEXT.pkgadmin.add_package_left,
                            Div::Right => HELP_TEXT.pkgadmin.add_package_right,
                        })
                        .block(help_block);

                    f.render_widget(help, chunks[2]);
                }
                Some(Popup::FieldExcess) => {
                    let help = Paragraph::new(
                        match div {
                            Div::Left => HELP_TEXT.pkgadmin.add_package_left,
                            Div::Right => HELP_TEXT.pkgadmin.add_package_right,
                        })
                        .block(help_block);

                    f.render_widget(help, chunks[2]);

                    let popup_area = centered_rect(&f.size(), 28, 4)?;

                    let err_block =
                        Block::default()
                        .borders(Borders::ALL)
                        .border_type(BorderType::Thick)
                        .style(Style::default().fg(Color::Red));

                    let err = Paragraph::new(Text::from(vec![
                        Line::raw("Remove the input on"),
                        Line::raw("Locker ID or Branch ID")
                    ]))
                    .centered()
                    .block(err_block);

                    f.render_widget(Clear, popup_area);
                    f.render_widget(err, popup_area);
                }
                Some(Popup::SelectPayment) => {
                    let help = Paragraph::new(HELP_TEXT.pkgadmin.select_payment).block(help_block);
                    f.render_widget(help, chunks[2]);

                    let popup_area = centered_rect(&chunks[1], 26, 7)?;

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
                        ])
                        .split(popup_area.inner(&Margin::new(1, 1)));

                    let sel_style = Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD);
                    let unsel_style = Style::default().fg(Color::White);

                    let online_action = Paragraph::new("Online payment")
                        .style(if let Some(0) = app.lock().unwrap().action_sel { sel_style } else { unsel_style })
                        .centered();

                    let cash_action = Paragraph::new("Cash payment")
                        .style(if let Some(1) = app.lock().unwrap().action_sel { sel_style } else { unsel_style })
                        .centered();

                    let card_action = Paragraph::new("Card payment")
                        .style(if let Some(2) = app.lock().unwrap().action_sel { sel_style } else { unsel_style })
                        .centered();

                    f.render_widget(online_action, actions_chunks[0]);
                    f.render_widget(cash_action, actions_chunks[2]);
                    f.render_widget(card_action, actions_chunks[4]);
                }
                Some(Popup::OnlinePayment) => {
                    online_payment(app, &chunks, f)?;
                }
                _ => {}
            }
        }
        _ => {}
    }
    Ok(())
}