use ratatui::{
    prelude::*,
    widgets::{Bar, BarChart, BarGroup, Block, Borders, Paragraph},
};
use sqlx::{postgres::PgPool, Row};
use super::{
    common::Screen,
    app::App,
};

#[derive(Debug)]
pub enum BarChartType {
    Year,
    Month,
    Day,
}

struct Stats<'a> {
    total_trips: Vec<u64>,
    label: &'a str,
    bar_style: Style,
}

struct Base<'a> {
    months: [&'a str; 12],
    type_stat: [Stats<'a>; 3],
}

const TOTAL_STATS: &str = "Total stats";

impl<'a> Base<'a> {
    async fn new(pool: &PgPool) -> Result<Self, sqlx::Error> {
        let total_trips = vec![ //total_trips???
            Stats {
                label: "TotalTrips",
                total_trips: vec![],
                bar_style: Style::default().fg(Color::Blue),
            },
            Stats {
                label: "AVG",
                total_trips: vec![],
                bar_style: Style::default().fg(Color::Yellow),
            },
            Stats {
                label: "MAX",
                total_trips: vec![],
                bar_style: Style::default().fg(Color::Cyan),
            },
        ];

        let months = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        ];
        
        for(i, Stats) in Stats.iter_mut().enumerate() {
            let query = format!(
                "
                SELECT
                COUNT(*) AS total_trips,
                COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 1) AS January,
                COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 2) AS February,
                COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 3) AS March,
                COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 4) AS April,
                COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 5) AS May,
                COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 6) AS June,
                COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 7) AS July,
                COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 8) AS August,
                COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 9) AS September,
                COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 10) AS October,
                COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 11) AS November,
               COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 12) AS December
                FROM
                Orders.Automatic_Orders
                WHERE
                EXTRACT(YEAR FROM completed_date) = 2024;
                "
            );
            let rows = sqlx::query(&query)
                .bind(Stats.label)
                .fetch_all(pool)
                .await?;

            for row in rows {
                let total_trips: u64 = row.get("totalTrips");
                Stats.total_trips.push(total_trips);
            }
        }
        Ok(Base {
            Stats,
            months,
        })
    }
}

#[allow(clippy::cast_precision_loss)]
fn create_groups<'a>(base: &'a Base, combine_values_and_labels: bool) -> Vec<BarGroup<'a>> {
    app.months
        .iter()
        .enumerate()
        .map(|(i, &month)| {
            let bars: Vec<Bar> = app
                .total_trips
                .iter()
                .map(|c| {
                    let mut bar = Bar::default()
                        .value(c.total_trips[i])
                        .style(c.bar_style)
                        .value_style(
                            Style::default()
                                .bg(c.bar_style.fg.unwrap())
                                .fg(Color::Black),
                        );

                    if combine_values_and_labels {
                        bar = bar.text_value(format!(
                            "{} ({:.1} M)",
                            c.label,
                            (c.total_trips[i] as f64)
                        ));
                    } else {
                        bar = bar
                            .text_value(format!("{:.1}", (c.total_trips[i] as f64)))
                            .label(c.label.into());
                    }
                    bar
                })
                .collect();
            BarGroup::default()
                .label(Line::from(month).centered())
                .bars(&bars)
        })
        .collect()
}

#[allow(clippy::cast_possible_truncation)]
fn draw_bar_with_group_labels(f: &mut Frame, base: &Base, area: Rect) {
    const LEGEND_HEIGHT: u16 = 6;

    let groups = create_groups(app, false);

    let mut barchart = BarChart::default()
        .block(Block::default().title("Stats").borders(Borders::ALL))
        .bar_width(2)
        .group_gap(2);
    
    for group in groups {
        barchart = barchart.data(group);
    } 
    f.render_widget(barchart, area);

    if area.height >= LEGEND_HEIGHT && area.width >= TOTAL_STATS.len() as u16 + 2 {
        let legend_width = TOTAL_STATS.len() as u16;
        let legend_area = Rect {
            height: LEGEND_HEIGHT,
            width: legend_width,
            y: area.y,
            x: area.right() - legend_width,
        };
      
    }
}

