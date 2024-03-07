use crate::BIN_PATH;
use std::fs;
use anyhow::Result;

pub struct Dot {
    pub x: f64,
    pub y: f64,
    pub z: f64,
}

impl Dot {
    fn new(x: f64, y: f64, z: f64) -> Self {
        Dot {
            x,
            y,
            z
        }
    }
}

#[derive(Copy, Clone)]
pub struct RotDot {
    pub char: char,
    pub x: f64,
    pub y: f64,
    pub z: f64,
}

impl RotDot {
    pub fn default() -> Self {
        RotDot {
            char: '*',
            x: 0.0,
            y: 0.0,
            z: 0.0,
        }
    }
    pub fn new(char: char, x: f64, y: f64, z: f64) -> Self {
        RotDot {
            char,
            x,
            y,
            z
        }
    }
}

pub struct CubeData {
    pub A: f64,
    pub B: f64,
    pub C: f64,
    pub dot: [Dot;8],
    pub rot_dot: [RotDot;8],
}

pub struct TitleData {
    pub text: String,
    pub cube: CubeData,
}

impl TitleData {
    pub fn from_file() -> Result<Self> {
        let file_contents = fs::read_to_string(
            BIN_PATH.lock().unwrap().clone() + "title.bin")?;
            let text = bincode::deserialize(&file_contents[..].as_bytes())?;
        let height = 0.50;
        let width = 0.70;
        let depth = 0.50;
        Ok(TitleData {
            text,
            cube: CubeData {
                A: 0.0,
                B: 0.0,
                C: 0.0,
                dot:
                    [Dot::new(-width, height, depth), Dot::new(width, height, depth), Dot::new(width, -height, depth), Dot::new(-width, -height, depth),
                     Dot::new(-width, height, -depth), Dot::new(width, height, -depth), Dot::new(width, -height, -depth), Dot::new(-width, -height, -depth)],
                rot_dot:
                    [RotDot::default(), RotDot::default(), RotDot::default(), RotDot::default(),
                     RotDot::default(), RotDot::default(), RotDot::default(), RotDot::default()],
            }
        })
    }
}