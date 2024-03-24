class FieldValueError(Exception):
    """
    Exception Raised for Invalid Values Used as Columns Data for a Given Table Group
    """

    def __init__(self, tableGroup: str, field: str, value: str):
        super().__init__(f"Invalid '{value}' at Column '{field}' for '{tableGroup}'\n")


class PlaceError(Exception):
    """
    Exception Raised for Invalid Place Names
    """

    def __init__(self, placeName: str):
        super().__init__(f"Invalid '{placeName}' as Place Name'\n")
