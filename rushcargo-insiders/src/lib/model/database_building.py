from psycopg import sql

from .classes import Building, Warehouse, Branch
from .constants import *
from .database import Database, console
from .database_tables import (
    SpecializationTable,
    noCoincidenceFetched,
    insertedRow,
    getTable,
)


# Functions that Returns Some Generic Table-related Strings
def getCoords(lat: float, lon: float) -> str:
    return f"{lat}\n{lon}"


# Building Table Class
class BuildingTable(SpecializationTable):
    # Constructor
    def __init__(self, tableName: str, tablePKFKName: str, database: Database):
        # Initialize Specialization Table Class
        super().__init__(
            tableName,
            BUILDING_TABLENAME,
            tablePKFKName,
            BUILDING_ID,
            database,
        )

    # Returns Building Insert Query
    def __insertParentQuery(self):
        return sql.SQL(
            "INSERT INTO {parentTableName} ({fields}) VALUES (%s,%s, %s, %s, %s, %s, %s)"
        ).format(
            parentTableName=sql.Identifier(self._parentTableName),
            fields=sql.SQL(",").join(
                [
                    sql.Identifier(BUILDING_ADDRESS_DESCRIPTION),
                    sql.Identifier(BUILDING_FK_CITY_AREA),
                    sql.Identifier(BUILDING_NAME),
                    sql.Identifier(BUILDING_EMAIL),
                    sql.Identifier(BUILDING_PHONE),
                    sql.Identifier(BUILDING_GPS_LATITUDE),
                    sql.Identifier(BUILDING_GPS_LONGITUDE),
                ]
            ),
        )

    # Find Building from Building Table
    def _find(self, areaId: int, buildingName: str) -> Building | None:
        """
        Returns Building Object if it was Found. Otherwise, False
        """

        # Get Building
        if not SpecializationTable._getMultParentTable(
            self, [BUILDING_FK_CITY_AREA, BUILDING_NAME], [areaId, buildingName]
        ):
            return None

        # Get Building Object from Item Fetched
        return Building.fromItemFetched(self._items[0])

    # Insert Building to Building Table
    def _add(self, b: Building | Warehouse | Branch) -> None:
        # Get Query to Insert Building to Building Table
        query = self.__insertParentQuery()

        # Execute Query
        try:
            self._c.execute(
                query,
                [
                    b.addressDescription,
                    b.areaId,
                    b.buildingName,
                    b.email,
                    b.phone,
                    b.gpsLatitude,
                    b.gpsLongitude,
                ],
            )

            console.print(
                insertedRow(b.buildingName, self._parentTableName),
                style="success",
            )

        except Exception as err:
            raise err


# Warehouse Table Class
class WarehouseTable(BuildingTable):
    # Constructor
    def __init__(self, database: Database):
        # Initialize Building Table Class
        super().__init__(
            WAREHOUSE_TABLENAME,
            WAREHOUSE_ID,
            database,
        )

    # Print Items
    def __print(self) -> None:
        w = None

        # Number of Items
        nItems = len(self._items)

        # Initialize Rich Table
        table = getTable("Warehouse", nItems)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Coords", justify="left", max_width=COORDINATE_NCHAR)
        table.add_column("Phone", justify="left", max_width=CONTACT_NCHAR)
        table.add_column("Email", justify="left", max_width=CONTACT_NCHAR)
        table.add_column("City Area", justify="left", max_width=ID_NCHAR)

        # Loop Over Items
        for item in self._items:
            # Intialize Warehouse from Item Fetched
            w = Warehouse.fromItemFetched(item)

            # Add Row to Rich Table
            table.add_row(
                str(w.buildingId),
                w.buildingName,
                getCoords(w.gpsLatitude, w.gpsLongitude),
                str(w.phone),
                w.email,
                str(w.areaId),
            )

        # Print Table
        console.print(table)

    # Returns Warehouse Insert Query
    def __insertQuery(self):
        return sql.SQL("INSERT INTO {tableName} ({field}) VALUES (%s)").format(
            tableName=sql.Identifier(self._tableName),
            field=sql.Identifier(self._tablePKFKName),
        )

    # Insert Warehouse to Warehouse Table
    def add(self, w: Warehouse) -> None:
        # Get Warehouse Insert Query
        warehouseQuery = self.__insertQuery()

        # Insert Building to Building Table
        BuildingTable._add(self, w)

        # Get Building ID
        b = BuildingTable._find(self, w.areaId, w.buildingName)

        # Execute Query to Insert Warehouse
        try:
            self._c.execute(
                warehouseQuery,
                [b.buildingId],
            )

            console.print(
                insertedRow(w.buildingName, self._tableName),
                style="success",
            )

        except Exception as err:
            raise err

    # Filter Items from Warehouse Table
    def get(self, field: str, value, printItems: bool = True) -> bool:
        if not SpecializationTable._getTable(self, field, value):
            if printItems:
                noCoincidenceFetched()
            return False

        # Print Items
        if printItems:
            self.__print()
        return True

    # Find Warehouse from Warehouse Table
    def find(self, warehouseId: int) -> Warehouse | None:
        """
        Returns Warehouse Object if it was Found. Otherwise, False
        """

        # Get Warehouse
        if not SpecializationTable._getTable(self, WAREHOUSE_ID, warehouseId):
            return None

        # Get Warehouse Object from Item Fetched
        return Warehouse.fromItemFetched(self._items[0])

    # Get All Items from Warehouse Table
    def all(self, orderBy: str, desc: bool) -> None:
        SpecializationTable._all(self, orderBy, desc)

        # Print Items
        self.__print()

    # Modify Row from Warehouse Table
    def modify(self, warehouseId: int, field: str, value) -> None:
        """
        NOTE: There's No Own Warehouse Field that can be Modified, Only the Ones Inherited from its Parent Table
        """

        # Modify Building Table Row Column
        SpecializationTable._modifyParentTable(self, warehouseId, field, value)

    # Remove Row from Warehouse Table
    def remove(self, warehouseId: int) -> None:
        SpecializationTable._remove(self, warehouseId)


