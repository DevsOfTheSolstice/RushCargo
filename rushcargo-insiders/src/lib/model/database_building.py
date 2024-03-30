from psycopg import sql

from rich.prompt import IntPrompt, Prompt

from .classes import Building, Warehouse, Branch
from .constants import *
from .exceptions import BuildingNameAssigned
from .database import console
from .database_tables import (
    SpecializationTable,
    noCoincidence,
    insertedRow,
    getTable,
    uniqueInsertedMult,
)
from .database_connections import WarehouseConnectionTable

from ..controller.constants import DICT_PROVINCE_ID, DICT_REGION_ID, DICT_CITY_ID

from ..geocoding.constants import NOMINATIM_LATITUDE, NOMINATIM_LONGITUDE

from ..io.validator import isAddressValid, isEmailValid, clear

from ..terminal.constants import MOD_VALUE_MSG


def fullBuildingName(tableName: str, buildingName: str) -> str:
    """
    Function to Get the Full Building Name

    :param str tableName: Building Table Name at Remote Database
    :param str name: Building Name (without its Type)
    :return: Full Building Name
    :rtype: str
    """

    buildingType = None

    # Assign Building Type Name
    if tableName == WAREHOUSE_TABLENAME:
        buildingType = "Warehouse"

    elif tableName == BRANCH_TABLENAME:
        buildingType = "Branch"

    return f"{buildingType} {buildingName}"


def askBuildingValue(tableName: str, field: str):
    """
    Function to Get and Check a Building-related Field

    :param str tableName: Building Table Name at Remote Database
    :param str field: Building Field
    :return: Building Field Value
    :rtype: string
    """

    value = None

    if field == BUILDING_PHONE:
        value = str(IntPrompt.ask(MOD_VALUE_MSG))

    elif field == BUILDING_EMAIL:
        value = Prompt.ask(MOD_VALUE_MSG)

        # Check Building Email and Get its Normalized Form
        value = isEmailValid(value)

    elif field == BUILDING_NAME:
        value = Prompt.ask(MOD_VALUE_MSG)

        isAddressValid(BUILDING_TABLENAME, field, value)

        # Get Full Building Name
        value = fullBuildingName(tableName, value)

    return value


def getCoords(lat: float, lon: float) -> str:
    """
    Function to Get a String with the Latitude and Longitude Coordinates

    :param float lat: Latitude Coordinate
    :param float lon: Longitude Coordinate
    :return: String that Contains both Coordinates
    :rtype: str
    """

    return f"{lat}\n{lon}"


