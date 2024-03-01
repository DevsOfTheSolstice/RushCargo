use std::time::{Duration, Instant};

#[derive(Debug, Clone)]
pub enum Screen {
    Login,
}

#[derive(Debug, Clone, Copy)]
pub enum TimeoutType {
    Resize,
    Login,
}

pub struct Timer {
    pub counter: u8,
    pub tick_rate: Duration,
    pub last_update: Instant,
}