# Branch Table Class
class BranchTable(BuildingTable):
    # Constructor
    def __init__(self, database: Database):
        # Initialize Building Table Class
        super().__init__(
            BRANCH_TABLENAME,
            BRANCH_ID,
            database,
        )

    # Print Items
    def __print(self) -> None:
        b = None

        # Number of Items
        nItems = len(self._items)

        # Initialize Rich Table
        table = getTable("Warehouse", nItems)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Coords", justify="left", max_width=COORDINATE_NCHAR)
        table.add_column("Phone", justify="left", max_width=CONTACT_NCHAR)
        table.add_column("Email", justify="left", max_width=CONTACT_NCHAR)
        table.add_column("Warehouse ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Distance", justify="left", max_width=DISTANCE_NCHAR)
        table.add_column("City Area ID", justify="left", max_width=ID_NCHAR)

        # Loop Over Items
        for item in self._items:
            # Intialize Branch from Item Fetched
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
                str(b.areaId),
            )

        # Print Table
        console.print(table)

    # Returns Branch Insert Query
    def __insertQuery(self):
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

    # Insert Branch to Branch Table
    def add(self, b: Branch) -> None:
        # Get Branch Insert Query
        branchQuery = self.__insertQuery()

        # Insert Building to Building Table
        BuildingTable._add(self, b)

        # Get Building ID
        B = BuildingTable._find(self, b.areaId, b.buildingName)

        # Execute Query to Insert Warehouse
        try:
            self._c.execute(
                branchQuery,
                [B.buildingId, b.warehouseConnection, b.routeDistance],
            )

            console.print(
                insertedRow(b.buildingName, self._tableName),
                style="success",
            )

        except Exception as err:
            raise err

    # Filter Items from Branch Table
    def get(self, field: str, value, printItems: bool = True) -> bool:
        if not SpecializationTable._getTable(self, field, value):
            if printItems:
                noCoincidenceFetched()
            return False

        # Print Items
        if printItems:
            self.__print()
        return True

    # Find Branch from Branch Table
    def find(self, branchId: int) -> Branch | None:
        """
        Returns Branch Object if it was Found. Otherwise, False
        """

        # Get Warehouse
        if not SpecializationTable._getTable(self, BRANCH_ID, branchId):
            return None

        # Get Branch Object from Item Fetched
        return Branch.fromItemFetched(self._items[0])

    # Get All Items from Branch Table
    def all(self, orderBy: str, desc: bool) -> None:
        SpecializationTable._all(self, orderBy, desc)

        # Print Items
        self.__print()

    # Modify Row from Branch Table
    def modify(self, branchId: int, field: str, value) -> None:
        # Modify Branch Table Row Columns
        if field == BRANCH_FK_WAREHOUSE_CONNECTION or field == BRANCH_ROUTE_DISTANCE:
            SpecializationTable._modifyTable(self, branchId, field, value)

        # Modify Building Table Row Column
        else:
            SpecializationTable._modifyParentTable(self, branchId, field, value)

    # Remove Row from Branch Table
    def remove(self, branchId: int) -> None:
        SpecializationTable._remove(self, branchId)
