from rich import box
from rich.theme import Theme

# Route Distances Debug Mode
ROUTES_DEBUG_MODE = False

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
        "mainTitle": "pale_turquoise1",
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

# ... for Countries Table Attributes
PHONE_PREFIX_NCHAR = 13

# Locations Scheme Name
LOCATIONS_SCHEME_NAME = "locations"

# Locations Scheme Tables Name
COUNTRIES_TABLE_NAME = "countries"
REGIONS_TABLE_NAME = "regions"
CITIES_TABLE_NAME = "cities"
BUILDINGS_TABLE_NAME = "buildings"
WAREHOUSES_TABLE_NAME = "warehouses"
BRANCHES_TABLE_NAME = "branches"

# Countries Table Columns
COUNTRIES_ID = "country_id"
COUNTRIES_NAME = "country_name"
COUNTRIES_PHONE_PREFIX = "phone_prefix"

# Regions ...
REGIONS_ID = "region_id"
REGIONS_NAME = "region_name"
REGIONS_FK_COUNTRY = "country_id"
REGIONS_FK_AIR_FORWARDER = "main_air_freight_forwarder"
REGIONS_FK_OCEAN_FORWARDER = "main_ocean_freight_forwarder"
REGIONS_FK_WAREHOUSE = "main_warehouse"

# Cities ...
CITIES_ID = "city_id"
CITIES_NAME = "city_name"
CITIES_FK_REGION = "region_id"
CITIES_FK_WAREHOUSE = "main_warehouse"

# Buildings ...
BUILDINGS_ID = "building_id"
BUILDINGS_NAME = "building_name"
BUILDINGS_EMAIL = "email"
BUILDINGS_PHONE = "phone"
BUILDINGS_GPS_LATITUDE = "gps_latitude"
BUILDINGS_GPS_LONGITUDE = "gps_longitude"
BUILDINGS_ADDRESS_DESCRIPTION = "address_description"
BUILDINGS_FK_CITY = "city_id"

# Warehouses ...
WAREHOUSES_ID = "warehouse_id"

# Branches ...
BRANCHES_ID = "branch_id"
BRANCHES_ROUTE_DISTANCE = "route_distance"
BRANCHES_FK_WAREHOUSE_CONNECTION = "warehouse_id"

# Connections Scheme Name
CONNECTIONS_SCHEME_NAME = "connections"

# Connections Scheme Tables Name
WAREHOUSES_CONN_TABLE_NAME = "warehouse_connections"

# Connections Scheme Views Name
WAREHOUSES_VIEW_NAME = "warehouses"
WAREHOUSES_RECEIVERS_VIEW_NAME = "warehouse_receivers"
RECEIVERS = "receivers"
WAREHOUSES_SENDERS_VIEW_NAME = "warehouse_senders"
SENDERS = "senders"
REGIONS_MAIN_WAREHOUSES_VIEW_NAME = "region_main_warehouses"
CITIES_MAIN_WAREHOUSES_VIEW_NAME = "city_main_warehouses"

# Warehouse Connections Table Columns
WAREHOUSES_CONN_ID = "connection_id"
WAREHOUSES_CONN_WAREHOUSE_FROM_ID = "warehouse_from_id"
WAREHOUSES_CONN_WAREHOUSE_TO_ID = "warehouse_to_id"
WAREHOUSES_CONN_ROUTE_DISTANCE = "route_distance"
WAREHOUSES_CONN_CONN_TYPE = "connection_type"

# Warehouse Receivers ...
RECEIVERS_WAREHOUSE_ID = "warehouse_id"
RECEIVERS_WAREHOUSE_CONN_ID = "connection_id"

# Warehouse Senders ...
SENDERS_WAREHOUSE_ID = "warehouse_id"
SENDERS_WAREHOUSE_CONN_ID = "connection_id"

# Warehouse Connection Types
CONN_TYPE_REGION = "Region"
CONN_TYPE_CITY = "City"

# Async Sleep Time in Seconds
ASYNC_SLEEP = 0.1
