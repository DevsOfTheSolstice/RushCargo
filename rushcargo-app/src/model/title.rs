use crate::BIN_PATH;
use std::fs;
use anyhow::Result;

#[derive(Copy, Clone)]
pub struct Dot {
    pub char: char,
    pub x: f64,
    pub y: f64,
    pub z: f64,
}

impl std::ops::Neg for Dot {
    type Output = Self;

    fn neg(self) -> Self::Output {
        Self::Output {
            char: self.char,
            x: -self.x,
            y: -self.x,
            z: -self.x,
        }
    }
}

impl Dot {
    pub fn default() -> Self {
        Dot {
            char: '*',
            x: 0.0,
            y: 0.0,
            z: 0.0,
        }
    }
    pub fn new(x: f64, y: f64, z: f64) -> Self {
        Dot {
            char: '*',
            x,
            y,
            z
        }
    }
    pub fn new_with_char(char: char, x: f64, y: f64, z: f64) -> Self {
        Dot {
            char,
            x,
            y,
            z
        }
    }
}

#[derive(Clone)]
pub struct RenderDot {
    pub zval: f64,
    pub char: char,
}

impl std::default::Default for RenderDot {
    fn default() -> Self {
        RenderDot {
            zval: f64::MAX,
            char: ' ',
        }
    }
}

pub struct CubeData {
    pub A: f64,
    pub B: f64,
    pub C: f64,
    pub dot: [Dot;8],
    pub rot_dot: [Dot;8],
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
        let depth = 0.40;
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
                    [Dot::default(), Dot::default(), Dot::default(), Dot::default(),
                     Dot::default(), Dot::default(), Dot::default(), Dot::default()],
            }
        })
    }
}