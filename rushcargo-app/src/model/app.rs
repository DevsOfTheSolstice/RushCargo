use std::collections::HashMap;
use sqlx::{Row, Pool, Postgres, PgPool};
use anyhow::{anyhow, Ok, Result};
use ratatui::widgets::{List, ListState};
use std::time::{Duration, Instant};
use tui_input::Input;
use crate::{
    HELP_TEXT,
    model::{
        app_list::ListData,
        app_table::{TableData, TableType},
        client::ClientData,
        trucker::TruckerData,
        common::{User, SubScreen, Popup, PackageData, InputFields, InputMode, Screen, TimeoutType, Timer},
        settings::SettingsData,
        title::TitleData,
    }
};

pub struct App {
    pub input: InputFields,
    pub input_mode: InputMode,
    pub action_sel: Option<u8>,
    pub failed_logins: u8,
    pub timeout: HashMap<TimeoutType, Timer>,
    pub settings: SettingsData,
    pub title: Option<Box<TitleData>>,
    pub list: ListData,
    pub table: TableData,
    //pub packages: Option<PackageData>,
    pub user: Option<User>,
    prev_screen: Option<Screen>,
    prev_popup: Option<Popup>,
    pub active_screen: Screen,
    pub active_popup: Option<Popup>,
    pub should_clear_screen: bool,
    pub should_quit: bool,
}

impl App {
    pub fn default() -> Self {
        let settings = SettingsData::from_file();
        if let Err(e) = settings {
            panic!("Error on settings data build: {}", e);
        }
        App {
            input: InputFields(Input::default(), Input::default()),
            input_mode: InputMode::Normal,
            action_sel: None,
            failed_logins: 0,
            timeout: HashMap::new(),
            settings: settings.unwrap(),
            title: None,
            list: ListData::default(),
            table: TableData::default(),
            //packages: None,
            user: None,
            prev_screen: None,
            prev_popup: None,
            active_screen: Screen::Login,
            active_popup: None,
            should_clear_screen: false,
            should_quit: false,
        }
    }
}

impl App {
    pub async fn enter_screen(&mut self, screen: Screen, pool: &PgPool) {
        self.should_clear_screen = true;
        self.cleanup_screen(&screen);
        self.active_screen = screen;

        match self.active_screen {
            Screen::Title => {
                let title = TitleData::from_file();
                if let Err(e) = title {
                    panic!("Error on title data build: {}", e);
                }
                self.title = Some(Box::new(title.unwrap()));
                self.add_timeout(10, 0, TimeoutType::CubeTick);
            }
            Screen::Login => {
                self.input_mode = InputMode::Editing(0);
                self.user = None;
            }
            Screen::Client(SubScreen::ClientMain) => {
                self.failed_logins = 0;
            }
            Screen::Client(SubScreen::ClientLockers) => {
                let client = self.get_client_mut();
                client.get_lockers_next(pool).await.expect("could not get initial lockers");
            }
            Screen::Client(SubScreen::ClientLockerPackages) => {
                self.get_client_mut().packages = Some(
                    PackageData {
                        viewing_packages: Vec::new(),
                        viewing_packages_idx: 0,
                        selected_packages: None,
                        active_package: None,
                    }
                );
                self.get_packages_next(TableType::LockerPackages, pool).await.expect("could not get initial packages");
            }
            Screen::Trucker(SubScreen::TruckerMain) => {
                self.active_screen = Screen::Trucker(SubScreen::TruckerMain);
            }
            Screen::Trucker(SubScreen::TruckerStatistics) => {
                self.active_screen = Screen::Trucker(SubScreen::TruckerStatistics)
            }
            Screen::Trucker(SubScreen::TruckerManagementPackets) => {
                self.active_screen = Screen::Trucker(SubScreen::TruckerManagementPackets)
            },
            
            _ => {}
        }
        
    }

