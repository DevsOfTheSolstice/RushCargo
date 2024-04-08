class GoToMenu(Exception):
    """
    Exception Raised when the User wants to Return to the Main Menu
    """

    def __init__(self):
        """
        GoToMenu Exception Constructor
        """

        super().__init__(f"Returning to the Main Menu...\n")


class FieldValueError(Exception):
    """
    Exception Raised for Invalid Values Used as Cell's Data at a Given Field
    """

    def __init__(self, tableGroup: str, field: str, value: str):
        """
        FieldValueError Exception Constructor

        :param str tableGroup: Table's Group that's Working On
        :param str field: Table Field that's being Checked
        :param str value: Value that's being Checked for the Given Table Field
        """

        super().__init__(f"Invalid '{value}' at Column '{field}' for '{tableGroup}'\n")


class PlaceError(Exception):
    """
    Exception Raised for Invalid Place Names
    """

    def __init__(self, placeName: str):
        """
        PlaceError Exception Constructor

        :param str placeName: Place Name that's being Checked
        """

        super().__init__(f"Invalid '{placeName}' as Place Name'\n")
