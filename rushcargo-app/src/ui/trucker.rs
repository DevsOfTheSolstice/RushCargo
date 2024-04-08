use ratatui::{
    layout::{Constraint, Direction, Layout},
    prelude::{Alignment, Frame, Margin, Rect},
    style::{Color, Modifier, Style, Styled},
    text::{Line, Span, Text},
    widgets::{Block, BorderType, Borders, Clear, List, ListItem, Paragraph, Row, Table}
};
use anyhow::{Result, anyhow};
use rust_decimal::Decimal;
use std::{default, sync::{Arc, Mutex}};
use crate::{
    model::{
        app::App, common::{GetDBErr, InputMode, Popup, Screen, SubScreen, TimeoutType, User}, db_obj::ShippingGuide, help_text, trucker::Trucker
    },
    ui::common_fn::{centered_rect, dimensions_string, wrap_text},
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

    let trucker_data_block = Block::default().borders(Borders::ALL).border_type(BorderType::Rounded);

    let trucker_data = {
        let app_lock = app.lock().unwrap();
        let trucker = app_lock.get_trucker_ref();
        Paragraph::new(
            Line::from(vec![
                Span::raw(" User "),
                Span::styled(trucker.info.username.clone(), Style::default().add_modifier(Modifier::BOLD).fg(Color::Cyan)),
                Span::raw(format!(" designated truck: {}", trucker.info.truck.clone()))
        
            ])
        ).block(trucker_data_block)
    };

    f.render_widget(trucker_data, chunks[0]);

    let help_block = Block::default().borders(Borders::TOP);

    let active_screen = app.lock().unwrap().active_screen.clone();
    
    match active_screen {
        Screen::Trucker(SubScreen::TruckerMain) => {
            let help = Paragraph::new(HELP_TEXT.trucker.main).block(help_block);
            f.render_widget(help, chunks[2]);

            let actions_chunks = Layout::default()
                .direction(Direction::Vertical)
                .constraints([
                    Constraint::Length(5),
                    Constraint::Length(5),
                    Constraint::Length(5),
                ])
                .split(centered_rect(&chunks[1], 30, 9)?);

            let unsel_action_block = Block::default().borders(Borders::ALL).border_type(BorderType::Rounded);
            let sel_action_block = Block::default().borders(Borders::ALL).border_type(BorderType::Thick);

            let Statistics = {
                let app_lock = app.lock().unwrap();
                if let Some(0) = app_lock.action_sel {
                    Paragraph::new("View statistics").centered().block(sel_action_block.clone()).style(Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD))
                } else {
                    Paragraph::new("View statistics").centered().block(unsel_action_block.clone()).style(Style::default().fg(Color::DarkGray))
                }
            };

            f.render_widget(Statistics, actions_chunks[0]);
 
            let management_action = {
                let app_lock = app.lock().unwrap();
                if let Some(1) = app_lock.action_sel {
                    Paragraph::new("View packages to accept").centered().block(sel_action_block.clone()).style(Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD))
                } else {
                    Paragraph::new("View packages to accept").centered().block(unsel_action_block.clone()).style(Style::default().fg(Color::DarkGray))
                }
            };

            f.render_widget(management_action, actions_chunks[1]);

            let route_action = {
                let app_lock = app.lock().unwrap();
                if let Some(2) = app_lock.action_sel {
                    Paragraph::new("View routes").centered().block(sel_action_block.clone()).style(Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD))
                } else {
                    Paragraph::new("View routes").centered().block(unsel_action_block.clone()).style(Style::default().fg(Color::DarkGray))
                }
            };

            f.render_widget(route_action, actions_chunks[2]);
            
        }  
        Screen::Trucker(SubScreen::TruckerStatistics) => {
            let help = Paragraph::new(HELP_TEXT.trucker.Statistics).block(help_block);
            f.render_widget(help, chunks[2]);

            let stats_chunks = Layout::default()
                .direction(Direction::Vertical)
                .constraints([
                    Constraint::Length(5),
                    Constraint::Length(5),
                    Constraint::Length(5),
                ])
                .split(centered_rect(&chunks[1], 30, 9)?);

                let unsel_action_block = Block::default().borders(Borders::ALL).border_type(BorderType::Rounded);
                let sel_action_block = Block::default().borders(Borders::ALL).border_type(BorderType::Thick);

                let year = {
                    let app_lock = app.lock().unwrap();
                    if let Some(0) = app_lock.action_sel {
                        Paragraph::new("Yearly Stats").centered().block(sel_action_block.clone()).style(Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD))
                    } else {
                        Paragraph::new("Yearly Stats").centered().block(unsel_action_block.clone()).style(Style::default().fg(Color::DarkGray))
                    }
                };
    
                f.render_widget(year, stats_chunks[0]);
                
                let month = {
                    let app_lock = app.lock().unwrap();
                    if let Some(1) = app_lock.action_sel {
                        Paragraph::new("Monthly Stats").centered().block(sel_action_block.clone()).style(Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD))
                    } else {
                        Paragraph::new("Monthly Stats").centered().block(unsel_action_block.clone()).style(Style::default().fg(Color::DarkGray))
                    }
                };
                f.render_widget(month, stats_chunks[1]);

                let day = {
                    let app_lock = app.lock().unwrap();
                    if let Some(2) = app_lock.action_sel {
                        Paragraph::new("Daily Stats").centered().block(sel_action_block.clone()).style(Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD))
                    } else {
                        Paragraph::new("Daily Stats").centered().block(unsel_action_block.clone()).style(Style::default().fg(Color::DarkGray))
                    }
                };
                f.render_widget(day, stats_chunks[2]);
        } 
        Screen::Trucker(SubScreen::TruckerStatYear) => {
            /*let help = Paragraph::new(HELP_TEXT.trucker.Statistics).block(help_block);
            let ystats_chunks = Layout::default()
                .direction(Direction::Horizontal)
                .constraints([
                    Constraint::Percentage(65),
                    Constraint::Min(1),
                    Constraint::Percentage(35)
                ])
                .split(chunks[1].inner(&Margin::new(6, 0))); */
                    /* 
                
                    // Create a block for the input field
                    let input_block = Block::default()
                        .borders(Borders::ALL)
                        .border_type(BorderType::Rounded)
                        .title("Enter Year");
                
                    // Create an input field
                    let input_field = Paragraph::new(app_lock.year_input.as_ref())
                        .block(input_block)
                        .style(Style::default().fg(Color::White))
                        .alignment(Alignment::Left);
                
                    // Render the input field
                    f.render_widget(input_field, chunks[1]);
                
                    // Create a block for the yearly statistics
                    let year_stats_block = Block::default()
                        .borders(Borders::ALL)
                        .border_type(BorderType::Rounded)
                        .title("Yearly Statistics");
                
                    // Get the statistics for the entered year
                    let stats = {
                        let year = app_lock.year_input.parse::<i32>().unwrap_or(0);
                        app_lock.get_yearly_stats(year)
                    };
                
                    // Create a paragraph for the statistics
                    let year_stats = Paragraph::new(stats)
                        .block(year_stats_block)
                        .style(Style::default().fg(Color::White))
                        .alignment(Alignment::Left);
                
                    // Render the statistics
                    f.render_widget(year_stats, chunks[2]);
                    */
                

        }
        Screen::Trucker(SubScreen::TruckerStatMonth) => {

        }
        Screen::Trucker(SubScreen::TruckerStatDay) => {

        }

        /*Screen::Trucker(SubScreen::TruckerRoutes) => {
            let help = Paragraph::new(HELP_TEXT.trucker.route_action).block(help_block);
            let routes_chunks = Layout::default()
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
                app_lock.get_trucker_guides_ref().viewing_guides
                .iter()
                .enumerate()
                .map(|(i, ShippingGuide)| {
                    Row::new(vec![
                        match &app_lock.get_trucker_guides_ref().viewing_guides {
                            Some(viewing_guides) if viewing_guides.contains(ShippingGuide) => {
                                Text::styled("☑ ", Style::default().fg(Color::Yellow))
                            }
                            _ => Text::from("☐")
                        },
                        Text::from((app_lock.get_trucker_guides_ref().viewing_guides_idx + 1 - (app_lock.get_trucker_guides_ref().viewing_guides.len() - i) as i64).to_string()),
                    ])
                    .height(2)
                })
                .collect()
            };

            let routes_table = Table::new(rows, widths)
            .column_spacing(3)
            .header(header.bottom_margin(1))
            .highlight_style(Style::default().fg(Color::LightYellow).add_modifier(Modifier::REVERSED))
            .highlight_symbol(vec![Line::raw(" █ "), Line::raw(" █ ")])
            .highlight_spacing(ratatui::widgets::HighlightSpacing::Always)
            .block(Block::default().borders(Borders::ALL).border_type(BorderType::Plain));

            f.render_stateful_widget(routes_table, routes_chunks[0], &mut app.lock().unwrap().table.state);

            let route_view_block = Block::default().borders(Borders::ALL).border_type(BorderType::Double);

            f.render_widget(route_view_block, routes_chunks[2]);

            let active_route = app.lock().unwrap().get_trucker_guides_ref().active_guide.clone();
            if let Some(active_route) = active_route {
                let route_view_chunks = Layout::default()
                    .direction(Direction::Vertical)
                    .constraints([
                        Constraint::Min(2),
                        Constraint::Min(7),
                    ])
                    .split(routes_chunks[2].inner(&Margin::new(1, 1)));

                let route_title = Paragraph::new(vec![
                    Line::styled("Order ID: ", Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD)),
                    Line::styled(active_route.shipping_num.to_string(), Style::default().fg(Color::LightYellow).add_modifier(Modifier::BOLD)),
                ]).centered();

                f.render_widget(route_title, route_view_chunks[0]);
            }

        }*/
        //here the trucker can reject or accept packages
        /* 
        Screen::Trucker(SubScreen::TruckerManagementPackages) => {
            let help = Paragraph::new(HELP_TEXT.trucker.route_action).block(help_block);
            let routes_chunks = Layout::default()
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
                app_lock.get_trucker_guides_ref().viewing_guides
                .iter()
                .enumerate()
                .map(|(i, ShippingGuide)| {
                    Row::new(vec![
                        match &app_lock.get_trucker_guides_ref().viewing_guides {
                            Some(viewing_guides) if viewing_guides.contains(ShippingGuide) => {
                                Text::styled("☑ ", Style::default().fg(Color::Yellow))
                            }
                            _ => Text::from("☒")
                        },
                        Text::from((app_lock.get_trucker_guides_ref().viewing_guides_idx + 1 - (app_lock.get_trucker_guides_ref().viewing_guides.len() - i) as i64).to_string()),
                    ])
                    .height(2)
                })
                .collect()
            };

            let routes_table = Table::new(rows, widths)
            .column_spacing(3)
            .header(header.bottom_margin(1))
            .highlight_style(Style::default().fg(Color::LightYellow).add_modifier(Modifier::REVERSED))
            .highlight_symbol(vec![Line::raw(" █ "), Line::raw(" █ ")])
            .highlight_spacing(ratatui::widgets::HighlightSpacing::Always)
            .block(Block::default().borders(Borders::ALL).border_type(BorderType::Plain));

            f.render_stateful_widget(routes_table, routes_chunks[0], &mut app.lock().unwrap().table.state);

            let route_view_block = Block::default().borders(Borders::ALL).border_type(BorderType::Double);

            f.render_widget(route_view_block, routes_chunks[2]);

            let active_route = app.lock().unwrap().get_trucker_guides_ref().active_guide.clone();
            if let Some(active_route) = active_route {
                let route_view_chunks = Layout::default()
                    .direction(Direction::Vertical)
                    .constraints([
                        Constraint::Min(2),
                        Constraint::Min(7),
                    ])
                    .split(routes_chunks[2].inner(&Margin::new(1, 1)));

                let route_title = Paragraph::new(vec![
                    Line::styled("Order ID: ", Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD)),
                    Line::styled(active_route.shipping_num.to_string(), Style::default().fg(Color::LightYellow).add_modifier(Modifier::BOLD)),
                ]).centered();

                f.render_widget(route_title, route_view_chunks[0]);
            }

        } */
        
        _ => {}
    }
    Ok(())

}