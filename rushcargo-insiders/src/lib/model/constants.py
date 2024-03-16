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

# ... for Location-related Tables
LOCATION_NAME_NCHAR = 20

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

# Region ...
REGION_TABLENAME = "region"
REGION_ID = "region_id"
REGION_NAME = "region_name"
REGION_FK_COUNTRY = "country_id"
REGION_FK_AIR_FORWARDER = "main_air_freight_forwarder"
REGION_FK_OCEAN_FORWARDER = "main_ocean_freight_forwarder"

# City ...
CITY_TABLENAME = "city"
CITY_ID = "city_id"
CITY_NAME = "city_name"
CITY_FK_REGION = "region_id"
CITY_FK_WAREHOUSE = "main_warehouse"

# Action-related Commands
ADD = "add"
RM = "rm"
MOD = "mod"
GET = "get"
ALL = "all"
EXIT = "exit"

# Table-related Available Action Commands
ACTION_CMDS = [ADD, RM, MOD, GET, ALL, EXIT]

# Available Tables that can be Interacted with
TABLE_CMDS = [COUNTRY_TABLENAME, REGION_TABLENAME, CITY_TABLENAME]
