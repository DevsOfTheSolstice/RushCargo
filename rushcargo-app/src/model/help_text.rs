pub struct HelpText {
    pub login: LoginHelpText,
}

impl HelpText {
    pub const fn default() -> Self {
        HelpText{
            login: LoginHelpText {
                main: "Press `Alt` to switch input.",
                login_failed: "Login failed.",
                login_failed_lock: "Login failed. - Try again in: ",
            }
        }
    }
}

pub struct LoginHelpText {
    pub main: &'static str,
    pub login_failed: &'static str,
    pub login_failed_lock: &'static str,
}