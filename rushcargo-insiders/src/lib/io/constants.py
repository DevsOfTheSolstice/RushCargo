from ..model.constants import (
    COUNTRY_TABLENAME,
    PROVINCE_TABLENAME,
    REGION_TABLENAME,
    CITY_TABLENAME,
    CITY_AREA_TABLENAME,
    WAREHOUSE_TABLENAME,
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

# Territory-related Commands
TABLE_TERRITORY_CMD = "territory"
TABLE_TERRITORY_CMDS = [
    COUNTRY_TABLENAME,
    PROVINCE_TABLENAME,
    REGION_TABLENAME,
    CITY_TABLENAME,
    CITY_AREA_TABLENAME,
]

# Building-related Commands
TABLE_BUILDING_CMD = "building"
TABLE_BUILDING_CMDS = [WAREHOUSE_TABLENAME, BRANCH_TABLENAME]

# Table Group Commands
TABLE_GROUP_CMDS = [TABLE_TERRITORY_CMD, TABLE_BUILDING_CMD]

# ArgParse Commands
TABLE_ARGPARSE_CMDS = list(TABLE_TERRITORY_CMDS + TABLE_BUILDING_CMDS)
