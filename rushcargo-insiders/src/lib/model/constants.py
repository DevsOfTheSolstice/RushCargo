# Number of Characters to Print per Column for Common Table Attributes
ID_NCHAR = 7

# ... for Country Table Attributes
PHONE_PREFIX_NCHAR = 15
COUNTRY_NAME_NCHAR = 20

# Country Table Columns
COUNTRY_ID = "country_id"
COUNTRY_NAME = "country_name"
COUNTRY_PHONE_PREFIX = "phone_prefix"

# Region Table Columns
REGION_ID = "region_id"
REGION_FK_COUNTRY = "country_id"
REGION_FK_MAIN_AIR_FORWARDER = "main_air_freight_forwarder"
REGION_FK_MAIN_OCEAN_FORWARDER = "main_ocean_freight_forwarder"
REGION_NAME = "region_name"
