from ..model.constants import (
    COUNTRY_TABLENAME,
    PROVINCE_TABLENAME,
    REGION_TABLENAME,
    CITY_TABLENAME,
    CITY_AREA_TABLENAME,
    WAREHOUSE_TABLENAME,
    WAREHOUSE_CONN_TABLENAME,
    BRANCH_TABLENAME,
)

# Action-related Commands
ADD = "add"
RM = "rm"
MOD = "mod"
GET = "get"
ALL = "all"
EXIT = "exit"

# Table-related Available Action Commands
ACTION_CMDS = [ADD, RM, MOD, GET, ALL, EXIT]

# Tables that can be Interacted with

# Location-related Commands
TABLE_LOCATION_CMD = "location"
TABLE_LOCATION_CMDS = [
    COUNTRY_TABLENAME,
    PROVINCE_TABLENAME,
    REGION_TABLENAME,
    CITY_TABLENAME,
    CITY_AREA_TABLENAME,
    WAREHOUSE_TABLENAME,
    BRANCH_TABLENAME,
]

# Table Group Commands
TABLE_GROUP_CMDS = [TABLE_LOCATION_CMD]

# ArgParse Commands
TABLE_ARGPARSE_CMDS = TABLE_LOCATION_CMDS
