use clap::Parser;

/// [ RushCargo-App ]
/// 
/// A project for a fictional company that handles national and international shippings, including ocean and air freight.
/// 
/// DevsOfTheSolstice, March 2024.
#[derive(Parser, Debug)]
#[clap(author, version, about)]
pub struct AppArgs {
    /// postgres://USER:PASSWORD@URL:PORT/rushcargo
    #[arg(short, long)]
    pub db: String,
    /// http://URL:5000/graph-calc/warehouses
    #[arg(short, long)]
    pub graphserver: String,
}