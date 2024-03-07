use std::collections::HashMap;
use anyhow::{Result, anyhow};
use ratatui::widgets::{List, ListState};
use std::time::{Duration, Instant};
use tui_input::Input;
use crate::{
    HELP_TEXT,
    model::{
        app_list::ListData,
        common::{Popup, UserType, InputFields, InputMode, Screen, TimeoutType, Timer},
        settings::SettingsData,
        title::TitleData,
    }
};

pub struct App {
    pub input: InputFields,
    pub input_mode: InputMode,
    pub failed_logins: u8,
    pub timeout: HashMap<TimeoutType, Timer>,
    pub settings: SettingsData,
    pub title: Option<Box<TitleData>>,
    pub list: ListData,
    pub active_user: Option<UserType>,
    prev_screen: Option<Screen>,
    pub active_screen: Screen,
    pub active_popup: Option<Popup>,
    pub hold_popup: bool,
    pub should_clear_screen: bool,
    pub should_quit: bool,
}

impl App {
    pub fn default() -> Self {
        let settings = SettingsData::from_file();
        if let Err(e) = settings {
            panic!("Error on settings data build: {}", e);
        }
        /*let title = TitleData::from_file();
        if let Err(e) = title {
            panic!("Error on title data build: {}", e);
        }*/
        App {
            input: InputFields(Input::default(), Input::default()),
            input_mode: InputMode::Normal,
            failed_logins: 0,
            timeout: HashMap::new(),
            settings: settings.unwrap(),
            title: None,
            list: ListData::default(),
            active_user: None,
            prev_screen: None,
            active_screen: Screen::Login,
            active_popup: None,
            hold_popup: false,
            should_clear_screen: false,
            should_quit: false,
        }
    }
}

impl App {
    pub fn enter_screen(&mut self, screen: &Screen) {
        self.should_clear_screen = true;
        self.cleanup();
        match screen {
            Screen::Title => {
                let title = TitleData::from_file();
                if let Err(e) = title {
                    panic!("Error on title data build: {}", e);
                }
 
                self.active_screen = Screen::Title;
                self.title = Some(Box::new(title.unwrap()));
                self.add_timeout(10, 0, TimeoutType::CubeTick);
            }
            Screen::Settings => {
                self.active_screen = Screen::Settings;
            }
            Screen::Login => {
                self.active_screen = Screen::Login;
                self.input_mode = InputMode::Editing(0);
                self.failed_logins = 0;
                self.active_user = None;
            }
            _ => {}
        }
    }

    fn cleanup(&mut self) {
        match self.prev_screen {
            Some(Screen::Title) => {
                self.title = None;
                self.list.state.0.select(None);
            }
            Some(Screen::Settings) => {
                self.list.state.0.select(None);
            }
            Some(Screen::Login) => {
                self.input.0.reset();
                self.input.1.reset();
                self.input_mode = InputMode::Normal;
            }
            Some(Screen::Trucker) => {}
            None => {}
        }
        self.prev_screen = Some(self.active_screen.clone());
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
                _ => {},
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

    fn update_cube(&mut self) {
        if let Some(title) = self.title.as_mut() {
                let mut counter = 0;
                for dot in title.cube.dot.iter() {
                let mut x = dot.x as f64;
                let mut y = dot.y as f64;
                let mut z = dot.z as f64;
                
                let x1 = &mut title.cube.rot_dot[counter].x;
                let y1 = &mut title.cube.rot_dot[counter].y;
                let z1 = &mut title.cube.rot_dot[counter].z;

                (x, y, z) = Self::rotate_x(title.cube.A, x as f64, y as f64, z as f64);
                (x, y, z) = Self::rotate_y(title.cube.B, x as f64, y as f64, z as f64);
                (x, y, z) = Self::rotate_z(title.cube.C, x as f64, y as f64, z as f64);
                //title.cube.rot_dot[counter].x = Self::calculate_x(title.cube.A, title.cube.B, title.cube.C, x, y, z);
                //title.cube.rot_dot[counter].y = Self::calculate_y(title.cube.A, title.cube.B, title.cube.C, x, y, z);
                //title.cube.rot_dot[counter].z = Self::calculate_z(title.cube.A, title.cube.B, title.cube.C, x, y, z);
                (*x1, *y1, *z1) = (x, y, z);

                counter += 1;
            }

            //println!("{}", title.cube.rot_dot.x);
            //println!("{}", title.cube.rot_dot.y);
            //println!("{}", title.cube.rot_dot.z);
            //println!();

            title.cube.A += 0.1;
            title.cube.B += 0.1;
            //title.cube.C += 0.1;

        }
    }
    
    /*fn calculate_x(A: f64, B: f64, C: f64, i: i8, j: i8, k: i8) -> f64 {
        j as f64 * A.sin() * B.sin() * C.cos() - k as f64 * A.cos() * B.sin() * C.cos() +
        j as f64 * A.cos() * C.sin() + k as f64 * A.sin() * C.sin() + i as f64 * B.cos() * C.cos()
    }*/
    
    fn calculate_x(A: f64, B: f64, C: f64, i: i8, j: i8, k: i8) -> f64 {
        i as f64 * C.cos() * B.cos() +
        j as f64 * (C.cos() * B.sin() * A.sin() - C.sin() * A.cos()) +
        k as f64 * (C.cos() * B.sin() * A.cos() + C.sin() * A.sin())
    }

    fn rotate_x(ang: f64, i: f64, j: f64, k: f64) -> (f64, f64, f64) {
        (
            i,
            j * ang.cos() + k * ang.sin(),
            k * ang.cos() - j * ang.sin()
        )
    }
    
    fn rotate_y(ang: f64, i: f64, j: f64, k: f64) -> (f64, f64, f64) {
        (
            i * ang.cos() - k * ang.sin(),
            j,
            i * ang.sin() + k.cos()
        )
    }

    fn rotate_z(ang: f64, i: f64, j: f64, k: f64) -> (f64, f64, f64) {
        (
            i * ang.cos() + j * ang.sin(),
            j * ang.cos() - i * ang.sin(),
            k
        )
    }

    fn calculate_y(A: f64, B: f64, C: f64, i: i8, j: i8, k: i8) -> f64 {
        j as f64 * A.cos() * C.cos() + k as f64 * A.sin() * C.cos() -
        j as f64 * A.sin() * B.sin() + C.sin() + k as f64 * A.cos() * B.sin() * C.sin() -
        i as f64 * B.cos() * C.sin()
    }

    fn calculate_z(A: f64, B: f64, C: f64, i: i8, j: i8, k: i8) -> f64 {
        k as f64 * A.cos() * B.cos() - j as f64 * A.sin() * B.cos() + i as f64 * B.sin()
    }
}