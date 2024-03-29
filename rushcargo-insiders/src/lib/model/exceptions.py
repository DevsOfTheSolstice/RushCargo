class LenError(Exception):
    """
    Exception Raised when Two Lists MUST have the Same Length, but don't
    """

    def __init__(self):
        """
        LenError Exception Constructor
        """
        super().__init__(f"Lists don't have the Same Length\n")


class BuildingNameAssigned(Exception):
    """
    Exception Raised when there's Already a Building with the Same Name at the Given City ID
    """

    def __init__(self, buildingName: str, cityId: int):
        """
        BuildingNameAssigned Exception Constructor

        :param str buildingName: Building Name that's Already Assigned at the Given City
        :param str cityId: City ID where the Building is Located
        """

        super().__init__(
            f"There's Already a Building Named as '{buildingName}' at City of ID '{cityId}'\n"
        )
