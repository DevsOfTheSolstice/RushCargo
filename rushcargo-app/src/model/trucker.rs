#[derive(Debug)]

pub struct Trucker {
    pub username: String,
    pub first_name: String,
    pub last_name: String,
}

pub struct TruckerData {
    trucker: Trucker,
}