class BuildingTable(SpecializationTable):
    """
    Class that Handles the SQL Operations related to the Remote SQL Building Table
    """

    def __init__(self, tableName: str, tablePKFKName: str, remoteCursor):
        """
        Building Remote Table Class Constructor

        :param str tableName: Building Specialization Table Name
        :param str tablePKFKName: Building Specialization Primary Key Foreign Key Field Name
        :param Cursor remoteCursor: Remote Database Connection Cursor
        """

        # Initialize Specialization Table Class
        super().__init__(
            tableName,
            BUILDING_TABLENAME,
            tablePKFKName,
            BUILDING_ID,
            remoteCursor,
        )

    def __insertQuery(self):
        """
        Method that Retuns a Query to Insert a New Building to its Remote Table

        :return: SQL Query to Insert a New Building
        :rtype: Composed
        """

        return sql.SQL(
            "INSERT INTO {parentTableName} ({fields}) VALUES (%s,%s, %s, %s, %s, %s, %s)"
        ).format(
            parentTableName=sql.Identifier(self._parentTableName),
            fields=sql.SQL(",").join(
                [
                    sql.Identifier(BUILDING_ADDRESS_DESCRIPTION),
                    sql.Identifier(BUILDING_FK_CITY),
                    sql.Identifier(BUILDING_NAME),
                    sql.Identifier(BUILDING_EMAIL),
                    sql.Identifier(BUILDING_PHONE),
                    sql.Identifier(BUILDING_GPS_LATITUDE),
                    sql.Identifier(BUILDING_GPS_LONGITUDE),
                ]
            ),
        )

    def __buildingExists(self, cityId: int, buildingName: str) -> bool:
        """
        Method to Check if a Building Name has already been Assigned to Another One at the Given City ID

        :param int cityId: City ID where the Building is Located
        :param str buildingName: Building Name to Search for at the Given City ID
        :return: ``True`` if the Building Name has already been Assigned. Otherwise, ``False``
        :rtype: bool
        """

        buildingFields = [BUILDING_FK_CITY, BUILDING_NAME]
        buildingValues = [cityId, buildingName]

        # Check if Building Name has already been Inserted at the Given City ID
        if SpecializationTable._getMultParentTable(
            self, buildingFields, buildingValues
        ):
            uniqueInsertedMult(buildingValues, buildingFields, buildingValues)
            return True

        return False

    def _find(self, cityId: int, buildingName: str) -> Building | None:
        """
        Method to Find a Building at its Remote Table based on its Name and the City ID where It's Located

        :param int cityId: City ID where the Building is Located
        :param str buildingName: Building Name to Search for at the Given City ID
        :return: Building Object if Found. Otherwise, ``None``
        :rtype: Building if Found. Otherwise, NoneType
        """

        # Get Building from its Remote Table
        if not SpecializationTable._getMultParentTable(
            self, [BUILDING_FK_CITY, BUILDING_NAME], [cityId, buildingName]
        ):
            return None

        # Get Building Object from the Fetched Item
        return Building.fromFetchedItem(self._items[0])

    def _add(self, location: dict, buildingName: str) -> None:
        """
        Method to Insert a New Building to the Building Table

        :param dict location: Location Dictionary that Contains All the Information Related to the Building Location
        :param str buildingName: Building Name to Insert
        :returns: None
        :rtype: NoneType
        :raises BuildingNameAssigned: Raised if the Building Name of the that's being Inserted is Already Inserted to ANother Building at the Same City ID
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Check if the Building Name for the Given City ID Already Exists
        if self.__buildingExists(location[DICT_CITY_ID], buildingName):
            raise BuildingNameAssigned(buildingName, location[DICT_CITY_ID])

        # Ask for New Building Fields
        console.print("Adding New Building...", style="caption")
        buildingPhone = IntPrompt.ask("Enter Building Phone Number")
        buildingEmail = Prompt.ask("Enter Building Email")
        addressDescription = Prompt.ask("Enter Building Address Description")

        # Check Building Building Email and Address Description
        isEmailValid(buildingEmail)
        isAddressValid(
            self._tableName, BUILDING_ADDRESS_DESCRIPTION, addressDescription
        )

        # Get Query to Insert the Building to its Remote Table
        query = self.__insertQuery()

        # Execute the Query
        try:
            self._c.execute(
                query,
                [
                    addressDescription,
                    location[DICT_CITY_ID],
                    buildingName,
                    buildingEmail,
                    buildingPhone,
                    location[NOMINATIM_LATITUDE],
                    location[NOMINATIM_LONGITUDE],
                ],
            )
            insertedRow(buildingName, self._parentTableName)

        except Exception as err:
            raise err


class WarehouseTable(BuildingTable):
    """
    Class that Handles the SQL Operations related to the Remote SQL Warehouse Table
    """

    def __init__(self, remoteCursor):
        """
        Warehouse Remote Table Class Constructor

        :param Cursor remoteCursor: Remote Database Connection Cursor
        """

        # Initialize Building Table Class
        super().__init__(
            WAREHOUSE_TABLENAME,
            WAREHOUSE_ID,
            remoteCursor,
        )

    def __print(self) -> None:
        """
        Method that Prints the Warehouses Fetched from its Remote Table

        :return: Nothing
        :rtype: NoneType
        """

        # Number of Warehouses to Print
        nRows = len(self._items)

        # Initialize Rich Table
        table = getTable("Warehouse", nRows)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Coords", justify="left", max_width=COORDINATE_NCHAR)
        table.add_column("Phone", justify="left", max_width=CONTACT_NCHAR)
        table.add_column("Email", justify="left", max_width=CONTACT_NCHAR)
        table.add_column("City ID", justify="left", max_width=ID_NCHAR)

        for item in self._items:
            # Intialize Warehouse from Fetched Item
            w = Warehouse.fromFetchedItem(item)

            # Add Row to Rich Table
            table.add_row(
                str(w.buildingId),
                w.buildingName,
                getCoords(w.gpsLatitude, w.gpsLongitude),
                str(w.phone),
                w.email,
                str(w.cityId),
            )

        console.print(table)

    def __insertQuery(self):
        """
        Method that Retuns a Query to Insert a New Warehouse to its Remote Table

        :return: SQL Query to Insert a New Warehouse
        :rtype: Composed
        """

        return sql.SQL("INSERT INTO {tableName} ({field}) VALUES (%s)").format(
            tableName=sql.Identifier(self._tableName),
            field=sql.Identifier(self._tablePKFKName),
        )

    def add(self, location: dict, buildingName: str) -> int:
        """
        Method to Insert a New Warehouse to the Warehouse Table

        :param dict location: Location Dictionary that Contains All the Information Related to the Warehouse Location
        :param str buildingName: Warehouse Name to Insert
        :returns: Warehouse Building ID
        :rtype: int
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Full Building Name
        buildingName = fullBuildingName(self._tableName, buildingName)

        # Insert Building to Building Table
        BuildingTable._add(self, location, buildingName)

        # Get Building Object of the Recently Inserted Warehouse Building
        b = BuildingTable._find(self, location[DICT_CITY_ID], buildingName)

        # Ask for the Warehouse Fields
        console.print("Adding New Warehouse...", style="caption")

        # Get Warehouse Insert Query
        warehouseQuery = self.__insertQuery()

        # Execute the Query to Insert the Warehouse
        try:
            self._c.execute(
                warehouseQuery,
                [b.buildingId],
            )
            insertedRow(b.buildingName, self._tableName)

            return b.buildingId

        except Exception as err:
            raise err

    def get(self, field: str, value, printItems: bool = True) -> bool:
        """
        Method to Filter Warehouses from its Remote Table based on a Given Field-Value Pair

        :param str field: Warehouse Field that will be Used to Compare in the Warehouse Table
        :param value: Value to Compare
        :param bool printItems: Specifies wheter to Print or not the Fetched Items. Default is ``True``
        :return: Returns ``True`` if One or More Items were Fetched. Otherwise, ``False``
        :rtype: bool
        """

        if printItems:
            # Clear Terminal
            clear()

        if not SpecializationTable._getTable(self, field, value, BUILDING_NAME):
            if printItems:
                noCoincidence()
            return False

        if printItems:
            self.__print()
        return True

    def find(self, warehouseId: int) -> Warehouse | None:
        """
        Method to Find a Warehouse at its Remote Table based on its ID

        :param str warehouseId: Warehouse ID to Search for
        :return: Warehouse Object if Found. Otherwise, ``None``
        :rtype: Warehouse if Found. Otherwise, NoneType
        """

        # Get Warehouse from its Remote Table
        if not SpecializationTable._getTable(self, WAREHOUSE_ID, warehouseId):
            return None

        # Get Warehouse Object from the Fetched Item
        return Warehouse.fromFetchedItem(self._items[0])

    def all(self, orderBy: str, desc: bool) -> None:
        """
        Method that Prints the All the Warehouses Stored at its Remote Table

        :param str orderBy: Warehouse Field that will be Used to Sort the Warehouse Table
        :param bool desc: Specificies wheter to Sort in Ascending Order (``False``) or in Descending Order (``True``)
        :return: Nothing
        :rtype: NoneType
        """

        # Fetch All Warehouses
        SpecializationTable._all(self, orderBy, desc)

        # Clear Terminal
        clear()

        # Print All Warehouses
        self.__print()

    def modify(self, warehouseId: int, field: str, value) -> None:
        """
        Method to Modify a Warehouse Field to its Remote Table

        :param int warehouseId: Warehouse ID from its Remote Table
        :param str field: Warehouse Field to Modify
        :param value: Warehouse Field Value to be Assigned
        :return: Nothing
        :rtype: NoneType

        NOTE: There's No Own Warehouse Field that can be Modified, Only the Ones Inherited from its Parent Table
        """

        # Modify Building Table Row Column
        SpecializationTable._modifyParentTable(self, warehouseId, field, value)

    def remove(self, warehouseId: int) -> None:
        """
        Method to Remove a Warehouse Row from its Remote Table

        :param int warehouseId: Warehouse ID from its Remote Table
        :return: Nothing
        :rtype: NoneType
        """

        SpecializationTable._remove(self, warehouseId)


