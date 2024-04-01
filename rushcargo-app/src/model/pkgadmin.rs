use std::ops::Add;

use super::{
    common::{GetDBErr, PackageData, ShippingGuideData},
    db_obj::ShippingGuide,
};
use tui_input::Input;

#[derive(Debug)]
pub struct PkgAdmin {
    pub username: String,
    pub warehouse_id: i64,
    pub first_name: String,
    pub last_name: String,
}

#[derive(Debug)]
pub struct PkgAdminData {
    pub info: PkgAdmin,
    pub shipping_guides: Option<ShippingGuideData>,
    pub packages: Option<PackageData>,
    pub add_package: Option<AddPkgData>,
    pub get_db_err: Option<GetDBErr>,
}

#[derive(Debug)]
pub struct AddPkgData {
    pub content: Input,
    pub value: Input,
    pub weight: Input,
    pub length: Input,
    pub width: Input,
    pub height: Input,
    pub client: Input,
    pub locker: Input,
    pub branch: Input,
}

impl std::default::Default for AddPkgData {
    fn default() -> Self {
        AddPkgData {
            content: Input::default(),
            value: Input::default(),
            weight: Input::default(),
            length: Input::default(),
            width: Input::default(),
            height: Input::default(),
            client: Input::default(),
            locker: Input::default(),
            branch: Input::default(),
        }
    }
}