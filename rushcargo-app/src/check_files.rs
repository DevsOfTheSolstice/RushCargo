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

const FILES: [&str; 2] = ["settings.bin", "title.bin"];

pub fn check_files() {
    let bin_path = BIN_PATH.lock().unwrap().clone();

    if !Path::new(bin_path.as_str()).exists() {
        panic!("Could not find the `bin` directory in the rushcargo-app directory");
    } else {
        for file in FILES {
            if !Path::new(&(bin_path.to_string() + file)).exists() {
                match file {
                    "settings.bin" => create_file(FileType::Settings, &bin_path).expect("Could not create file `settings.bin`"),
                    _ => panic!("The file `{}` was not included in the check_files() function or cannot be created automatically", file)
                }
            }
        }
    }
}

fn create_file(file_type: FileType, bin_path: &String) -> Result<(), std::io::Error> {
    match file_type {
        FileType::Settings => {
            let settings_data = SettingsData::default();
            let mut settings = File::create(bin_path.clone() + "settings.bin")?;
            settings.write_all(&bincode::serialize(&settings_data).unwrap())
        }
    }
}