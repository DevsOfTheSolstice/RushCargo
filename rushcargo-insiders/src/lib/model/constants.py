from rich import box
from rich.theme import Theme

# Theme Styles
THEME = Theme(
    {
        "title": "italic pale_turquoise1",
        "header": "pale_turquoise1",
        "border": "pale_turquoise1",
        "caption": "dim italic grey93",
        "text": "grey93",
        "textAlt": "dim grey93",
        "warning": "deep_pink4",
        "success": "light_green",
    }
)

# Default Box Style
BOX_STYLE = box.ROUNDED

# Number of Characters to Print per Column for Common Table Attributes
ID_NCHAR = 10
DESCRIPTION_NCHAR = 20
CONTACT_NCHAR = 10

# ... for Location-related Tables
LOCATION_NAME_NCHAR = 20
COORDINATE_NCHAR = 10

# ... for Warehouse-related Attributes
WAREHOUSE_NCHAR = 20

# ... for Forwarder-related Attributes
FORWARDER_NCHAR = 20

# ... for Country Table Attributes
PHONE_PREFIX_NCHAR = 15

# Country Table Columns
COUNTRY_TABLENAME = "country"
COUNTRY_ID = "country_id"
COUNTRY_NAME = "country_name"
COUNTRY_PHONE_PREFIX = "phone_prefix"

# Province ...
PROVINCE_TABLENAME = "province"
PROVINCE_ID = "province_id"
PROVINCE_NAME = "province_name"
PROVINCE_FK_COUNTRY = "country_id"
PROVINCE_FK_AIR_FORWARDER = "main_air_freight_forwarder"
PROVINCE_FK_OCEAN_FORWARDER = "main_ocean_freight_forwarder"

# Region ...
REGION_TABLENAME = "region"
REGION_ID = "region_id"
REGION_NAME = "region_name"
REGION_FK_PROVINCE = "province_id"
REGION_FK_WAREHOUSE = "main_warehouse"

# City ...
CITY_TABLENAME = "city"
CITY_ID = "city_id"
CITY_NAME = "city_name"
CITY_FK_REGION = "region_id"

# City Area ...
CITY_AREA_TABLENAME = "city_area"
CITY_AREA_ID = "area_id"
CITY_AREA_NAME = "area_name"
CITY_AREA_DESCRIPTION = "area_description"
CITY_AREA_FK_CITY = "city_id"

# Building ...
BUILDING_TABLENAME = "building"
BUILDING_ID = "building_id"
BUILDING_NAME = "building_name"
BUILDING_EMAIL = "email"
BUILDING_PHONE = "phone"
BUILDING_GPS_LATITUDE = "gps_latitude"
BUILDING_GPS_LONGITUDE = "gps_longitude"
BUILDING_ADDRESS_DESCRIPTION = "address_description"
BUILDING_FK_CITY_AREA = "area_id"

# Warehouse ...
WAREHOUSE_TABLENAME = "warehouse"
WAREHOUSE_ID = "warehouse_id"

# Branch ...
BRANCH_TABLENAME = "branch"
BRANCH_ID = "branch_id"
BRANCH_RUTE_DISTANCE = "rute_distance"
BRANCH_FK_WAREHOUSE_CONNECTION = "warehouse_connection"
