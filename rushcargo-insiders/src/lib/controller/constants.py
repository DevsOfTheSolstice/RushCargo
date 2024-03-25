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
DICT_PROVINCE_NAME = getDictName("province")
DICT_REGION_NAME = getDictName("region")
DICT_CITY_NAME = getDictName("city")
DICT_CITY_AREA_NAME = getDictName("area")

DICT_COUNTRY_NAME_ID = getDictNameId("country")
DICT_PROVINCE_NAME_ID = getDictNameId("province")
DICT_REGION_NAME_ID = getDictNameId("region")
DICT_CITY_NAME_ID = getDictNameId("city")
DICT_CITY_AREA_NAME_ID = getDictNameId("area")

DICT_COUNTRY_ID = getDictId("country")
DICT_PROVINCE_ID = getDictId("province")
DICT_REGION_ID = getDictId("region")
DICT_CITY_ID = getDictId("city")
DICT_CITY_AREA_ID = getDictId("area")

# All Handler Messages
ALL_SORT_BY_MSG = "How do you want to Sort it?"
ALL_DESC_MSG = "\nDo you want to Sort it in Descending Order?"

# Get Handler Messages
GET_FIELD_MSG = "\nWhich Field do you want to Compare?"
GET_VALUE_MSG = "Which Value do you want to Compare that Field with?"

# Add Handler Messages
ADD_MORE_MSG = "\nDo you want to Add More at this Location?"

# Modify Handler Messages
MOD_CONFIRM_MSG = "\nIs this the Row you want to Modify?"
MOD_FIELD_MSG = "Which Field do you want to Modify?"
MOD_VALUE_MSG = "Which New Value do you want to Assign it?"
MOD_NOTHING_MSG = "Nothing to Modify"

# Remove Handler Messages
RM_CONFIRM_MSG = "\nIs this the Row you want to Remove?"

# Program Exting Message
END_MSG = "\nExiting..."
