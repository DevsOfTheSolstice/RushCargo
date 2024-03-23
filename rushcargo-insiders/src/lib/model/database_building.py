from .database import *


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

    # Get Insert Query
    def __getInsertQuery(self):
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

    # Filter Items with Multiple Conditions from Building Table
    def _getMult(self, fields: list[str], values: list) -> bool:
        if not SpecializationTable._getMultParentTable(self, fields, values):
            return False

        return True

    # Find Building from Building Table
    def _find(self, areaId: int, buildingName: str) -> Building | None:
        """
        Returns Building Object if it was Found. Otherwise, False
        """

        # Get Building
        if not self._getMult(
            [BUILDING_FK_CITY_AREA, BUILDING_NAME], [areaId, buildingName]
        ):
            return None

        # Get Building Object from Item Fetched
        return Building.fromItemFetched(self._items[0])

    # Insert Building to Table
    def _add(self, b: Building) -> None:
        # Get Query
        query = self.__getInsertQuery()

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
        # Initialize Basic Table Class
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

        # No Results
        if nItems == 0:
            noCoincidenceFetched()
            return

        # Initialize Rich Table
        table = getTable("Warehouse", nItems)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Coords", justify="left", max_width=COORDINATE_NCHAR)
        table.add_column("Description", justify="left", max_width=DESCRIPTION_NCHAR)
        table.add_column("Phone", justify="left", max_width=CONTACT_NCHAR)
        table.add_column("Email", justify="left", max_width=CONTACT_NCHAR)
        table.add_column("City Area ID", justify="left", max_width=ID_NCHAR)

        # Loop Over Items
        for item in self._items:
            # Intialize Warehouse from Item Fetched
            w = Warehouse.fromItemFetched(item)

            # Add Row to Rich Table
            table.add_row(
                str(w.buildingId),
                w.buildingName,
                getCoords(w.gpsLatitude, w.gpsLongitude),
                w.addressDescription,
                str(w.phone),
                w.email,
                str(w.areaId),
            )

        # Print Table
        console.print(table)

    # Get Insert Query
    def __getInsertQuery(self):
        return sql.SQL("INSERT INTO {tableName} ({field}) VALUES (%s)").format(
            tableName=sql.Identifier(self._tableName),
            field=sql.Identifier(WAREHOUSE_ID),
        )

    # Insert Warehouse to Table
    def add(self, w: Warehouse) -> None:
        # Get Warehouse Insert Query
        warehouseQuery = self.__getInsertQuery()

        # Get Building object from Warehouse
        b = Building.fromWarehouse(w)

        # Insert Building to Building Table
        BuildingTable._add(self, b)

        # Get Building ID
        b = BuildingTable._find(self, b.areaId, b.buildingName)

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
            return False

        # Print Items
        if printItems:
            self.__print()
        return True

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

        SpecializationTable._modifyParentTable(
            self, BUILDING_ID, warehouseId, field, value
        )

    # Remove Row from Warehouse Table
    def remove(self, warehouseId: int) -> None:
        SpecializationTable._remove(self, WAREHOUSE_ID, BUILDING_ID, warehouseId)
