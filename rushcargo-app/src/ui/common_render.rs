use ratatui::{
    layout::{Constraint, Direction, Layout},
    prelude::{Alignment, Frame, Margin, Rect},
    style::{Color, Modifier, Style},
    text::{Line, Span, Text},
    widgets::{Block, BorderType, Borders, Clear, List, ListItem, Paragraph, Row, Table}
};
use rust_decimal::Decimal;
use anyhow::Result;
use std::{
    sync::{MutexGuard, Arc, Mutex},
    rc::Rc,
};
use crate::{
    model::{
        app::App,
        common::User,
    },
    ui::common_fn::{centered_rect, wrap_text, dimensions_string},
    HELP_TEXT
};

pub fn online_payment(app: &mut Arc<Mutex<App>>, chunks: &Rc<[Rect]>, f: &mut Frame) -> Result<()> {
    let help_block = Block::default().borders(Borders::TOP);
    let help = Paragraph::new(HELP_TEXT.client.order_payment).block(help_block);
    f.render_widget(help, chunks[2]);

    let mut app_lock = app.lock().unwrap();

    let popup_area = centered_rect(&chunks[1], 40, 9)?;

    let popup_block = Block::default()
        .borders(Borders::ALL)
        .border_type(BorderType::Thick)
        .title(Line::styled("Payment", Style::default().fg(Color::Cyan)))
        .title_alignment(Alignment::Center);

    f.render_widget(Clear, popup_area);
    f.render_widget(popup_block, popup_area);

    let input_chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Percentage(100),
            Constraint::Min(2),
            Constraint::Min(1),
            Constraint::Min(2),
        ])
        .split(popup_area.inner(&Margin::new(3, 1)));

    let width = input_chunks[1].width.max(3) - 3;
    let reference_scroll = app_lock.input.0.visual_scroll(width as usize - "* Reference. num: ".len());

    let reference_style = Style::default();
    
    let pay_amount =
        match &app_lock.user {
            Some(User::Client(client_data)) => {
                client_data.send_payment.as_ref().unwrap().amount
            }
            Some(User::PkgAdmin(pkgadmin_data)) => {
                pkgadmin_data.add_package.as_ref().unwrap().payment.as_ref().unwrap().amount
            }
            _ => panic!()
        };

    let pay_text = Paragraph::new(Text::from(vec![
        Line::from(vec![Span::raw("Amount to pay: "), Span::styled("USD ".to_string() + &pay_amount.to_string(), Style::default().fg(Color::Yellow))])
    ])).centered();

    f.render_widget(pay_text, input_chunks[0]);

    let reference_block = Block::default()
        .borders(Borders::BOTTOM)
        .border_type(BorderType::Rounded)
        .border_style(reference_style);

    let input = Paragraph::new(Text::from(Line::from(vec![
        Span::styled("* Reference num.: ", Style::default().fg(Color::Yellow)),
        Span::styled(app_lock.input.0.value(), reference_style)
    ])))
    .block(reference_block)
    .scroll((0, reference_scroll as u16));

    f.render_widget(input, input_chunks[1]);

    if let Some(1) = app_lock.action_sel {
        let bank_title = Line::styled("* Bank: ", Style::default().fg(Color::Yellow));
        f.render_widget(bank_title, input_chunks[3]);
        let bank_dropdown_area =
            Rect::new(
                input_chunks[3].x + "* Bank: ".len() as u16,
                input_chunks[3].y,
            25,
            5
            );

        let bank_dropdown_block = Block::default().borders(Borders::ALL);

        f.render_widget(Clear, bank_dropdown_area);
        f.render_widget(bank_dropdown_block, bank_dropdown_area);

        let banks_list_area = bank_dropdown_area.inner(&Margin::new(1, 1));

        let banks_list = List::new(
            app_lock.list.actions.payment_banks.clone()
        ).highlight_style(Style::default().fg(Color::Yellow).add_modifier(Modifier::REVERSED));

        f.render_stateful_widget(banks_list, banks_list_area, &mut app_lock.list.state.0);

    } else {
        let bank_title =
            Line::from(vec![
                Span::styled("* Bank: ", Style::default().fg(Color::Yellow)),
                Span::raw("▼ ──────────────────────")
            ]);

        f.render_widget(bank_title, input_chunks[3]);
        
        f.set_cursor(input_chunks[1].x
                        + (app_lock.input.0.visual_cursor().max(reference_scroll) - reference_scroll) as u16
                        + "* Reference num.: ".len() as u16
                        + 0,
                        input_chunks[1].y + 0,
                    );
    }
    Ok(())
}

pub fn order_successful(app: &mut Arc<Mutex<App>>, chunks: &Rc<[Rect]>, f: &mut Frame) -> Result<()> {
    let help_block = Block::default().borders(Borders::TOP);
    let help = Paragraph::new(HELP_TEXT.common.yay).block(help_block);
    f.render_widget(help, chunks[2]);

    let popup_area = centered_rect(&chunks[1], 28, 4)?;

    let popup_block = Block::default().borders(Borders::ALL).border_type(BorderType::Thick);

    let order_successful = Paragraph::new(Text::from(vec![
        Line::raw("Order placed"),
        Line::raw("successfully!")
    ]))
    .centered()
    .block(popup_block);

    f.render_widget(Clear, popup_area);
    f.render_widget(order_successful, popup_area);
    Ok(())
}