class ValueError(Exception):
    """
    Exception Raised for Invalid Values Used as Columns Data for a Given Table
    """

    def __init__(self, tableName: str, field: str, value: str):
        super().__init__(
            f"Invalid '{value}' at Column '{field}' for '{tableName}' Table\n"
        )


class LenError(Exception):
    """
    Exception Raised when Two Lists MUST have the Same Length, but don't
    """

    def __init__(self):
        super().__init__(f"Lists don't have the Same Length\n")


class LocationError(Exception):
    """
    Exception Raised when Geopy couldn't Find a Given Location for a Specific Address Type
    """

    def __init__(self, locationName, locationType):
        super().__init__(
            f"Geopy didn't Find '{locationName}' with Address Type of '{locationType}'\n"
        )


class RowNotFound(Exception):
    """
    Exception Raised when a Query MUST Return at Least One Coincidence, but it doesn't
    """

    def __init__(self, tableName: str, field: str, value: str):
        super().__init__(
            f"'{value}' Not Found at Column '{field}' for '{tableName}' Table\n"
        )
