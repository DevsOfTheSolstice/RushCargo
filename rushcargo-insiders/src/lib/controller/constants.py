# Rich Logger Debug Mode
RICH_LOGGER_DEBUG_MODE = False

# Location Dictionary Key Types
DICT_NAME = "name"
DICT_NAME_ID = "name_id"
DICT_ID = "id"


# Functions that Returns Some Generic Dictionary Key-related Strings
def getDictName(locationName: str) -> str:
    return f"{locationName}_{DICT_NAME}"


def getDictNameId(locationName: str) -> str:
    return f"{locationName}_{DICT_NAME_ID}"


def getDictId(locationName: str) -> str:
    return f"{locationName}_{DICT_ID}"


# Location Dictionary Keys
DICT_COUNTRY_NAME = getDictName("country")
DICT_REGION_NAME = getDictName("region")
DICT_CITY_NAME = getDictName("city")

DICT_COUNTRY_NAME_ID = getDictNameId("country")
DICT_REGION_NAME_ID = getDictNameId("region")
DICT_CITY_NAME_ID = getDictNameId("city")

DICT_COUNTRY_ID = getDictId("country")
DICT_REGION_ID = getDictId("region")
DICT_CITY_ID = getDictId("city")
