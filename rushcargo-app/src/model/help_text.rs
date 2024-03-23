pub struct HelpText {
    pub login: LoginHelpText,
    pub client: ClientHelpText,
}

impl HelpText {
    pub const fn default() -> Self {
        HelpText{
            login: LoginHelpText {
                main: "Press `TAB` to switch input.",
                login_failed: "Login failed.",
                login_failed_lock: "Login failed. - Try again in: ",
            },
            client: ClientHelpText {
                main: "Press `TAB` to switch actions, or `Esc` to go back.",
                lockers: "Select a locker.",
                locker_packages: "Select a package.",
                sent_packages: "Select a package.",
            },
        }
    }
}

pub struct LoginHelpText {
    pub main: &'static str,
    pub login_failed: &'static str,
    pub login_failed_lock: &'static str,
}

pub struct ClientHelpText {
    pub main: &'static str,
    pub lockers: &'static str,
    pub locker_packages: &'static str,
    pub sent_packages: &'static str,
}