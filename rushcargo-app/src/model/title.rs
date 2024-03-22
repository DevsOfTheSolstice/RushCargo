use std::fs;
use anyhow::Result;
use crate::{
    BIN_PATH,
    model::app::App,
};

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
        let height = 3.0;
        let width = 5.0;
        let depth = 3.0;
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

impl App {
    pub fn update_cube(&mut self) {
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

                (*x1, *y1, *z1) = (x, y, z);

                counter += 1;
            }

            title.cube.A += 0.1;
            title.cube.B += 0.1;
            //title.cube.C += 0.1;
        }
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
}