use crate::BIN_PATH;
use std::path::Path;
use std::io::Write;
use std::fs::{
    File,
    create_dir
};
use crate::model::settings::SettingsData;

enum FileType {
    Settings
}

pub fn check_files() {
    let bin_path = BIN_PATH.lock().unwrap().clone();

    if !Path::new(bin_path.as_str()).exists() {
        create_dir(&bin_path).expect("Could not create directory `bin`");
        create_file(FileType::Settings, bin_path).expect("Could not create file `settings.bin`");
    }
}

fn create_file(file_type: FileType, bin_path: String) -> Result<(), std::io::Error> {
    match file_type {
        FileType::Settings => {
            let settings_data = SettingsData::default();
            let mut settings = File::create(bin_path + "settings.bin")?;
            settings.write_all(&bincode::serialize(&settings_data).unwrap())
        }
    }
}