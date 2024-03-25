from psycopg import sql

from .constants import *

from .database import Database, console


# Functions that Returns Some Generic Table-related Strings
def getLocationName(locationTableName: str) -> tuple[str, str] | None:
    if locationTableName == COUNTRY_TABLENAME:
        return "Country", COUNTRY_ID

    elif locationTableName == PROVINCE_TABLENAME:
        return "Province", PROVINCE_ID

    elif locationTableName == REGION_TABLENAME:
        return "Region", REGION_ID

    elif locationTableName == CITY_TABLENAME:
        return "City", CITY_ID

    elif locationTableName == CITY_AREA_TABLENAME:
        return "City Area", CITY_AREA_ID

    return None


# Warehouse Connection Table Class
class WarehouseConnectionTable:
    # Table Name and ID Column Name
    _tableName = WAREHOUSE_CONN_TABLENAME
    _tablePKName = WAREHOUSE_CONN_ID

    _items = None
    _c = None

    # Constructor
    def __init__(self, database: Database):
        # Get Cursor
        self._c = database.getCursor()

    # Returns Query to Remove a Main Warehouse of a Given Location as a Sender from All its Connections
    def __removeSenderMainWarehouse(self, locationIdField: str):
        return sql.SQL(
            "DELETE FROM {tableName} WHERE {idField} EXISTS IN (SELECT {sendersConnIdField} FROM {sendersViewName} {senders} WHERE {senders}.{locationIdField} = %s AND {receivers}.{warehouseIdField} = %s)"
        ).format(
            tableName=sql.Identifier(self._tableName),
            idField=sql.Identifier(self._tablePKName),
            sendersConnIdField=sql.Identifier(SENDERS_WAREHOUSE_CONN_ID),
            sendersViewName=sql.Identifier(COUNTRY_WAREHOUSES_SENDERS_VIEWNAME),
            senders=sql.Identifier(SENDERS),
            locationIdField=sql.Identifier(locationIdField),
            warehouseIdField=sql.Identifier(SENDERS_WAREHOUSE_ID),
        )

    # Returns Query to Remove a Main Warehouse of a Given Location as a Receiver from All its Connections
    def __removeReceiverMainWarehouse(self, locationIdField: str):
        return sql.SQL(
            "DELETE FROM {tableName} WHERE {idField} EXISTS IN (SELECT {receiversConnIdField} FROM {receiversViewName} {receivers} WHERE {receivers}.{locationIdField} = %s AND {receivers}.{warehouseIdField} = %s)"
        ).format(
            tableName=sql.Identifier(self._tableName),
            idField=sql.Identifier(self._tablePKName),
            sendersConnIdField=sql.Identifier(SENDERS_WAREHOUSE_CONN_ID),
            sendersViewName=sql.Identifier(COUNTRY_WAREHOUSES_SENDERS_VIEWNAME),
            senders=sql.Identifier(SENDERS),
            locationIdField=sql.Identifier(locationIdField),
            warehouseIdField=sql.Identifier(SENDERS_WAREHOUSE_ID),
        )

    # Returns Query to Remove a Given Location Main Warehouse with All its Counterparts Connections
    def __removeMainWarehouse(
        self,
        locationTableName: str,
        locationId: int,
        warehouseId: int,
    ):
        # Get Location Name and ID Field
        locationName, locationIdField = getLocationName(locationTableName)

        # Get Query to Remove the Given Warehouse as a Sender
        senderQuery = self.__removeSenderMainWarehouse(locationIdField)

        # Get Query to Remove the Given Warehouse as a Receiver
        receiverQuery = self.__removeReceiverMainWarehouse(locationIdField)

        # Execute Query
        try:
            # Remove Given Warehouse as a Sender
            self._c.execute(senderQuery, [locationId, warehouseId])

            console.print(
                f"Removed Warehouse ID {warehouseId} as a Sender at {locationName}-Level",
                style="success",
            )

            # Remove Given Warehouse as a Receiver
            self._c.execute(receiverQuery, [locationId, warehouseId])

            console.print(
                f"Removed Warehouse ID {warehouseId} as a Receiver at {locationName}-Level",
                style="success",
            )

        except Exception as err:
            raise err

    # Returns Query to Remove a Given Province Main Warehouse with All its Counterparts Connections
    def removeProvinceMainWarehouse(self, provinceId: int, warehouseId: int) -> None:
        return self.__removeMainWarehouse(PROVINCE_TABLENAME, provinceId, warehouseId)

    # Returns Query to Remove a Given Region Main Warehouse with All its Counterparts Connections
    def removeRegionMainWarehouse(self, regionId: int, warehouseId: int) -> None:
        return self.__removeMainWarehouse(REGION_TABLENAME, regionId, warehouseId)

    # Returns Query to Remove a Given City Main Warehouse with All its Counterparts Connections
    def removeCityMainWarehouse(self, cityId: int, warehouseId: int) -> None:
        return self.__removeMainWarehouse(CITY_TABLENAME, cityId, warehouseId)

    # Returns Query to Remove a Given City Area Main Warehouse with All its Counterparts Connections
    def removeCityAreaMainWarehouse(self, areaId: int, warehouseId: int) -> None:
        return self.__removeMainWarehouse(CITY_AREA_TABLENAME, areaId, warehouseId)
