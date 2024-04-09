import asyncio

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

from ..controller.constants import DICT_CITY_ID

from ..geocoding.constants import NOMINATIM_LATITUDE, NOMINATIM_LONGITUDE

from ..io.validator import isAddressValid, isEmailValid

from ..terminal.constants import MOD_VALUE_MSG
from ..terminal.clear import clear


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
    if tableName == WAREHOUSES_TABLE_NAME:
        buildingType = "Warehouse"

    elif tableName == BRANCHES_TABLE_NAME:
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

    if field == BUILDINGS_PHONE:
        value = str(IntPrompt.ask(MOD_VALUE_MSG))

    elif field == BUILDINGS_EMAIL:
        value = Prompt.ask(MOD_VALUE_MSG)

        # Check Building Email and Get its Normalized Form
        value = isEmailValid(value)

    elif field == BUILDINGS_NAME:
        value = Prompt.ask(MOD_VALUE_MSG)

        isAddressValid(BUILDINGS_TABLE_NAME, field, value)

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


class BuildingsTable(SpecializationTable):
    """
    Class that Handles the SQL Operations related to the Remote SQL Buildings Table
    """

    def __init__(self, tableName: str, tablePKFKName: str, schemeName: str = None):
        """
        Buildings Remote Table Class Constructor

        :param str tableName: Building Specialization Table Name
        :param str tablePKFKName: Building Specialization Primary Key Foreign Key Field Name
        :param str schemeName: Scheme Name where the Building Specialization Table is Located. Default is ``None``
        :param Cursor remoteCursor: Remote Database Connection Cursor
        """

        # Initialize Specialization Table Class
        super().__init__(
            tableName,
            BUILDINGS_TABLE_NAME,
            tablePKFKName,
            BUILDINGS_ID,
            schemeName,
            LOCATIONS_SCHEME_NAME,
        )

    def __insertQuery(self):
        """
        Method that Retuns a Query to Insert a New Building to its Remote Table

        :return: SQL Query to Insert a New Building
        :rtype: Composed
        """

        return sql.SQL(
            "INSERT INTO {schemeName}.{parentTableName} VALUES (%s,%s, %s, %s, %s, %s, %s)"
        ).format(
            schemeName=sql.Identifier(self._schemeName),
            parentTableName=sql.Identifier(self._parentTableName),
            fields=sql.SQL(",").join(
                [
                    sql.Identifier(BUILDINGS_ADDRESS_DESCRIPTION),
                    sql.Identifier(BUILDINGS_FK_CITY),
                    sql.Identifier(BUILDINGS_NAME),
                    sql.Identifier(BUILDINGS_EMAIL),
                    sql.Identifier(BUILDINGS_PHONE),
                    sql.Identifier(BUILDINGS_GPS_LATITUDE),
                    sql.Identifier(BUILDINGS_GPS_LONGITUDE),
                ]
            ),
        )

    async def __buildingExists(self, aconn, cityId: int, buildingName: str) -> bool:
        """
        Asynchronous Method to Check if a Building Name has already been Assigned to Another One at the Given City ID

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int cityId: City ID where the Building is Located
        :param str buildingName: Building Name to Search for at the Given City ID
        :return: ``True`` if the Building Name has already been Assigned. Otherwise, ``False``
        :rtype: bool
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        buildingFields = [BUILDINGS_FK_CITY, BUILDINGS_NAME]
        buildingValues = [cityId, buildingName]

        # Check if Building Name has already been Inserted at the Given City ID
        await asyncio.gather(
            SpecializationTable._getMultParentTable(
                self, aconn.cursor(), buildingFields, buildingValues
            )
        )

        if self._items == None:
            return False

        uniqueInsertedMult(buildingValues, buildingFields, buildingValues)
        return True

    def __getFetchedObjects(self) -> list[Building]:
        """
        Method to Get a List of Fetched Buildings Objects from ``self_items``

        :return: List of Fetched Buildings Objects
        :rtype: list
        """

        buildingsList = []

        for item in self._items:
            # Intialize Building from the SQL Fetched Row
            b = Building.fromFetchedItem(item)
            buildingsList.append(b)

        return buildingsList

    async def _getMult(
        self, aconn, fields: list[str], values: list
    ) -> list[Building] | None:
        """
        Asynchronous Method to Filter Buildings from its Remote Table based on Some Given Field-Value Pair

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param list fields: Region Fields that will be Used to Compare in the Region Table
        :param list values: Values to Compare
        :return: List of Fetched Buildings Objects if there's at Least One Coincidence. Otherwise, ``None``
        :rtype: list if there's at Least One Coincidence. Otherwise, NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Exceute the Query
        await asyncio.gather(
            SpecializationTable._getMultParentTable(
                self, aconn.cursor(), fields, values
            )
        )

        # Get the Regions Objects from the Fetched Regions
        regionsList = self.__getFetchedObjects()

        return None if len(regionsList) == 0 else regionsList

    async def _findMult(self, aconn, cityId: int, buildingName: str) -> Building | None:
        """
        Asynchronous Method to Find a Building at its Remote Table based on its Name and the City ID where It's Located

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int cityId: City ID where the Building is Located
        :param str buildingName: Building Name to Search for at the Given City ID
        :return: Building Object if Found. Otherwise, ``None``
        :rtype: Building if Found. Otherwise, NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Building from its Remote Table
        getTask = asyncio.create_task(
            self._getMult(
                aconn, [BUILDINGS_FK_CITY, BUILDINGS_NAME], [cityId, buildingName]
            )
        )
        await asyncio.gather(getTask)
        building = getTask.result()

        # Get Building Object from the Fetched Item
        if building == None:
            return None

        return building[0]

    async def _add(self, aconn, location: dict, buildingName: str) -> None:
        """
        Asynchronous Method to Insert a New Building to the Building Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param dict location: Location Dictionary that Contains All the Information Related to the Building Location
        :param str buildingName: Building Name to Insert
        :returns: None
        :rtype: NoneType
        :raises BuildingNameAssigned: Raised if the Building Name of the that's being Inserted is Already Inserted to Another Building at the Same City ID
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Check if the Building Name for the Given City ID Already Exists
        existsTask = asyncio.create_task(
            self.__buildingExists(aconn, location[DICT_CITY_ID], buildingName)
        )
        await asyncio.gather(existsTask)

        if existsTask.result():
            raise BuildingNameAssigned(buildingName, location[DICT_CITY_ID])

        # Ask for New Building Fields
        console.print("\nAdding New Building...", style="caption")
        buildingPhone = IntPrompt.ask("Enter Building Phone Number")
        buildingEmail = Prompt.ask("Enter Building Email")
        addressDescription = Prompt.ask("Enter Building Address Description")

        # Check Building Building Email and Address Description
        isEmailValid(buildingEmail)
        isAddressValid(
            self._tableName, BUILDINGS_ADDRESS_DESCRIPTION, addressDescription
        )

        # Get Query to Insert the Building to its Remote Table
        query = self.__insertQuery()

        # Execute the Query
        await asyncio.gather(
            aconn.cursor().execute(
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
        )
        insertedRow(buildingName, self._parentTableName)


class WarehousesTable(BuildingsTable):
    """
    Class that Handles the SQL Operations related to the Remote SQL Warehouses Table
    """

    def __init__(self):
        """
        Warehouses Remote Table Class Constructor
        """

        # Initialize Building Table Class
        super().__init__(WAREHOUSES_TABLE_NAME, WAREHOUSES_ID, LOCATIONS_SCHEME_NAME)

    def __getFetchedObjects(self) -> list[Warehouse]:
        """
        Method to Get a List of Fetched Warehouses Objects from ``self_items``

        :return: List of Fetched Warehouses Objects
        :rtype: list
        """

        warehousesList = []

        for item in self._items:
            # Intialize Warehouse from the SQL Fetched Row
            w = Warehouse.fromFetchedItem(item)
            warehousesList.append(w)

        return warehousesList

    def __print(self, warehousesList: list[Warehouse]) -> None:
        """
        Method that Prints the Warehouses Fetched from its Remote Table

        :param list warehousesList: Fetched Warehouses Objects to Print
        :return: Nothing
        :rtype: NoneType
        """

        # Number of Warehouses to Print
        nRows = len(warehousesList)

        # Initialize Rich Table
        table = getTable("Warehouses", nRows)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Coords", justify="left", max_width=COORDINATE_NCHAR)
        table.add_column("Phone", justify="left", max_width=CONTACT_NCHAR)
        table.add_column("Email", justify="left", max_width=CONTACT_NCHAR)
        table.add_column("City ID", justify="left", max_width=ID_NCHAR)

        for w in warehousesList:
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

        return sql.SQL(
            "INSERT INTO {schemeName}.{tableName} ({field}) VALUES (%s)"
        ).format(
            schemeName=sql.Identifier(self._schemeName),
            tableName=sql.Identifier(self._tableName),
            field=sql.Identifier(self._tablePKFKName),
        )

    async def add(self, aconn, location: dict, buildingName: str) -> int:
        """
        Asynchronous Method to Insert a New Warehouse to the Warehouse Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param dict location: Location Dictionary that Contains All the Information Related to the Warehouse Location
        :param str buildingName: Warehouse Name to Insert
        :return: Warehouse Building ID
        :rtype: int
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Full Building Name
        buildingName = fullBuildingName(self._tableName, buildingName)

        # Insert Building to Building Table
        await asyncio.gather(BuildingsTable._add(self, location, buildingName))

        # Get Building Object of the Recently Inserted Warehouse Building
        findTask = asyncio.create_task(
            BuildingsTable._findMult(self, aconn, location[DICT_CITY_ID], buildingName)
        )
        await asyncio.gather(findTask)
        b = findTask.result()

        # Ask for the Warehouse Fields
        console.print("Adding New Warehouse...", style="caption")

        # Get Warehouse Insert Query
        warehouseQuery = self.__insertQuery()

        # Execute the Query to Insert the Warehouse
        await asyncio.gather(
            aconn.cursor().execute(
                warehouseQuery,
                [b.buildingId],
            )
        )
        insertedRow(b.buildingName, self._tableName)

        return b.buildingId

    async def get(
        self, aconn, field: str, value, printItems: bool = True
    ) -> list[Warehouse] | None:
        """
        Asynchronous Method to Filter Warehouses from its Remote Table based on a Given Field-Value Pair

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str field: Warehouse Field that will be Used to Compare in the Warehouse Table
        :param value: Value to Compare
        :param bool printItems: Specifies whether to Print or not the Fetched Items. Default is ``True``
        :return: List of Fetched Warehouses Objects if the Table isn't Empty. Otherwise, ``None``
        :rtype: list if the Table isn't Empty. Otherwise, NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Fetch Filtered Warehouses
        queryTask = asyncio.gather(
            SpecializationTable._getTable(
                self, aconn.cursor(), field, value, BUILDINGS_NAME
            )
        )

        # Clear Terminal
        if printItems:
            clear()

        await queryTask

        # Get the Warehouses Objects from the Fetched Warehouses
        warehousesList = self.__getFetchedObjects()

        # Print Filtered Warehouses
        if printItems:
            self.__print(warehousesList)

        return None if len(warehousesList) == 0 else warehousesList

    async def find(self, aconn, warehouseId: int) -> Warehouse | None:
        """
        Asynchronous Method to Find a Warehouse at its Remote Table based on its ID

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str warehouseId: Warehouse ID to Search for
        :return: Warehouse Object if Found. Otherwise, ``None``
        :rtype: Warehouse if Found. Otherwise, NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Warehouses from its Remote Table
        getTask = asyncio.create_task(
            self.get(aconn, WAREHOUSES_ID, warehouseId, False)
        )
        await asyncio.gather(getTask)
        warehouse = getTask.result()

        # Get Warehouses Object from the Fetched Item
        if warehouse == None:
            return None

        return warehouse[0]

    async def all(self, aconn, orderBy: str, desc: bool) -> None:
        """
        Asynchronous Method that Prints the All the Warehouses Stored at its Remote Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str orderBy: Warehouse Field that will be Used to Sort the Warehouse Table
        :param bool desc: Specificies whether to Sort in Ascending Order (``False``) or in Descending Order (``True``)
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Fetch All Warehouses
        queryTask = asyncio.gather(
            SpecializationTable._all(self, aconn.cursor(), orderBy, desc)
        )

        # Clear Terminal
        clear()

        await queryTask

        # Get the Warehouses Objects from the Fetched Warehouses
        warehousesList = self.__getFetchedObjects()

        # Print All Warehouses
        self.__print(warehousesList)

    async def modify(self, aconn, warehouseId: int, field: str, value) -> None:
        """
        Asynchronous Method to Modify a Warehouse Field to its Remote Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int warehouseId: Warehouse ID from its Remote Table
        :param str field: Warehouse Field to Modify
        :param value: Warehouse Field Value to be Assigned
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching

        NOTE: There's No Own Warehouse Field that can be Modified, Only the Ones Inherited from its Parent Table
        """

        # Modify Building Table Row Column
        await asyncio.gather(
            SpecializationTable._modifyParentTable(
                self, aconn.cursor(), warehouseId, field, value
            )
        )

    async def remove(self, aconn, warehouseId: int) -> None:
        """
        Asynchronous Method to Remove a Warehouse Row from its Remote Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int warehouseId: Warehouse ID from its Remote Table
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        await asyncio.gather(
            SpecializationTable._remove(self, aconn.cursor(), warehouseId)
        )


class BranchesTable(BuildingsTable):
    """
    Class that Handles the SQL Operations related to the Remote SQL Branches Table
    """

    def __init__(self):
        """
        Branches Remote Table Class Constructor
        """

        # Initialize Building Table Class
        super().__init__(BRANCHES_TABLE_NAME, BRANCHES_ID, LOCATIONS_SCHEME_NAME)

    def __getFetchedObjects(self) -> list[Branch]:
        """
        Method to Get a List of Fetched Branches Objects from ``self_items``

        :return: List of Fetched Branches Objects
        :rtype: list
        """

        branchesList = []

        for item in self._items:
            # Intialize Branch from the SQL Fetched Row
            b = Branch.fromFetchedItem(item)
            branchesList.append(b)

        return branchesList

    def __print(self, branchesList: list[Branch]) -> None:
        """
        Method that Prints the Branches Fetched from its Remote Table

        :param list branchesList: Fetched Branches Objects to Print
        :return: Nothing
        :rtype: NoneType

        """
        # Number of Branches to Print
        nRows = len(branchesList)

        # Initialize Rich Table
        table = getTable("Branches", nRows)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Coords", justify="left", max_width=COORDINATE_NCHAR)
        table.add_column("Phone", justify="left", max_width=CONTACT_NCHAR)
        table.add_column("Email", justify="left", max_width=CONTACT_NCHAR)
        table.add_column("Warehouse ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Distance", justify="left", max_width=DISTANCE_NCHAR)
        table.add_column("City ID", justify="left", max_width=ID_NCHAR)

        for b in branchesList:
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

        return sql.SQL(
            "INSERT INTO {schemeName}.{tableName} ({fields}) VALUES (%s, %s, %s)"
        ).format(
            schemeName=sql.Identifier(self._schemeName),
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [
                    sql.Identifier(self._tablePKFKName),
                    sql.Identifier(BRANCHES_FK_WAREHOUSE_CONNECTION),
                    sql.Identifier(BRANCHES_ROUTE_DISTANCE),
                ]
            ),
        )

    async def add(
        self,
        aconn,
        location: dict,
        buildingName: str,
        warehouseConnId: int,
        routeDistance: int,
    ) -> None:
        """
        Asynchronous Method to Insert a New Branch to the Branch Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param dict location: Location Dictionary that Contains All the Information Related to the Branch Location
        :param str buildingName: Branch Name to Insert
        :param int warehouseConnId: Warehouse ID that will be Connected with the New Branch Inserted
        :param int routeDistance: Route Distance between the Branch and the Warehouse which is Connected with
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Full Building Name
        buildingName = fullBuildingName(self._tableName, buildingName)

        # Insert Building to its Remote Table
        await asyncio.gather(BuildingsTable._add(self, aconn, location, buildingName))

        # Get Building Object of the Recently Inserted Branch Building
        findTask = asyncio.create_task(
            BuildingsTable._findMult(self, aconn, location[DICT_CITY_ID], buildingName)
        )
        await asyncio.gather(findTask)
        b = findTask.result()

        # Ask for the Branch Fields
        console.print("Adding New Branch...", style="caption")

        # Get Query to Insert Branch to its Remote Table
        branchQuery = self.__insertQuery()

        # Execute the Query to Insert the Branch
        await asyncio.gather(
            aconn[0].execute(
                branchQuery,
                [b.buildingId, warehouseConnId, routeDistance],
            )
        )
        insertedRow(b.buildingName, self._tableName)

    async def get(
        self, aconn, field: str, value, printItems: bool = True
    ) -> list[Branch] | None:
        """
        Asynchronous Method to Filter Branches from its Remote Table based on a Given Field-Value Pair

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str field: Branch Field that will be Used to Compare in the Branch Table
        :param value: Value to Compare
        :param bool printItems: Specifies whether to Print or not the Fetched Items. Default is ``True``
        :return: List of Fetched Branches Objects if the Table isn't Empty. Otherwise, ``None``
        :rtype: list if the Table isn't Empty. Otherwise, NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Fetch Filtered Branches
        queryTask = asyncio.gather(
            SpecializationTable._getTable(
                self, aconn.cursor(), field, value, BUILDINGS_NAME
            )
        )

        # Clear Terminal
        if printItems:
            clear()

        await queryTask

        # Get the Branches Objects from the Fetched Branches
        branchesList = self.__getFetchedObjects()

        # Print Filtered Branches
        if printItems:
            self.__print(branchesList)

        return None if len(branchesList) == 0 else branchesList

    async def find(self, aconn, branchId: int) -> Branch | None:
        """
        Asynchronous Method to Find a Branch at its Remote Table based on its ID

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str provinceId: Branch ID to Search for
        :return: Branch Object if Found. Otherwise, ``None``
        :rtype: Branch if Found. Otherwise, NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Branch from its Remote Table
        getTask = asyncio.create_task(self.get(aconn, BRANCHES_ID, branchId, False))
        await asyncio.gather(getTask)
        branch = getTask.result()

        # Get Branch Object from the Fetched Item
        if branch == None:
            return None

        return branch[0]

    async def all(self, aconn, orderBy: str, desc: bool) -> None:
        """
        Asynchronous Method that Prints the All the Branches Stored at its Remote Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str orderBy: Branches Field that will be Used to Sort the Branches Table
        :param bool desc: Specificies whether to Sort in Ascending Order (``False``) or in Descending Order (``True``)
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Fetch All Branches
        queryTask = asyncio.gather(
            SpecializationTable._all(self, aconn.cursor(), orderBy, desc)
        )

        # Clear Terminal
        clear()

        await queryTask

        # Get the Branches Objects from the Fetched Branches
        branchesList = self.__getFetchedObjects()

        # Print All Branches
        self.__print(branchesList)

    async def modify(self, aconn, branchId: int, field: str, value) -> None:
        """
        Asynchronous Method to Modify a Branch Field to its Remote Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int branchId: Branch ID from its Remote Table
        :param str field: Branch Field to Modify
        :param value: Branch Field Value to be Assigned
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Modify Branch Table Row Columns
        if (
            field == BRANCHES_FK_WAREHOUSE_CONNECTION
            or field == BRANCHES_ROUTE_DISTANCE
        ):
            await asyncio.gather(
                SpecializationTable._modifyTable(
                    self, aconn.cursor(), branchId, field, value
                )
            )

        # Modify Building Table Row Column
        else:
            await asyncio.gather(
                SpecializationTable._modifyParentTable(
                    self, aconn.cursor(), branchId, field, value
                )
            )

    async def remove(self, aconn, branchId: int) -> None:
        """
        Asynchronous Method to Remove a Branch Row from its Remote Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int branchId: Branch ID from its Remote Table
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        await asyncio.gather(
            SpecializationTable._remove(self, aconn.cursor(), branchId)
        )
