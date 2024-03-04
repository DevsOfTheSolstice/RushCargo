use std::fs;
use std::mem::size_of;
use anyhow::{Result, Error};
use serde::{Serialize, Deserialize};
use crate::BIN_PATH;

#[derive(Serialize, Deserialize)]
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

impl SettingsData {
    pub fn from_file() -> Result<Self> {
        let file_contents = fs::read_to_string(
            BIN_PATH.lock().unwrap().clone() + "settings.bin")?;
        let settings_data = bincode::deserialize(&file_contents[..].as_bytes())?;
        Ok(settings_data)
    }

    pub fn iter(&self) -> SettingsDataIterator {
        SettingsDataIterator {
            settings_data: self,
            index: 0,
        }
    }
}

pub struct SettingsDataIterator<'a> {
    settings_data: &'a SettingsData,
    index: usize,
}

impl<'a> Iterator for SettingsDataIterator<'a> {
    type Item = bool;

    fn next(&mut self) -> Option<Self::Item> {
        self.index += 1;
        match self.index {
            1 => Some(self.settings_data.display_animation),
            _ => None
        }
    }
}