class BranchTable(BuildingTable):
    """
    Class that Handles the SQL Operations related to the Remote SQL Branch Table
    """

    def __init__(self, remoteCursor):
        """
        Branch Remote Table Class Constructor

        :param Cursor remoteCursor: Remote Database Connection Cursor
        """

        # Initialize Building Table Class
        super().__init__(
            BRANCH_TABLENAME,
            BRANCH_ID,
            remoteCursor,
        )

    def __print(self) -> None:
        """
        Method that Prints the Branches Fetched from its Remote Table

        :return: Nothing
        :rtype: NoneType

        """
        # Number of Branches to Print
        nRows = len(self._items)

        # Initialize Rich Table
        table = getTable("Branch", nRows)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Coords", justify="left", max_width=COORDINATE_NCHAR)
        table.add_column("Phone", justify="left", max_width=CONTACT_NCHAR)
        table.add_column("Email", justify="left", max_width=CONTACT_NCHAR)
        table.add_column("Warehouse ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Distance", justify="left", max_width=DISTANCE_NCHAR)
        table.add_column("City ID", justify="left", max_width=ID_NCHAR)

        for item in self._items:
            # Intialize Branch from Fetched Item
            b = Branch.fromItemFetched(item)

            # Add Row to Rich Table
            table.add_row(
                str(b.buildingId),
                b.buildingName,
                getCoords(b.gpsLatitude, b.gpsLongitude),
                str(b.phone),
                b.email,
                str(b.warehouseConnection),
                str(b.routeDistance),
                str(b.cityId),
            )

        console.print(table)

    def __insertQuery(self):
        """
        Method that Retuns a Query to Insert a New Branch to its Remote Table

        :return: SQL Query to Insert a New Branch
        :rtype: Composed
        """

        return sql.SQL("INSERT INTO {tableName} ({fields}) VALUES (%s, %s, %s)").format(
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [
                    sql.Identifier(self._tablePKFKName),
                    sql.Identifier(BRANCH_FK_WAREHOUSE_CONNECTION),
                    sql.Identifier(BRANCH_ROUTE_DISTANCE),
                ]
            ),
        )

    def add(
        self,
        location: dict,
        buildingName: str,
        warehouseConnId: int,
        routeDistance: int,
    ) -> None:
        """
        Method to Insert a New Branch to the Branch Table

        :param dict location: Location Dictionary that Contains All the Information Related to the Branch Location
        :param str buildingName: Branch Name to Insert
        :param int warehouseConnId: Warehouse ID that will be Connected with the New Branch Inserted
        :param int routeDistance: Route Distance between the Branch and the Warehouse which is Connected with
        :returns: None
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Full Building Name
        buildingName = fullBuildingName(self._tableName, buildingName)

        # Insert Building to its Remote Table
        BuildingTable._add(self, buildingName)

        # Get Building Object of the Recently Inserted Branch Building
        b = BuildingTable._find(self, location[DICT_CITY_ID], buildingName)

        # Ask for the Branch Fields
        console.print("Adding New Branch...", style="caption")

        # Get Query to Insert Branch to its Remote Table
        branchQuery = self.__insertQuery()

        # Execute the Query to Insert the Branch
        try:
            self._c.execute(
                branchQuery,
                [b.buildingId, warehouseConnId, routeDistance],
            )
            insertedRow(b.buildingName, self._tableName)

        except Exception as err:
            raise err

    def get(self, field: str, value, printItems: bool = True) -> bool:
        """
        Method to Filter Branches from its Remote Table based on a Given Field-Value Pair

        :param str field: Branch Field that will be Used to Compare in the Branch Table
        :param value: Value to Compare
        :param bool printItems: Specifies wheter to Print or not the Fetched Items. Default is ``True``
        :return: Returns ``True`` if One or More Items were Fetched. Otherwise, ``False``
        :rtype: bool
        """

        if printItems:
            # Clear Terminal
            clear()

        if not SpecializationTable._getTable(self, field, value, BUILDING_NAME):
            if printItems:
                noCoincidence()
            return False

        if printItems:
            self.__print()
        return True

    def find(self, branchId: int) -> Branch | None:
        """
        Method to Find a Branch at its Remote Table based on its ID

        :param str provinceId: Branch ID to Search for
        :return: Branch Object if Found. Otherwise, ``None``
        :rtype: Branch if Found. Otherwise, NoneType
        """

        # Get Branch from its Remote Table
        if not SpecializationTable._getTable(self, BRANCH_ID, branchId):
            return None

        # Get Branch Object from the Fetched Item
        return Branch.fromFetchedItem(self._items[0])

    def all(self, orderBy: str, desc: bool) -> None:
        """
        Method that Prints the All the Branches Stored at its Remote Table

        :param str orderBy: Branches Field that will be Used to Sort the Branches Table
        :param bool desc: Specificies wheter to Sort in Ascending Order (``False``) or in Descending Order (``True``)
        :return: Nothing
        :rtype: NoneType
        """

        # Fetch All Branches
        SpecializationTable._all(self, orderBy, desc)

        # Clear Terminal
        clear()

        # Print All Branches
        self.__print()

    def modify(self, branchId: int, field: str, value) -> None:
        """
        Method to Modify a Branch Field to its Remote Table

        :param int branchId: Branch ID from its Remote Table
        :param str field: Branch Field to Modify
        :param value: Branch Field Value to be Assigned
        :return: Nothing
        :rtype: NoneType
        """

        # Modify Branch Table Row Columns
        if field == BRANCH_FK_WAREHOUSE_CONNECTION or field == BRANCH_ROUTE_DISTANCE:
            SpecializationTable._modifyTable(self, branchId, field, value)

        # Modify Building Table Row Column
        else:
            SpecializationTable._modifyParentTable(self, branchId, field, value)

    def remove(self, branchId: int) -> None:
        """
        Method to Remove a Branch Row from its Remote Table

        :param int branchId: Branch ID from its Remote Table
        :return: Nothing
        :rtype: NoneType
        """

        SpecializationTable._remove(self, branchId)
