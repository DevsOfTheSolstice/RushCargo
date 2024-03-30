pub struct HelpText {
    pub login: LoginHelpText,
    pub client: ClientHelpText,
    pub pkgadmin: PkgAdminHelpText,
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
                order_recipient: "(Tab) switch input | (Enter) next | (Esc) back",
                order_locker_popup_invalid: "Invalid username or locker ID",
                order_locker_popup_same_as_active: "The packages are already there",
                order_locker_popup_locker_weight_err: "Weight exceeded. Max: ",
                order_locker_popup_locker_count_err: "Package limit (5) exceeded",
                order_branch_popup_invalid: "Invalid username or branch ID.",
                order_delivery_popup_invalid: "The username is invalid or no delivery exists for the recipient's affiliated branch",
                order_delivery_failed_attempts: "3 failed attempts. - Timeout: ",
                order_delivery_no_compat: "No motorcyclist on the recipient's affiliated branch can deliver these packages",
                order_payment: "(Tab) open banks list | (Enter) complete order",
                sent_packages: "Select a package."
            },
            pkgadmin: PkgAdminHelpText {
                main: "(Tab) select action | (Esc) back",
                guides: "(Enter) view info | (a) Place guide order | (b) Reject guide | (Esc) back",
            },
            common: CommonHelpText {
                yay: ":D",
                render_err: "The terminal is too smol :(",
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
    pub order_recipient: &'static str,
    pub order_locker_popup_invalid: &'static str,
    pub order_locker_popup_same_as_active: &'static str,
    pub order_locker_popup_locker_weight_err: &'static str,
    pub order_locker_popup_locker_count_err: &'static str,
    pub order_branch_popup_invalid: &'static str,
    pub order_delivery_popup_invalid: &'static str,
    pub order_delivery_failed_attempts: &'static str,
    pub order_delivery_no_compat: &'static str,
    pub order_payment: &'static str,
    pub sent_packages: &'static str,
}

pub struct PkgAdminHelpText {
    pub main: &'static str,
    pub guides: &'static str,
}

pub struct CommonHelpText {
    pub yay: &'static str,
    pub render_err: &'static str,
}