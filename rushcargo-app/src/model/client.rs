#[derive(Debug)]
pub struct Client {
    pub username: String,
    pub first_name: String,
    pub last_name: String,
}

pub struct ClientData {
    client: Client,
}

