#![allow(non_snake_case)]

mod check_files;
mod model;
mod update;
mod event;
mod tui;
mod ui;

use anyhow::Result;
use clap::Parser;
use ratatui::{ backend::CrosstermBackend, Terminal };
use model::{app::App, common::Screen, help_text::HelpText};
use update::update;
use event::EventHandler;
use tui::Tui;
use std::sync::{Arc, Mutex};
use lazy_static::lazy_static;

#[derive(Parser, Debug)]
#[command(version, about, long_about = None)]
struct Args {
    #[arg(short, long)]
    url: String,
}

const HELP_TEXT: HelpText = HelpText::default();

lazy_static! {
    static ref BIN_PATH: Mutex<String> = Mutex::new({
            let mut path = String::from(std::env::current_exe().unwrap().to_string_lossy());
            path = path[..=path.find("rushcargo-app").expect("could not find the `rushcargo-app` folder") + ("rushcargo-app").len()].to_string();
            if cfg!(windows){
                path.push_str("bin\\");
            } else {
                path.push_str("bin/");
            }
            path
        });
}

#[tokio::main]
async fn main() -> Result<()> {
    /*x{let mut title_file = std::fs::File::create(BIN_PATH.lock().unwrap().clone() + "title.bin")?;
    title_file.write_all(&bincode::serialize("    ____             __    ______                     
   / __ \\__  _______/ /_  / ____/___ __________ _____ 
  / /_/ / / / / ___/ __ \\/ /   / __ `/ ___/ __ `/ __ \\
 / _, _/ /_/ (__  ) / / / /___/ /_/ / /  / /_/ / /_/ /
/_/ |_|\\__,_/____/_/ /_/\\____/\\__,_/_/   \\__, /\\____/ 
                                        /____/        ").unwrap())?;
    }*/
    crate::check_files::check_files();

    let args = Args::parse();
    println!("{}", args.url);
    let pool = sqlx::postgres::PgPool::connect(&args.url).await?;

    let app = App::default();
    let mut app_arc = Arc::new(Mutex::new(app));

    let backend = CrosstermBackend::new(std::io::stderr());
    let terminal = Terminal::new(backend)?;
    let events = EventHandler::new(100, &app_arc);
    let mut tui = Tui::new(terminal, events);
    tui.enter()?;

    app_arc.lock().unwrap().enter_screen(Screen::Login, &pool).await;

    /*use sqlx::FromRow;
    let test = crate::model::db_obj::ShippingGuide::from_row(&sqlx::query(
        "SELECT guide.*,
        sender.username AS sender_username, sender.client_name AS sender_client_name, sender.last_name AS sender_last_name,
        receiver.username AS receiver_username, receiver.client_name AS receiver_client_name, receiver.last_name AS receiver_last_name
        FROM shipping_guide AS guide
        INNER JOIN natural_client AS sender ON guide.client_user_from=sender.username
        INNER JOIN natural_client AS receiver ON guide.client_user_to=receiver.username
        LIMIT 1
    ")
    .fetch_one(&pool).await?)?;

    panic!("{}", test.shipping_type);*/

    tui.draw(&mut app_arc)?;

    while !app_arc.lock().unwrap().should_quit {
        if let Ok(event) = tui.events.next() {
            update(&mut app_arc, &pool, event).await.unwrap_or_else(|error| panic!("{}", error));
            tui.draw(&mut app_arc)?;
        }
    }

    tui.exit()?;

    Ok(())
}