    fn cleanup_screen(&mut self, next_screen: &Screen) {
        match self.prev_screen {
            Some(Screen::Title) => {
                self.title = None;
                self.list.state.0.select(None);
                self.timeout.remove(&TimeoutType::CubeTick);
            }
            Some(Screen::Settings) => {
                self.list.state.0.select(None);
            }
            Some(Screen::Login) => {
                self.input.0.reset();
                self.input.1.reset();
                self.input_mode = InputMode::Normal;
            }
            Some(Screen::Client(SubScreen::ClientMain)) => {
                self.action_sel = None;
            }
            Some(Screen::Client(SubScreen::ClientLockers)) => {
                if let Some(User::Client(client)) = &mut self.user {
                    client.viewing_lockers = None;
                    client.viewing_lockers_idx = 0;
                }
                self.table.state.select(None);
            }
            Some(Screen::Client(SubScreen::ClientLockerPackages)) => {
                self.get_client_mut().packages = None;
                self.table.state.select(None);
            }
            Some(Screen::Client(_)) => {}
            Some(Screen::Trucker(SubScreen::TruckerMain)) => {
                self.action_sel = None;
            }
            Some(Screen::Trucker(_)) => {}
            None => {}
        }
        self.prev_screen = Some(next_screen.clone());
    }

    pub async fn enter_popup(&mut self, popup: Option<Popup>, pool: &PgPool) {
        self.cleanup_popup(&popup);
        self.active_popup = popup;

        match self.active_popup {
            Some(Popup::ClientOrderLocker) => {
                self.input_mode = InputMode::Editing(0);
            }
            Some(Popup::ClientInputPayment) => {
                self.action_sel = Some(0);
                self.input_mode = InputMode::Editing(0);
            }
            _ => {}
        }

    }

    fn cleanup_popup(&mut self, next_popup: &Option<Popup>) {
        match self.prev_popup {
            Some(Popup::ClientOrderMain) => {
                self.action_sel = None;
            }
            Some(Popup::ClientOrderLocker) => {
                self.input.0.reset();
                self.input.1.reset();
                self.get_client_mut().send_to_locker_err = None;
                self.input_mode = InputMode::Normal;
            }
            Some(Popup::ClientInputPayment) => {
                self.input.0.reset();
                self.input.1.reset();
                self.list.state.0.select(None);
                self.action_sel = None;
            }
            _ => {}
        }
        self.prev_popup = next_popup.clone();
    }

    /// The timeout tick rate here should be equal or greater to the EventHandler tick rate.
    /// This is important because the minimum update time perceivable is defined by the EventHandler tick rate.
    pub fn add_timeout(&mut self, counter: u8, tick_rate: u16, timeout_type: TimeoutType) {
        if self.timeout.contains_key(&timeout_type) {
            panic!("cannot add timeout {:?} to list of timeouts since it already exists", timeout_type);
        }

        let tick_rate = Duration::from_millis(tick_rate as u64);

        self.timeout.insert(timeout_type, Timer{
            counter,
            tick_rate,
            last_update: Instant::now(),
        });
    }

    pub fn update_timeout_counter(&mut self, timeout_type: TimeoutType) {
        let timer = self.timeout.get_mut(&timeout_type)
            .unwrap_or_else(|| panic!("Tried to update a nonexistent timeout"));

        if timer.counter > 1 {
            timer.counter -= 1;
            timer.last_update = Instant::now();
            match timeout_type {
                TimeoutType::CubeTick => {
                    timer.counter = 10;
                    self.update_cube();
                },
                _ => {}
            }
        } else {
            match timeout_type {
                TimeoutType::Login => self.failed_logins = 0,
                _ => {}
            }
            if timeout_type != TimeoutType::CubeTick {
                self.timeout.remove(&timeout_type);
            }
        }
    }
    pub fn get_client_ref(&self) -> &ClientData {
        self.user.as_ref().map(|u|
            match u {
                User::Client(client) => client,
                _ => panic!(),
            }
        ).unwrap()
    }
    pub fn get_client_mut(&mut self) -> &mut ClientData {
        self.user.as_mut().map(|u|
            match u {
                User::Client(client) => client,
                _ => panic!(),
            }
        ).unwrap()
    }
    /*FIXME: i put the panics because otherwise it appears the error
    "match` arms have incompatible types expected `&PackageData`, found `()`"
    so the code should panic in case that the user is not of type User::Client
    so the match should only return a reference to PackageData.
    */
    pub fn get_client_packages_ref(&self) -> &PackageData {
        self.user.as_ref().map(|u|
            match u {
                User::Client(client) => client.packages.as_ref().unwrap(),
                _ => panic!("Expected User::Client"), //TODO: change this
            }
        ).unwrap()
    }
    pub fn get_client_packages_mut(&mut self) -> &mut PackageData {
        self.user.as_mut().map(|u|
            match u {
                User::Client(client) => client.packages.as_mut().unwrap(),
                _ => panic!("Expected User::Client"),
            }
        ).unwrap()
    }
}