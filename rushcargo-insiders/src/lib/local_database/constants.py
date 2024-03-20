# Local SQLite Databases Information
GEOPY_DATABASE_NAME = "geopy.db"

# GeoPy Location-related Table Names
GEOPY_COUNTRY_NAME_TABLENAME = "country_name"
GEOPY_COUNTRY_SEARCH_TABLENAME = "country_search"
GEOPY_REGION_NAME_TABLENAME = "region_name"
GEOPY_REGION_SEARCH_TABLENAME = "region_search"
GEOPY_SUBREGION_TABLENAME = "subregion_name"
GEOPY_SUBREGION_SEARCH_TABLENAME = "subregion_search"
GEOPY_CITY_NAME_TABLENAME = "city_name"
GEOPY_CITY_SEARCH_TABLENAME = "city_search"
GEOPY_CITY_AREA_NAME_TABLENAME = "area_name"
GEOPY_CITY_AREA_SEARCH_TABLENAME = "area_search"

# Maximum Amount of Locations at its GeoPy Table
GEOPY_COUNTRY_MAX = 50
GEOPY_REGION_MAX = 3 * GEOPY_COUNTRY_MAX
GEOPY_SUBREGION_MAX = 2 * GEOPY_REGION_MAX
GEOPY_CITY_MAX = 2 * GEOPY_SUBREGION_MAX
GEOPY_CITY_AREA_MAX = 3 * GEOPY_CITY_MAX

# Maximum Number of Searches related to a Single One Location
GEOPY_LOCATION_SEARCH_MAX = 10
