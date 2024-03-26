pub struct HelpText {
    pub login: LoginHelpText,
    pub client: ClientHelpText,
}

impl HelpText {
    pub const fn default() -> Self {
        HelpText{
            login: LoginHelpText {
                main: "(Tab) switch input | (Esc) back",
                login_failed: "Login failed.",
                login_failed_lock: "Login failed. - Try again in: ",
            },
            client: ClientHelpText {
                main: "(Tab) select action | (Esc) back",
                lockers: "(Enter) select locker | (⬆) move up | (⬇) move down | (Esc) back",
                locker_packages: "(s) select package | (⬆) move up | (⬇) move down | (Enter) place order",
                order_main: "(Tab) select action",
                order_locker: "(Tab) switch input | (Enter) next | (Esc) back",
                order_locker_popup_normal: "Input the recipient's information.",
                sent_packages: "Select a package."
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
    pub order_main: &'static str,
    pub order_locker: &'static str,
    pub order_locker_popup_normal: &'static str,
    pub sent_packages: &'static str,
}