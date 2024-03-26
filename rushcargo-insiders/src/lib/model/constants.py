from rich import box
from rich.theme import Theme

# Environment Variables
ENV_HOST = "HOST"
ENV_PORT = "PORT"
ENV_DBNAME = "DBNAME"
ENV_USER = "USER"
ENV_PASSWORD = "PASSWORD"
ENV_ORS_API_KEY = "ORS_API_KEY"

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
ID_NCHAR = 12
DESCRIPTION_NCHAR = 15
CONTACT_NCHAR = 10

# ... for Location-related Tables
LOCATION_NAME_NCHAR = 20
COORDINATE_NCHAR = 10
DISTANCE_NCHAR = 10

# ... for Warehouse-related Attributes
WAREHOUSE_NCHAR = 14

# ... for Forwarder-related Attributes
FORWARDER_NCHAR = 16

# ... for Country Table Attributes
PHONE_PREFIX_NCHAR = 13

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
PROVINCE_FK_WAREHOUSE = "main_warehouse"

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
CITY_FK_WAREHOUSE = "main_warehouse"

# City Area ...
CITY_AREA_TABLENAME = "city_area"
CITY_AREA_ID = "area_id"
CITY_AREA_NAME = "area_name"
CITY_AREA_DESCRIPTION = "area_description"
CITY_AREA_FK_CITY = "city_id"
CITY_AREA_FK_WAREHOUSE = "main_warehouse"

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

# Warehouse Connection
WAREHOUSE_CONN_TABLENAME = "warehouse_connection"
WAREHOUSE_CONN_ID = "connection_id"
WAREHOUSE_CONN_WAREHOUSE_FROM_ID = "warehouse_from_id"
WAREHOUSE_CONN_WAREHOUSE_TO_ID = "warehouse_to_id"
WAREHOUSE_CONN_ROUTE_DISTANCE = "route_distance"
WAREHOUSE_CONN_CONN_TYPE = "connection_type"

# Branch ...
BRANCH_TABLENAME = "branch"
BRANCH_ID = "branch_id"
BRANCH_ROUTE_DISTANCE = "route_distance"
BRANCH_FK_WAREHOUSE_CONNECTION = "warehouse_connection"

# Warehouse Connection Dictionary Fields from a Given Main Warehouses View
DICT_WAREHOUSES_COORDS = "coords"
DICT_WAREHOUSES_ID = "id"

# Warehouse Receivers ...
WAREHOUSES_RECEIVERS_VIEWNAME = "warehouse_receivers"
RECEIVERS = "receivers"
RECEIVERS_WAREHOUSE_ID = "warehouse_id"
RECEIVERS_WAREHOUSE_CONN_ID = "connection_id"

# Warehouse Senders ...
WAREHOUSES_SENDERS_VIEWNAME = "warehouse_senders"
SENDERS = "senders"
SENDERS_WAREHOUSE_ID = "warehouse_id"
SENDERS_WAREHOUSE_CONN_ID = "connection_id"

# Main Warehouses for a Given Location Type Views
PROVINCE_MAIN_WAREHOUSES = "province_main_warehouses"
REGION_MAIN_WAREHOUSES = "region_main_warehouses"
CITY_MAIN_WAREHOUSES = "city_main_warehouses"
CITY_AREA_MAIN_WAREHOUSES = "city_area_main_warehouses"

# Warehouse Connection Types
CONN_TYPE_PROVINCE = "Province"
CONN_TYPE_REGION = "Region"
CONN_TYPE_CITY = "City"
CONN_TYPE_AREA = "City Area"

# Async Sleep Time in Seconds
ASYNC_SLEEP = 0.1
