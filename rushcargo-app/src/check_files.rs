use crate::BIN_PATH;
use std::path::Path;
use std::io::{Cursor, Write};
use std::fs::{
    File,
    create_dir
};

enum FileType {
    Settings
}

pub fn check_files() {
    let bin_path = BIN_PATH.lock().unwrap().clone();

    if !Path::new(bin_path.as_str()).exists() {
        create_dir(&bin_path).expect("Could not create directory `bin`");
        create_file(FileType::Settings, bin_path);
    }
}

fn create_file(file_type: FileType, bin_path: String) -> Result<(), std::io::Error> {
    match file_type {
        FileType::Settings => {
            let mut settings = File::create(bin_path + "settings.bin")
                .expect("Could not create file `settings.bin`");
            settings.write_all("Hello".as_bytes())
        }
    }
}