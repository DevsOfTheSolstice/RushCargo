pub struct HelpText {
    pub login: LoginHelpText,
    pub client: ClientHelpText,
    pub trucker: TruckerHelpText,
    pub common: CommonHelpText,
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
                order_locker_popup_normal: "",
                order_locker_popup_invalid: "Invalid username or locker ID.",
                order_locker_popup_same_as_active: "The packages are already there.",
                order_locker_popup_locker_weight_err: "Weight exceeded. Max: ",
                order_locker_popup_locker_count_err: "Package limit (5) exceeded.",
                order_payment: "(Tab) open banks list | (Enter) complete order",
                sent_packages: "Select a package."
            },
                trucker: TruckerHelpText {
                main: "Press 'TAB' to swicth actions, or 'Esc' to go back",
                Statistics: "Select a type of Statistic",
                management_action: "Select packages to accept",
                route_action: "(⬆) move up | (⬇) move down | (Esc) back",
            },
            common: CommonHelpText {
                yay: ":D",
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
    pub order_locker_popup_invalid: &'static str,
    pub order_locker_popup_same_as_active: &'static str,
    pub order_locker_popup_locker_weight_err: &'static str,
    pub order_locker_popup_locker_count_err: &'static str,
    pub order_payment: &'static str,
    pub sent_packages: &'static str,
}

pub struct TruckerHelpText{
    pub main: &'static str,
    pub Statistics: &'static str,
    pub management_action: &'static str,
    pub route_action: &'static str,
}

pub struct CommonHelpText {
    pub yay: &'static str,
}