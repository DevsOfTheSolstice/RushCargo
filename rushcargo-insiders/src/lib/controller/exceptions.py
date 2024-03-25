class RowNotFound(Exception):
    """
    Exception Raised when a Query MUST Return at Least One Coincidence, but it doesn't
    """

    def __init__(self, tableName: str, field: str, value: str):
        super().__init__(
            f"'{value}' Not Found at Column '{field}' in '{tableName}' Table\n"
        )


class InvalidLocation(Exception):
    """
    Exception Raised when the Location is not Located in a Given Parent Territory
    """

    def __init__(
        self, locationName: str, parentLocationName: str, parentLocationId: int
    ):
        super().__init__(
            f"There's No '{locationName}' Referencing to '{parentLocationName}' Table Row of ID '{parentLocationId}'\n"
        )


class BuildingFound(Exception):
    """
    Exception Raised when there's Already a Building with the Same Name at the Given City Area
    """

    def __init__(self, buildingName: str, cityAreaId: int):
        super().__init__(
            f"There's Already a Building Named as '{buildingName}' at City Area of ID '{cityAreaId}'\n"
        )


class WarehouseNotFound(Exception):
    """
    Exception Raised when there a Branch couldn't be Registered because there's no Warehouse for the Given City Area ID
    """

    def __init__(self, cityAreaId: int):
        super().__init__(
            f"Branch couldn't be Registered. There's no a Warehouse at City Area ID '{cityAreaId}'\n"
        )


class InvalidWarehouse(Exception):
    """
    Exception Raised when the Warehouse City Area is not the Same as the Given City Area ID
    """

    def __init__(self, cityAreaId: int):
        super().__init__(f"Warehouse is not at City Area ID '{cityAreaId}'\n")
