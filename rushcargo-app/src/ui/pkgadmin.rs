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
        common::{InputMode, Popup, Screen, SubScreen, Div, TimeoutType, User, GetDBErr},
        db_obj::PayType,
        app::App,
        client::Client,
    },
    ui::common_fn::{centered_rect, wrap_text, dimensions_string},
    HELP_TEXT
};

pub fn render(app: &mut Arc<Mutex<App>>, f: &mut Frame) -> Result<()> {
    let mut app_lock = app.lock().unwrap();

    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3),
            Constraint::Percentage(90),
            Constraint::Length(3),
        ])
        .split(centered_rect(&f.size(), 80, 18)?);

    let pkgadmin = app_lock.get_pkgadmin_ref();

    let pkgadmin_data_block = Block::default().borders(Borders::ALL).border_type(BorderType::Rounded);
    
    let pkgadmin_data = Paragraph::new(
        Line::from(vec![
            Span::raw(" User "),
            Span::styled(pkgadmin.info.username.clone(), Style::default().add_modifier(Modifier::BOLD).fg(Color::Cyan)),
            Span::raw(format!(": {} {}", pkgadmin.info.first_name.clone(), pkgadmin.info.last_name.clone()))
        ])
    ).block(pkgadmin_data_block);

    f.render_widget(pkgadmin_data, chunks[0]);

    let help_block = Block::default().borders(Borders::TOP);

    match &app_lock.active_screen {
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
                if let Some(0) = app_lock.action_sel {
                    Paragraph::new("View order requests").centered().block(sel_action_block.clone()).style(Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD))
                } else {
                    Paragraph::new("View order requests").centered().block(unsel_action_block.clone()).style(Style::default().fg(Color::DarkGray))
                };

            f.render_widget(order_reqs_action, actions_chunks[0]);
 
            let add_package_action  =
                if let Some(1) = app_lock.action_sel {
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

            let guides = app_lock.get_pkgadmin_guides_ref();

            let rows: Vec<Row> =
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
                .collect();

            let guides_table = Table::new(rows, widths)
                .column_spacing(3)
                .header(header.bottom_margin(1))
                .highlight_style(Style::default().fg(Color::LightYellow).add_modifier(Modifier::REVERSED))
                .highlight_symbol(" ▶ ")
                .highlight_spacing(ratatui::widgets::HighlightSpacing::Always)
                .block(Block::default().borders(Borders::ALL).border_type(BorderType::Plain));

            f.render_stateful_widget(guides_table, guides_table_area, &mut app_lock.table.state);
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

            let active_guide = app_lock.get_pkgadmin_guides_ref().active_guide.as_ref().unwrap_or_else(|| panic!("active guide was None on SubScreenPkgAdminGuideInfo"));

            let sender = Paragraph::new(Text::from(vec![
                Line::default(),
                Line::styled("Sender:", Style::default().fg(Color::Cyan)),
                Line::raw(active_guide.sender.username.clone())
            ]))
            .centered()
            .block(clients_block.clone());

            let recipient = Paragraph::new(Text::from(vec![
                Line::default(),
                Line::styled("Recipient:", Style::default().fg(Color::Cyan)),
                Line::raw(active_guide.recipient.username.clone())
            ]))
            .centered()
            .block(clients_block);

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
            
            let packages = pkgadmin.packages.as_ref().unwrap();

            let rows: Vec<Row> =
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
                .collect();

            let packages_table = Table::new(rows, widths)
                .column_spacing(3)
                .header(header.bottom_margin(1))
                .highlight_style(Style::default().fg(Color::LightYellow).add_modifier(Modifier::REVERSED))
                .highlight_symbol(vec![Line::raw(" █ "), Line::raw(" █ ")])
                .highlight_spacing(ratatui::widgets::HighlightSpacing::Always);

            f.render_stateful_widget(packages_table, packages_chunks[0], &mut app_lock.table.state);
            
            let guides = app_lock.get_pkgadmin_guides_ref();
            
            let payment = guides.active_guide_payment.as_ref().unwrap();

            let payment_block = Block::default().borders(Borders::TOP);

            let payment_info = Paragraph::new(Text::from(vec![
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
            .block(payment_block);     

            f.render_widget(payment_info, packages_chunks[1]);
            
            let package_view_block = Block::default().borders(Borders::ALL).border_type(BorderType::Double);
            f.render_widget(package_view_block, guide_info_chunks[2]);
            if let Some(active_package) = &app_lock.get_packages_ref().active_package {
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
            let help = Paragraph::new(HELP_TEXT.pkgadmin.add_package).block(help_block);
            f.render_widget(help, chunks[2]);
            
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
            
            let (package_info_style, recipient_info_style) =
                match div {
                    Div::Left => (Style::default().fg(Color::White), Style::default().fg(Color::DarkGray)),
                    Div::Right => (Style::default().fg(Color::DarkGray), Style::default().fg(Color::White)),
                };

            let package_info_block =
                Block::default()
                .borders(Borders::ALL)
                .border_type(BorderType::Rounded)
                .style(package_info_style);
            
            let package = pkgadmin.add_package.as_ref().unwrap();
            
            let width = (info_chunks[0].width.checked_sub(2).unwrap_or(3).max(3) - 3) as usize;

            let (content_text, value_text, weight_text, length_text, width_text, height_text) =
                ("Content: ", "Value: ", "Weight: ", "Length: ", "Width: ", "Height: ");
            
            let (content_scroll, value_scroll, weight_scroll, length_scroll, width_scroll, height_scroll) = (
                package.content.visual_scroll(width - content_text.len()),
                package.value.visual_scroll(width - value_text.len()),
                package.weight.visual_scroll(width - weight_text.len()),
                package.length.visual_scroll(width - length_text.len()),
                package.width.visual_scroll(width - weight_text.len()),
                package.height.visual_scroll(width - height_text.len())
            );
            
            let package_info_area = info_chunks[0].inner(&Margin::new(2, 2));

            match div {
                Div::Left =>
                    if let InputMode::Editing(field) = app_lock.input_mode {
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
                Div::Right => {}
            }

            let package_info_highlight = Style::default().fg(Color::Cyan);

            let package_info_title = Paragraph::new("Package Info").style(Style::default().fg(Color::Yellow)).centered();
            
            let content = Line::from(vec![
                Span::styled(content_text, package_info_highlight),
                Span::raw(package.content.value()),
            ]);
                
            let value = Line::from(vec![
                Span::styled(value_text, package_info_highlight),
                Span::raw(package.value.value()),
            ]);

            let weight = Line::from(vec![
                Span::styled(weight_text, package_info_highlight),
                Span::raw(package.weight.value()),
            ]);

            let length = Line::from(vec![
                Span::styled(length_text, package_info_highlight),
                Span::raw(package.length.value()),
            ]);

            let width = Line::from(vec![
                Span::styled(width_text, package_info_highlight),
                Span::raw(package.width.value()),
            ]);
            
            let height = Line::from(vec![
                Span::styled(height_text, package_info_highlight),
                Span::raw(package.height.value()),
            ]);

            let recipient_info_block =
                Block::default()
                .borders(Borders::ALL)
                .border_type(BorderType::Rounded)
                .style(recipient_info_style);

            f.render_widget(package_info_block, info_chunks[0]);
            f.render_widget(package_info_title, info_chunks[0].inner(&Margin::new(1, 1)));
            f.render_widget(content, package_info_chunks[1]);
            f.render_widget(value, package_info_chunks[2]);
            f.render_widget(weight, package_info_chunks[3]);
            f.render_widget(length, package_info_chunks[4]);
            f.render_widget(width, package_info_chunks[5]);
            f.render_widget(height, package_info_chunks[6]);
            
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

            let recipient_info_title = Paragraph::new("Recipient Info").style(Style::default().fg(Color::Yellow)).centered();
            
            let (username_text, locker_text, branch_text) =
                ("Username: ", "Locker ID: ", "Branch ID: ");
            
            let width = (recipient_info_chunks[0].width.checked_sub(2).unwrap_or(3).max(3) - 3) as usize;

            let (username_scroll, locker_scroll, branch_scroll) = (
                package.client.visual_scroll(width - username_text.len()),
                package.locker.visual_scroll(width - locker_text.len()),
                package.branch.visual_scroll(width - branch_text.len()),
            );

            let recipient_info_highlight = Style::default().fg(Color::Cyan);

            let username = Line::from(vec![
                Span::styled(username_text, recipient_info_highlight),
                Span::raw(package.client.value()),
            ]);
            
            let locker = Line::from(vec![
                Span::styled(locker_text, recipient_info_highlight),
                Span::raw(package.locker.value()),
            ]);
            
            let branch = Line::from(vec![
                Span::styled(branch_text, recipient_info_highlight),
                Span::raw(package.branch.value()),
            ]);
            
            f.render_widget(recipient_info_block.clone(), info_chunks[1]);
            f.render_widget(recipient_info_title, recipient_info_chunks[0]);
            f.render_widget(username, recipient_info_chunks[2]);
            f.render_widget(locker, recipient_info_chunks[4]);
            f.render_widget(branch, recipient_info_chunks[5]);
        }
        _ => {}
    }
    Ok(())
}