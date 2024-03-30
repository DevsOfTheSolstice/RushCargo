use super::{
    common::{GetDBErr, PackageData, ShippingGuideData},
    db_obj::ShippingGuide,
};

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
    pub get_db_err: Option<GetDBErr>,
}