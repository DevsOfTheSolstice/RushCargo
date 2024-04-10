class RowNotFound(Exception):
    """
    Exception Raised when a Query MUST Return at Least One Coincidence, but it doesn't
    """

    def __init__(self, tableName: str, field: str, value: str):
        """
        RowNotFound Exception Constructor

        :param str tableName: Table Name that's is being Searched through
        :param str field: Table Field that's being Used to Compare the Rows
        :param str value: Value Used to Compare at the Given Field
        """

        super().__init__(
            f"'{value}' Not Found at Column '{field}' in '{tableName}' Table"
        )


class EmptyTable(Exception):
    """
    Exception Raised when a Table is Empty, but it shouldn't
    """

    def __init__(self, tableName: str):
        """
        EmptyTable Exception Constructor

        :param str tableName: Table Name that's is Empty
        """

        super().__init__(f"No Rows Found in '{tableName}' Table\n")


class InvalidLocation(Exception):
    """
    Exception Raised when the Location is not Located in a Given Parent Territory
    """

    def __init__(
        self, locationName: str, parentLocationTableName: str, parentLocationId: int
    ):
        """
        InvalidLocation Exception Constructor

        :param str locationName: Location Name that's is being Searched at its 'Parent Location'
        :param str parentLocationTableName: Supposed Parent Location Table Name where the Location that's being Searched should be Referencing to
        :param str parentLocationId: Parent Location ID at its Table
        """

        super().__init__(
            f"There's No '{locationName}' Referencing to '{parentLocationTableName}' Table Row of ID '{parentLocationId}'\n"
        )


class WarehouseNotFound(Exception):
    """
    Exception Raised when there's no Warehouse for the Given City ID
    """

    def __init__(self, cityId: int):
        """
        WarehouseNotFound Exception Constructor

        :param str cityId: City ID where the Warehouse was Searched for
        """

        super().__init__(f"Warehouse not Found at City ID '{cityId}'\n")


class MainWarehouseError(Exception):
    """
    Exception Raised when the Warehouse couldn't be Removed because It's the Main One at a Given Location
    """

    def __init__(self, locationTableName: str, locationId: int):
        """
        MainWarehouseError Exception Constructor

        :param str locationTableName: Location Table Name where the Warehouse is the Main One
        :param int locationId: Location ID at the Given Location Table where the Warehouse is the Main One
        """

        super().__init__(
            f"Warehouse is the Main One at the '{locationTableName}' Row ID '{locationId}'\n"
        )
