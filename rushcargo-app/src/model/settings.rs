pub struct SettingsData {
    pub display_animation: bool,
}

impl std::default::Default for SettingsData {
    fn default() -> Self {
        SettingsData {
            display_animation: true,
        }
    }
}