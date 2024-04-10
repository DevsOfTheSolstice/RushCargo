use ratatui::{
    layout::{Layout, Direction, Constraint, Offset},
    prelude::{Alignment, Frame, Margin, Modifier},
    style::{Color, Style},
    text::{Line, Span, Text},
    widgets::{Block, BorderType, Borders, Paragraph, Clear}
};
use anyhow::{Result, anyhow};
use std::sync::{Arc, Mutex};
use crate::{
    HELP_TEXT,
    model::{
        common::{Popup, InputMode, TimeoutType},
        app::App,
    },
    ui::common_fn::centered_rect,
};

pub fn render(app: &mut Arc<Mutex<App>>, f: &mut Frame) -> Result<()> {
    let mut app_lock = app.lock().unwrap();

    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(1),
            Constraint::Length(3),
            Constraint::Length(3),
            Constraint::Length(1),
        ])
        .split(centered_rect(&f.size(), 45, 8)?);

    let title_block = Block::default();

    let title = Paragraph::new(Text::from(
        "Login"
    ))
    .block(title_block)
    .alignment(Alignment::Center);

    f.render_widget(title, chunks[0]);

    let width = chunks[0].width.max(3) - 3;
    let name_scroll = app_lock.input.0.visual_scroll(width as usize - "* Username: ".len());
    let password_scroll = app_lock.input.1.visual_scroll(width as usize - "* Password: ".len());
    let mut name_style = Style::default();
    let mut password_style = Style::default();
    
    if let InputMode::Editing(field) = app_lock.input_mode {
        if field == 0 {
            password_style = password_style.fg(Color::DarkGray);
            f.set_cursor(chunks[1].x
                            + ((app_lock.input.0.visual_cursor()).max(name_scroll) - name_scroll) as u16
                            + "* Username: ".len() as u16
                            + 1,
                            chunks[1].y + 1,
                        );
        } else {
            name_style = name_style.fg(Color::DarkGray);
            f.set_cursor(chunks[2].x
                            + ((app_lock.input.1.visual_cursor()).max(password_scroll) - password_scroll) as u16
                            + "* Password: ".len() as u16
                            + 1,
                        chunks[2].y + 1,
                        );
        }
    }
    
    let name_block = Block::default()
        .borders(Borders::ALL)
        .border_type(BorderType::Rounded)
        .border_style(name_style);

    let input = Paragraph::new(Text::from(Line::from(vec![
        Span::styled("* Username: ", Style::default().fg(Color::Yellow)),
        Span::styled(app_lock.input.0.value(), name_style)
    ])))
    .block(name_block)
    .scroll((0, name_scroll as u16));

    f.render_widget(input, chunks[1]);
    
    let password_block = Block::default()
        .borders(Borders::ALL)
        .border_type(BorderType::Rounded)
        .border_style(password_style);

    let input = Paragraph::new(Text::from(Line::from(vec![
        Span::styled("* Password: ", Style::default().fg(Color::Yellow)),
        Span::styled(app_lock.input.1.value().to_string(), password_style)
    ])))
    .block(password_block)
    .scroll((0, password_scroll as u16));

    f.render_widget(input, chunks[2]);

    let help_text = {
        if app_lock.failed_logins == 3 {
            Line::styled(format!("{}{}", HELP_TEXT.login.login_failed_lock, app_lock.timeout.get(&TimeoutType::Login).unwrap().counter), Style::default().fg(Color::Red))
        }
        else if app_lock.failed_logins > 0 {
            Line::styled(HELP_TEXT.login.login_failed, Style::default().fg(Color::Red))
        } else {
            Line::raw(HELP_TEXT.login.main)
        }
    };
    let help_block = Block::default();
    let help = Paragraph::new(help_text).block(help_block);
    f.render_widget(help, chunks[3]);
    
    if let Some(popup) = &app_lock.active_popup {
        match popup {
            Popup::LoginSuccessful => {
                let popup_rect = centered_rect(&f.size(), 28, 3)?;

                let login_successful_block = Block::default()
                    .borders(Borders::ALL)
                    .border_type(BorderType::Thick);

                let login_successful_popup = Paragraph::new(Text::from(
                    "Login successful."
                ))
                .alignment(Alignment::Center)
                .block(login_successful_block);

                f.render_widget(Clear, popup_rect);
                f.render_widget(login_successful_popup, popup_rect);
            }
            Popup::ServerUnavailable => {
                let popup_rect = centered_rect(&f.size(), 55, 7)?;

                let popup_chunks = Layout::default()
                    .direction(Direction::Vertical)
                    .constraints([
                        Constraint::Min(2),
                        Constraint::Percentage(100)
                    ])
                    .split(popup_rect.inner(&Margin::new(1, 1)));

                let popup_block = Block::default()
                    .borders(Borders::ALL)
                    .border_type(BorderType::Thick)
                    .style(Style::default().fg(Color::Red));
                
                let server_unavailable = Paragraph::new(Text::from(vec![
                    Line::raw("The server could not be reached."),
                    Line::raw("Would you like to login with limited functionality?")
                ]))
                .centered();

                let (yes_style, yes_borders, no_style, no_borders) =
                    match app_lock.action_sel {
                        None => (Style::default().fg(Color::DarkGray), BorderType::Rounded, Style::default().fg(Color::DarkGray), BorderType::Rounded),
                        Some(0) => (Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD), BorderType::Thick, Style::default().fg(Color::DarkGray), BorderType::Rounded),
                        Some(1) => (Style::default().fg(Color::DarkGray), BorderType::Rounded, Style::default().fg(Color::Yellow).add_modifier(Modifier::BOLD), BorderType::Thick),
                        _ => panic!()
                    };

                let action_chunks = Layout::default()
                    .direction(Direction::Horizontal)
                    .constraints([
                        Constraint::Percentage(20),
                        Constraint::Percentage(20),
                        Constraint::Percentage(20),
                        Constraint::Percentage(20),
                        Constraint::Percentage(20),
                    ])
                    .split(popup_chunks[1]);
                
                let yes_action_block = Block::default()
                    .borders(Borders::ALL)
                    .border_type(yes_borders);

                let yes_action = Paragraph::new("Yes")
                    .centered()
                    .block(yes_action_block)
                    .style(yes_style);
                
                let no_action_block = Block::default()
                    .borders(Borders::ALL)
                    .border_type(no_borders);
                    
                let no_action = Paragraph::new("No")
                    .centered()
                    .block(no_action_block)
                    .style(no_style);
                
                f.render_widget(Clear, popup_rect);
                f.render_widget(popup_block, popup_rect);
                f.render_widget(server_unavailable, popup_chunks[0]);
                f.render_widget(yes_action, action_chunks[1]);
                f.render_widget(no_action, action_chunks[3]);
            }
            _ => { unimplemented!() }
        }
    }
    Ok(())
}