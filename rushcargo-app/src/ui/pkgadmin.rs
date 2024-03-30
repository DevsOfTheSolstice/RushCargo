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
    ui::common_fn::{centered_rect, wrap_text},
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

    match app_lock.active_screen {
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
                Row::new(vec!["#", "Sender", "Recipient", "Packages"])
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
                        guide.recipient.username.clone(),
                        guide.package_count.to_string()
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
        _ => {} 
    }

    Ok(())
}