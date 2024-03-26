import asyncio
from psycopg import sql

from .constants import *

from .database import Database, console

from ..geocoding.constants import NOMINATIM_LONGITUDE, NOMINATIM_LATITUDE
from ..geocoding.routingpy import RoutingPyGeocoder


# Functions that Returns Some Generic Table-related Strings
def getLocationInfo(locationTableName: str) -> tuple[str, str] | None:
    if locationTableName == PROVINCE_TABLENAME:
        return CONN_TYPE_PROVINCE, PROVINCE_ID

    elif locationTableName == REGION_TABLENAME:
        return CONN_TYPE_REGION, REGION_ID

    elif locationTableName == CITY_TABLENAME:
        return CONN_TYPE_CITY, CITY_ID

    elif locationTableName == CITY_AREA_TABLENAME:
        return CONN_TYPE_AREA, CITY_AREA_ID

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

    # Fetch All Items and return them
    def __fetchall(self):
        # Fetch Items
        self._items = self._items.fetchall()

    # Get Valid List of Warehouse Dictionaries to be Used by a Warehouse Table Class
    def __getWarehouseDicts(
        self, warehouseConnsList: list[tuple[int, float, float]]
    ) -> list[dict]:
        # Initialize List
        warehouseList = []

        # Loop Over Fetched Items
        for w in warehouseConnsList:
            # Initialize Warehouse Dictionary
            warehouseDict = {}

            # Assign Dictionary Fields
            warehouseDict[DICT_WAREHOUSES_ID] = w[0]
            warehouseDict[DICT_WAREHOUSES_COORDS] = {
                NOMINATIM_LONGITUDE: w[1],
                NOMINATIM_LATITUDE: w[2],
            }

            # Append to Warehouse List
            warehouseList.append(warehouseDict)

        return warehouseList

    # Returns Query to Remove a Main Warehouse of a Given Location as a Sender from All its Connections
    def __removeSenderMainWarehouseQuery(self, locationIdField: str, connType: str):
        return sql.SQL(
            "DELETE FROM {tableName} WHERE {idField} EXISTS IN (SELECT {sendersConnIdField} FROM {sendersViewName} {senders} WHERE {senders}.{locationIdField} = %s AND {senders}.{warehouseIdField} = %s AND {senders}.{warehouseConnType} = {connType})"
        ).format(
            tableName=sql.Identifier(self._tableName),
            idField=sql.Identifier(self._tablePKName),
            sendersConnIdField=sql.Identifier(SENDERS_WAREHOUSE_CONN_ID),
            sendersViewName=sql.Identifier(WAREHOUSES_SENDERS_VIEWNAME),
            senders=sql.Identifier(SENDERS),
            locationIdField=sql.Identifier(locationIdField),
            warehouseIdField=sql.Identifier(SENDERS_WAREHOUSE_ID),
            warehouseConnType=sql.Identifier(WAREHOUSE_CONN_CONN_TYPE),
            connType=sql.Identifier(connType),
        )

    # Returns Query to Remove a Main Warehouse of a Given Location as a Receiver from All its Connections
    def __removeReceiverMainWarehouseQuery(self, locationIdField: str, connType: str):
        return sql.SQL(
            "DELETE FROM {tableName} WHERE {idField} EXISTS IN (SELECT {receiversConnIdField} FROM {receiversViewName} {receivers} WHERE {receivers}.{locationIdField} = %s AND {receivers}.{warehouseIdField} = %s AND {receivers}.{warehouseConnType} = {connType})"
        ).format(
            tableName=sql.Identifier(self._tableName),
            idField=sql.Identifier(self._tablePKName),
            sendersConnIdField=sql.Identifier(SENDERS_WAREHOUSE_CONN_ID),
            sendersViewName=sql.Identifier(WAREHOUSES_SENDERS_VIEWNAME),
            senders=sql.Identifier(SENDERS),
            locationIdField=sql.Identifier(locationIdField),
            warehouseIdField=sql.Identifier(SENDERS_WAREHOUSE_ID),
            warehouseConnType=sql.Identifier(WAREHOUSE_CONN_CONN_TYPE),
            connType=sql.Identifier(connType),
        )

    # Returns Query to Remove a Given Location Main Warehouse with All its Counterparts Connections
    def __removeMainWarehouse(
        self,
        locationTableName: str,
        locationId: int,
        warehouseId: int,
    ):
        # Get Location Type and ID Field
        locationType, locationIdField = getLocationInfo(locationTableName)

        # Get Query to Remove the Given Warehouse as a Sender
        senderQuery = self.__removeSenderMainWarehouseQuery(
            locationIdField, locationType
        )

        # Get Query to Remove the Given Warehouse as a Receiver
        receiverQuery = self.__removeReceiverMainWarehouseQuery(
            locationIdField, locationType
        )

        # Execute Query
        try:
            # Remove Given Warehouse as a Sender
            self._c.execute(senderQuery, [locationId, warehouseId])

            console.print(
                f"Removed Warehouse ID {warehouseId} as a Sender at {locationType}-Level",
                style="success",
            )

            # Remove Given Warehouse as a Receiver
            self._c.execute(receiverQuery, [locationId, warehouseId])

            console.print(
                f"Removed Warehouse ID {warehouseId} as a Receiver at {locationType}-Level",
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

    # Returns Query to Get All Main Warehouses of a Given Location Type from a Given Parent Location ID
    def __getMainWarehousesQuery(
        self, locationMainWarehousesTableName: str, parentLocationIdField: str
    ):
        return sql.SQL(
            "SELECT {warehouseIdField}, {warehouseLatCoord}, {warehouseLonCoord} FROM {locationMainWarehousesTableName} WHERE {parentLocationIdField} = %s"
        ).format(
            warehouseIdField=sql.Identifier(WAREHOUSE_ID),
            warehouseLatCoord=sql.Identifier(BUILDING_GPS_LATITUDE),
            warehouseLonCoord=sql.Identifier(BUILDING_GPS_LONGITUDE),
            locationMainWarehousesTableName=sql.Identifier(
                locationMainWarehousesTableName
            ),
            parentLocationIdField=sql.Identifier(parentLocationIdField),
        )

    # Returns Query to Get All Province Main Warehouses from a Given Country ID
    def __getProvinceMainWarehousesQuery(self):
        return self.__getMainWarehousesQuery(PROVINCE_MAIN_WAREHOUSES, COUNTRY_ID)

    # Get All Province Main Warehouses from a Given Country ID
    def getProvinceMainWarehouses(self, countryId: int) -> list[dict]:
        # Get Query to Get All Province Main Warehouses
        provinceMainQuery = self.__getProvinceMainWarehousesQuery()

        # Execute Query and Fetch Items
        try:
            # Get All Province Main Warehouses
            self._items = self._c.execute(
                provinceMainQuery,
                [countryId],
            )

            # Fetch Items
            self.__fetchall()

            console.print(
                f"Get All Province Main Warehouses from Country ID {countryId}",
                style="success",
            )

        except Exception as err:
            raise err

        # Get List of Warehouse Dictionaries
        warehouseConns = self.__getWarehouseDicts(self._items)

        return warehouseConns

    # Returns Query to Get All Region Main Warehouses from a Given Province ID
    def __getRegionMainWarehousesQuery(self):
        return self.__getMainWarehousesQuery(REGION_MAIN_WAREHOUSES, PROVINCE_ID)

    # Get All Region Main Warehouses from a Given Province ID
    def getRegionMainWarehouses(self, provinceId: int) -> list[dict]:
        # Get Query to Get All Region Main Warehouses
        regionMainQuery = self.__getRegionMainWarehousesQuery()

        # Execute Query and Fetch Items
        try:
            # Get All Region Main Warehouses
            self._items = self._c.execute(
                regionMainQuery,
                [provinceId],
            )

            # Fetch Items
            self.__fetchall()

            console.print(
                f"Get All Region Main Warehouses from Province ID {provinceId}",
                style="success",
            )

        except Exception as err:
            raise err

        # Get List of Warehouse Dictionaries
        warehouseConns = self.__getWarehouseDicts(self._items)

        return warehouseConns

    # Returns Query to Get All City Main Warehouses from a Given Region ID
    def __getCityMainWarehousesQuery(self):
        return self.__getMainWarehousesQuery(CITY_MAIN_WAREHOUSES, REGION_ID)

    # Returns Query to Get All City Area Main Warehouses from a Given City ID
    def __getCityAreaMainWarehousesQuery(self):
        return self.__getMainWarehousesQuery(CITY_AREA_MAIN_WAREHOUSES, CITY_ID)

    # Returns Query to Insert a Main Warehouse Connection of a Given Location
    def __insertMainWarehouseQuery(self):
        return sql.SQL(
            "INSERT INTO {tableName} ({fields}) VALUES (%s, %s, %s, %s)"
        ).format(
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [
                    sql.Identifier(WAREHOUSE_CONN_WAREHOUSE_FROM_ID),
                    sql.Identifier(WAREHOUSE_CONN_WAREHOUSE_TO_ID),
                    sql.Identifier(WAREHOUSE_CONN_ROUTE_DISTANCE),
                    sql.Identifier(WAREHOUSE_CONN_CONN_TYPE),
                ]
            ),
        )

    # Insert a Warehouse Connection of the New Main Warehouse as a Sender Asynchronously
    async def __insertMainWarehouseSenderConn(
        self,
        routingPyGeocoder: RoutingPyGeocoder,
        query,
        connType: str,
        warehouse: dict,
        warehouseConn: dict,
    ):
        # Get Route Distance from the Main Warehouse to Insert and the Inserted Warehouse
        routeDistanceSender = routingPyGeocoder.getRouteDistance(
            warehouse[DICT_WAREHOUSES_COORDS], warehouseConn[DICT_WAREHOUSES_COORDS]
        )

        # Get Warehouse and Warehouse Connection ID
        warehouseId = warehouse[DICT_WAREHOUSES_ID]
        warehouseConnId = warehouseConn[DICT_WAREHOUSES_ID]

        # Execute Query
        try:
            # Insert the Given Warehouse as a Sender
            await self._c.execute(
                query,
                [warehouseId, warehouseConnId, routeDistanceSender, connType],
            )

            console.print(
                f"Inserted Warehouse Connection from ID {warehouseId} to ID {warehouseConnId} at {connType}-Level",
                style="success",
            )

        except Exception as err:
            raise err

    # Insert a Warehouse Connection of the New Main Warehouse as a Receiver Asynchronously
    async def __insertMainWarehouseReceiverConn(
        self,
        routingPyGeocoder: RoutingPyGeocoder,
        query,
        connType: str,
        warehouse: dict,
        warehouseConn: dict,
    ):
        # Get Route Distance from the Inserted Warehouse to the Main Warehouse to Insert
        routeDistanceReceiver = routingPyGeocoder.getRouteDistance(
            warehouseConn[DICT_WAREHOUSES_COORDS], warehouse[DICT_WAREHOUSES_COORDS]
        )

        # Get Warehouse and Warehouse Connection ID
        warehouseId = warehouse[DICT_WAREHOUSES_ID]
        warehouseConnId = warehouseConn[DICT_WAREHOUSES_ID]

        # Execute Query
        try:
            # Insert the Given Warehouse as a Receiver
            await self._c.execute(
                query, [warehouseConnId, warehouseId, routeDistanceReceiver, connType]
            )

            console.print(
                f"Inserted Warehouse Connection from ID {warehouseConnId} to ID {warehouseId} at {connType}-Level",
                style="success",
            )

        except Exception as err:
            raise err

    # Insert All its Warehouse Connections of the New Main Warehouse Asynchronously
    async def __insertMainWarehouseConns(
        self,
        routingPyGeocoder: RoutingPyGeocoder,
        connType: str,
        warehouse: dict,
        warehouseConns: list[dict],
    ):
        # Get Query to Insert Warehouse Connections
        query = self.__insertMainWarehouseQuery()

        # Insert Each Warehouse Connection to Warehouse Connection Table Asynchronously
        async with asyncio.TaskGroup() as tg:
            for warehouseConn in warehouseConns:
                # Check Warehouse Connection ID. Ignore if it's the Same from the Parent
                if warehouseConn[DICT_WAREHOUSES_ID] == warehouse[DICT_WAREHOUSES_ID]:
                    continue

                # Insert Main Warehouse Sender Connection
                tg.create_task(
                    self.__insertMainWarehouseSenderConn(
                        routingPyGeocoder, query, connType, warehouse, warehouseConn
                    )
                )

                # Insert Main Warehouse Receiver Connection
                tg.create_task(
                    self.__insertMainWarehouseReceiverConn(
                        routingPyGeocoder, query, connType, warehouse, warehouseConn
                    )
                )

                # Sleep for N Seconds
                await asyncio.sleep(ASYNC_SLEEP)

    # Insert Province Main Warehouse and Set All of its Connections
    def insertProvinceMainWarehouse(
        self, countryId: int, provinceId: int, warehouseDict: dict
    ):
        # Get All Province Main Warehouses at the Given Country ID
        provinceMainWarehouses = self.getProvinceMainWarehouses(countryId)

        # Get All Region Main Warehouses at the Given Province ID
        regionMainWarehouses = self.getRegionMainWarehouses(provinceId)

        # Set Province Main Warehouse Connections
        asyncio.run(
            self.__insertMainWarehouseConns(
                provinceMainWarehouses,
                CONN_TYPE_PROVINCE,
                warehouseDict,
                provinceMainWarehouses,
            )
        )

        # Set Region Main Warehouse Connections
        asyncio.run(
            self.__insertMainWarehouseConns(
                regionMainWarehouses,
                CONN_TYPE_PROVINCE,
                warehouseDict,
                regionMainWarehouses,
            )
        )
