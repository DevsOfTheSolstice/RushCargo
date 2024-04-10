from ..model.constants import (
    LOCATIONS_SCHEME_NAME,
    COUNTRIES_TABLE_NAME,
    REGIONS_TABLE_NAME,
    CITIES_TABLE_NAME,
    WAREHOUSES_TABLE_NAME,
    BRANCHES_TABLE_NAME,
)

# Exit Command
EXIT = "exit"

# Command Type Parser
CMD_TYPE = "cmdType"

# Action Type Commands
DB = "db"
GRAPH = "graph"

# Avalaible Main Commands
CMD_TYPE_CMDS = [DB, GRAPH, EXIT]

# Database-related Action Parsers
DB_ACTION = "action"
DB_SCHEME = "scheme"
DB_TABLE = "table"

# Graph-related Action Parser
GRAPH_TYPE = "type"
GRAPH_LEVEL = "level"

# Action-related Commands
DB_ADD = "add"
DB_RM = "rm"
DB_MOD = "mod"
DB_GET = "get"
DB_ALL = "all"

# Table-related Available Action Commands
DB_ACTION_CMDS = [DB_ADD, DB_RM, DB_MOD, DB_GET, DB_ALL, EXIT]

# Locations Scheme-related Commands
DB_LOCATIONS_SCHEME_CMD = LOCATIONS_SCHEME_NAME
DB_LOCATIONS_SCHEME_TABLE_CMDS = [
    COUNTRIES_TABLE_NAME,
    REGIONS_TABLE_NAME,
    CITIES_TABLE_NAME,
    WAREHOUSES_TABLE_NAME,
    BRANCHES_TABLE_NAME,
    EXIT,
]

# Scheme Commands
DB_SCHEME_CMDS = [DB_LOCATIONS_SCHEME_CMD, EXIT]

# Table Commands
DB_TABLE_CMDS = DB_LOCATIONS_SCHEME_TABLE_CMDS

# Graph Type Available Commands
GRAPH_TYPE_CMDS = [WAREHOUSES_TABLE_NAME]

# Graph Level Available Commands
GRAPH_LEVEL_CMDS = [COUNTRIES_TABLE_NAME, REGIONS_TABLE_NAME, CITIES_TABLE_NAME, EXIT]
