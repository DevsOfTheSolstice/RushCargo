import asyncio
from psycopg import sql

from .constants import *

from .database import console
from .database_tables import cancelTasks

from ..controller.constants import RICH_LOGGER_DEBUG_MODE

from ..geocoding.constants import (
    NOMINATIM_LONGITUDE,
    NOMINATIM_LATITUDE,
    DICT_WAREHOUSE_COORDS,
    DICT_WAREHOUSE_ID,
)
from ..geocoding.exceptions import RouteNotFound, RouteLimitSurpassed
from ..geocoding.routingpy import ORSGeocoder


def getLocationInfo(locationTableName: str) -> tuple[str, str] | None:
    """
    Function to Get the Location Connection Type and Location ID Field for a Given Location Table Name

    :return: Location Connection Type and Location ID Field if Found. Otherwise, ``None``
    :rtype: Tuple if Found. Otherwise, NoneType
    """

    if locationTableName == REGIONS_TABLE_NAME:
        return CONN_TYPE_REGION, REGIONS_ID

    elif locationTableName == CITIES_TABLE_NAME:
        return CONN_TYPE_CITY, CITIES_ID

    return None


class WarehouseConnectionsTable:
    """
    Warehouse Connections Remote Table Class
    """

    # Database Connection
    _items = None

    # Scheme, Table, Table PK and Scheme + Table Name
    _schemeName = None
    _tableName = None
    _tablePKName = None
    _fullTableName = None

    # Constructor
    def __init__(self):
        """
        Warehouse Connections Remote Table Class Constructor
        """

        # Store Table-related Information
        self._schemeName = CONNECTIONS_SCHEME_NAME
        self._tableName = WAREHOUSES_CONN_TABLE_NAME
        self._tablePKName = WAREHOUSES_CONN_ID
        self._fullTableName = sql.SQL(".").join(
            [sql.Identifier(self._schemeName), sql.Identifier(self._tableName)]
        )

    def __getWarehouseDicts(
        self, warehousesList: list[tuple[int, float, float]]
    ) -> list[dict]:
        """
        Method to Get a List of Warehouse Dictionaries, that Contain its ID and Coordinates

        :param list warehousesList: List of Fetched Warehouses
        :return: List of Warehouse Dictionaries that Contain its ID and Coordinates
        :rtype: list
        """

        warehouseDictsList = []

        for w in warehousesList:
            warehouseDict = {}

            warehouseDict[DICT_WAREHOUSE_ID] = w[0]
            warehouseDict[DICT_WAREHOUSE_COORDS] = {
                NOMINATIM_LATITUDE: w[1],
                NOMINATIM_LONGITUDE: w[2],
            }

            warehouseDictsList.append(warehouseDict)

        return warehouseDictsList

    def __getWarehouseIds(self, warehousesList: list[tuple[int]]) -> list[int]:
        """
        Method to Get a List that Contains All the Warehouse IDs that have been Fetched from the Warehouses Remote View

        :param list warehouseList: List of Fetched Warehouse IDs from the Remote Table
        :return: List that Contains All the Warehouse IDs
        :rtype: list
        """

        warehouseIdsList = []

        for w in warehousesList:
            warehouseIdsList.append(w[0])

        return warehouseIdsList

    def __isMainWarehouseQuery(
        self, locationIdField: str, tableName: str, warehouseIdField: str
    ):
        """
        Method that Returns the Query to Check if a Given Warehouse is the Main One at a Given Location Table

        :param str locationIdField: Location ID Field
        :param str tableName: Location Table Name to Check
        :param str warehouseIdField: Warehouse ID Field to Compare at the Given Location Table
        :return: SQL Query
        :rtype: Composed
        """

        sql.SQL(
            "SELECT {locationIdField} FROM {locationsSchemeName}.{locationTableName} WHERE {warehouseIdField} = (%s)"
        ).format(
            locationIdField=sql.Identifier(locationIdField),
            locationsSchemeName=sql.Identifier(LOCATIONS_SCHEME_NAME),
            warehouseIdField=sql.Identifier(warehouseIdField),
            locationTableName=sql.Identifier(tableName),
        )

    async def isMainWarehouse(
        self, acursor, warehouseId: int
    ) -> tuple[str, int] | None:
        """
        Method that Returns the Query to Check if a Given Warehouse is Main at Any Location

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param str warehouseId: Warehouse ID to Compare
        :return: The Table Name where the Given Warehouse ID is the Main One if Found, and the Location ID where It's. Otherwise, ``None``
        :rtype: tuple if the Given Warehouse ID is the Main for Any Location. Otherwise, NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get the Query to Check if the Given Warehouse is the Main One to Any Region
        regionMainQuery = self.__isMainWarehouseQuery(
            REGIONS_ID, REGIONS_TABLE_NAME, REGIONS_FK_WAREHOUSE
        )

        # Get the Query to Check if the Given Warehouse is the Main One to Any City
        cityMainQuery = self.__isMainWarehouseQuery(
            CITIES_ID, CITIES_TABLE_NAME, CITIES_FK_WAREHOUSE
        )

        # Check if the Warehouse is the Main One to Any Region
        await asyncio.gather(acursor.execute(regionMainQuery, [warehouseId]))
        fetchTask = asyncio.create_task(acursor.fetchone())
        await asyncio.gather(fetchTask)
        regionId = fetchTask.result()

        if regionId != None:
            return REGIONS_TABLE_NAME, regionId

        # Check if the Warehouse is the Main One to Any City
        await asyncio.gather(acursor.execute(cityMainQuery, [warehouseId]))
        fetchTask = asyncio.create_task(acursor.fetchone())
        await asyncio.gather(fetchTask)
        cityId = fetchTask.result()

        if cityId != None:
            return CITIES_TABLE_NAME, cityId

        return None

    def __removeSenderMainWarehouseQuery(self, locationIdField: str):
        """
        Method that Returns the Query to Remove a Main Warehouse of a Given Location as a Sender from All its Connections

        :param str locationIdField: Location Type ID Field to Compare
        :return: SQL Query
        :rtype: Composed
        """

        return sql.SQL(
            "DELETE FROM {fullTableName} WHERE {warehouseConnIdField} IN (SELECT {sendersConnIdField} FROM {connectionsSchemeName}.{sendersViewName} {senders} WHERE {senders}.{locationIdField} = (%s) AND {senders}.{warehouseIdField} = (%s) AND {senders}.{warehouseConnType} = (%s))"
        ).format(
            fullTableName=self._fullTableName,
            warehouseConnIdField=sql.Identifier(WAREHOUSES_CONN_ID),
            idField=sql.Identifier(self._tablePKName),
            sendersConnIdField=sql.Identifier(SENDERS_WAREHOUSE_CONN_ID),
            connectionsSchemeName=sql.Identifier(CONNECTIONS_SCHEME_NAME),
            sendersViewName=sql.Identifier(WAREHOUSES_SENDERS_VIEW_NAME),
            senders=sql.Identifier(SENDERS),
            locationIdField=sql.Identifier(locationIdField),
            warehouseIdField=sql.Identifier(SENDERS_WAREHOUSE_ID),
            warehouseConnType=sql.Identifier(WAREHOUSES_CONN_CONN_TYPE),
        )

    def __removeReceiverMainWarehouseQuery(self, locationIdField: str):
        """
        Method that Returns the Query to Remove a Main Warehouse of a Given Location as a Receiver from All its Connections

        :param str locationIdField: Location Type ID Field to Compare
        :return: SQL Query
        :rtype: Composed
        """

        return sql.SQL(
            "DELETE FROM {fullTableName} WHERE {warehouseConnIdField} IN (SELECT {receiversConnIdField} FROM {connectionsSchemeName}.{receiversViewName} {receivers} WHERE {receivers}.{locationIdField} = %s AND {receivers}.{warehouseIdField} = %s AND {receivers}.{warehouseConnType} =%s)"
        ).format(
            fullTableName=self._fullTableName,
            warehouseConnIdField=sql.Identifier(WAREHOUSES_CONN_ID),
            idField=sql.Identifier(self._tablePKName),
            receiversConnIdField=sql.Identifier(RECEIVERS_WAREHOUSE_CONN_ID),
            connectionsSchemeName=sql.Identifier(CONNECTIONS_SCHEME_NAME),
            receiversViewName=sql.Identifier(WAREHOUSES_RECEIVERS_VIEW_NAME),
            receivers=sql.Identifier(RECEIVERS),
            locationIdField=sql.Identifier(locationIdField),
            warehouseIdField=sql.Identifier(RECEIVERS_WAREHOUSE_ID),
            warehouseConnType=sql.Identifier(WAREHOUSES_CONN_CONN_TYPE),
        )

    async def __removeMainWarehouse(
        self,
        acursor,
        locationTableName: str,
        locationId: int,
        warehouseId: int,
    ) -> None:
        """
        Method to Remove a Main Warehouse of a Given Location as a Sender and as a Receiver from All of its Warehouse Connections at a Given Location Level

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param str locationTableName: Location Table Name where the Warehouse is Located and Set as the Main One
        :param str locationId: Location ID at its Table where the Warehouse is Located
        :param int warehouseId: Main Warehouse ID that is going to be Removed from its Warehouse Connections at the Given Location Level
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        locationType, locationIdField = getLocationInfo(locationTableName)

        # Get Query to Remove the Given Warehouse as a Sender
        senderQuery = self.__removeSenderMainWarehouseQuery(locationIdField)

        # Get Query to Remove the Given Warehouse as a Receiver
        receiverQuery = self.__removeReceiverMainWarehouseQuery(locationIdField)

        # Remove Given Warehouse as a Sender and as a Receiver
        senderTask = asyncio.create_task(
            acursor.execute(senderQuery, [locationId, warehouseId, locationType])
        )
        removeTask = asyncio.create_task(
            acursor.execute(receiverQuery, [locationId, warehouseId, locationType])
        )

        tasks = [senderTask, removeTask]
        try:
            await asyncio.gather(*tasks)

        except Exception as err:
            cancelTasks(tasks)
            raise err

        if ROUTES_DEBUG_MODE:
            console.print(
                f"Removed Warehouse ID {warehouseId} as a Sender and as a Receiver at {locationType}-Level\n",
                style="success",
            )

    async def removeRegionMainWarehouse(
        self, acursor, regionId: int, warehouseId: int
    ) -> None:
        """
        Asynchronous  Method to Remove a Given Region Main Warehouse as a Sender and as a Receiver from All of its Warehouse Connections

         :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
         :param str regionId: Region ID where the Warehouse is Located and Set as the Main One
         :param int warehouseId: Main Warehouse ID that is going to be Removed from its Warehouse Connections at the Given Location Level (Region)
         :return: Nothing
         :rtype: NoneType
         :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Remove Region-Type Connections
        await asyncio.gather(
            self.__removeMainWarehouse(
                acursor, REGIONS_TABLE_NAME, regionId, warehouseId
            )
        )

    async def removeCityMainWarehouse(
        self, acursor, regionId: int, cityId: int, warehouseId: int
    ) -> None:
        """
        Asynchronous Method to Remove a Given City Main Warehouse as a Sender and as a Receiver from All of its Warehouse Connections

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param str regionId: Region ID where the Parent Main Warehouse is Located
        :param str cityId: City ID where the Warehouse is Located and Set as the Main One
        :param int warehouseId: Main Warehouse ID that is going to be Removed from its Warehouse Connections at the Given Location Level (City)
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Remove Region-Type Connection (with its Parent Main Warehouse)
        regionTask = asyncio.create_task(
            self.__removeMainWarehouse(
                acursor, REGIONS_TABLE_NAME, regionId, warehouseId
            )
        )

        # Remove City-Type Connections
        cityTask = asyncio.create_task(
            self.__removeMainWarehouse(acursor, CITIES_TABLE_NAME, cityId, warehouseId)
        )

        tasks = [regionTask, cityTask]
        try:
            await asyncio.gather(*tasks)

        except Exception as err:
            cancelTasks(tasks)
            raise err

    def __getMainWarehousesQuery(
        self, locationMainWarehousesViewName: str, parentLocationIdField: str
    ):
        """
        Method that Returns the Query to Get All the Main Warehouses of a Given Location Type from a Given Parent Location ID

        :param str locationMainWarehousesViewName: View Name that Contains Only the Main Warehouses for the Given Location
        :param str parentLocationIdField: Parent Location Type ID Field to Compare
        :return: SQL Query
        :rtype: Composed
        """

        return sql.SQL(
            "SELECT {warehouseIdField}, {warehouseLatCoord}, {warehouseLonCoord} FROM {connectionsSchemeName}.{locationMainWarehousesViewName} WHERE {parentLocationIdField} = (%s)"
        ).format(
            warehouseIdField=sql.Identifier(WAREHOUSES_ID),
            warehouseLatCoord=sql.Identifier(BUILDINGS_GPS_LATITUDE),
            warehouseLonCoord=sql.Identifier(BUILDINGS_GPS_LONGITUDE),
            connectionsSchemeName=sql.Identifier(CONNECTIONS_SCHEME_NAME),
            locationMainWarehousesViewName=sql.Identifier(
                locationMainWarehousesViewName
            ),
            parentLocationIdField=sql.Identifier(parentLocationIdField),
        )

    async def __getMainWarehouses(
        self, acursor, query, parentLocationId: int
    ) -> list[dict]:
        """
        Asynchronous Method to Get All the Main Warehouses from a Given Parent Location ID

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param Composed query: SQL Query to Get All the Main Warehouses from the Given Parent Location
        :param str parentLocationId: Parent Location ID to Compare
        :return: List of Warehouse Connection Dictionaries
        :rtype: list
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get All Main Warehouses
        await asyncio.gather(acursor.execute(query, [parentLocationId]))
        fetchTask = asyncio.create_task(acursor.fetchall())
        await asyncio.gather(fetchTask)
        self._items = fetchTask.result()

        # Get List of Warehouse Dictionaries
        warehouseConns = self.__getWarehouseDicts(self._items)

        return warehouseConns

    def __getCityWarehousesQuery(self):
        """
        Method that Returns the Query to Get All the Warehouses from a Given City ID

        :return: SQL Query
        :rtype: Composed
        """

        return sql.SQL(
            "SELECT {warehouseIdField}, {warehouseLatCoord}, {warehouseLonCoord} FROM {connectionsSchemeName}.{warehousesViewName} WHERE {cityIdField} = (%s)"
        ).format(
            warehouseIdField=sql.Identifier(WAREHOUSES_ID),
            warehouseLatCoord=sql.Identifier(BUILDINGS_GPS_LATITUDE),
            warehouseLonCoord=sql.Identifier(BUILDINGS_GPS_LONGITUDE),
            connectionsSchemeName=sql.Identifier(CONNECTIONS_SCHEME_NAME),
            warehousesViewName=sql.Identifier(WAREHOUSES_VIEW_NAME),
            cityIdField=sql.Identifier(CITIES_ID),
        )

    async def getRegionMainWarehouseIds(self, acursor, countryId: int) -> list[int]:
        """
        Asynchronous Method to Get All the Region Main Warehouse IDs from a Given Country ID

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param int countryId: Country ID where the Warehouses are Located
        :return: List of Warehouse IDs
        :rtype: int
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Query to Get All the Region Main Warehouses from a Given Country ID
        query = self.__getMainWarehousesQuery(
            REGIONS_MAIN_WAREHOUSES_VIEW_NAME, COUNTRIES_ID
        )

        # Get All the Warehouses
        await asyncio.gather(acursor.execute(query, [countryId]))
        fetchTask = asyncio.create_task(acursor.fetchall())
        await asyncio.gather(fetchTask)
        self._items = fetchTask.result()

        # Get List of Warehouse IDs
        warehouseIds = self.__getWarehouseIds(self._items)

        return warehouseIds

    async def getRegionMainWarehouseDicts(self, acursor, countryId: int) -> list[dict]:
        """
        Asynchronous Method to Get All the Region Main Warehouse IDs and Coordinates from a Given Country ID

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param int countryId: Country ID where the Regions are Located
        :return: List of Warehouse Connection Dictionaries
        :rtype: list
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Query to Get All the Region Main Warehouses from a Given Country ID
        query = self.__getMainWarehousesQuery(
            REGIONS_MAIN_WAREHOUSES_VIEW_NAME, COUNTRIES_ID
        )

        getTask = asyncio.create(self.__getMainWarehouses(query, countryId))
        await asyncio.gather(getTask)

        return getTask.result()

    async def getCityMainWarehouseIds(self, acursor, regionId: int) -> list[int]:
        """
        Asynchronous Method to Get All the City Main Warehouse IDs from a Given Region ID

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param int regionId: Region ID where the Warehouses are Located
        :return: List of Warehouse IDs
        :rtype: int
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Query to Get All the City Main Warehouses from a Given Region ID
        query = self.__getMainWarehousesQuery(
            CITIES_MAIN_WAREHOUSES_VIEW_NAME, REGIONS_ID
        )

        # Get All the Warehouses
        await asyncio.gather(acursor.execute(query, [regionId]))
        fetchTask = asyncio.create_task(acursor.fetchall())
        await asyncio.gather(fetchTask)
        self._items = fetchTask.result()

        # Get List of Warehouse IDs
        warehouseIds = self.__getWarehouseIds(self._items)

        return warehouseIds

    async def getCityMainWarehouseDicts(self, acursor, regionId: int) -> list[dict]:
        """
        Asynchronous Method to Get All the City Main Warehouse IDs and Coordinates from a Given Region ID

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param int regionId: Region ID where the Cities are Located
        :return: List of Warehouse Connection Dictionaries
        :rtype: list
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Query to Get All the City Main Warehouses from a Given Region ID
        query = self.__getMainWarehousesQuery(
            CITIES_MAIN_WAREHOUSES_VIEW_NAME, REGIONS_ID
        )

        getTask = asyncio.create_task(self.__getMainWarehouses(query, regionId))
        await asyncio.gather(getTask)

        return getTask.result()

    async def getCityWarehouseIds(self, acursor, cityId: int) -> list[int]:
        """
        Asynchronous Method to Get All the Warehouse IDs from a Given City ID

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param int cityId: City ID where the Warehouses are Located
        :return: List of Warehouse IDs
        :rtype: int
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Query to Get All the Warehouses from a Given City ID
        query = self.__getCityWarehousesQuery()

        # Get All the Warehouses
        await asyncio.gather(acursor.execute(query, [cityId]))
        fetchTask = asyncio.create_task(acursor.fetchall())
        await asyncio.gather(fetchTask)
        self._items = fetchTask.result()

        # Get List of Warehouse IDs
        warehouseIds = self.__getWarehouseIds(self._items)

        return warehouseIds

    async def getCityWarehouseDicts(self, acursor, cityId: int) -> list[dict]:
        """
        Asynchronous Method to Get All the Warehouse IDs and Coordinates from a Given City ID

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param int cityId: City ID where the Warehouses are Located
        :return: List of Warehouse Connection Dictionaries
        :rtype: list
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Query to Get All the City Warehouses from a Given City ID
        query = self.__getCityWarehousesQuery()

        # Get All City Warehouses
        await asyncio.gather(acursor.execute(query, [cityId]))
        fetchTask = asyncio.create_task(acursor.fetchall())
        await asyncio.gather(fetchTask)
        self._items = fetchTask.result()

        # Get List of Warehouse Dictionaries
        warehouseConns = self.__getWarehouseDicts(self._items)

        return warehouseConns

    def __insertWarehouseConnQuery(self):
        """
        Method that Returns the Query to Insert a Warehouse Connection

        :return: SQL Query
        :rtype: Composed
        """

        return sql.SQL(
            "INSERT INTO {fullTableName} ({fields}) VALUES (%s, %s, %s, %s)"
        ).format(
            fullTableName=self._fullTableName,
            fields=sql.SQL(",").join(
                [
                    sql.Identifier(WAREHOUSES_CONN_WAREHOUSE_FROM_ID),
                    sql.Identifier(WAREHOUSES_CONN_WAREHOUSE_TO_ID),
                    sql.Identifier(WAREHOUSES_CONN_ROUTE_DISTANCE),
                    sql.Identifier(WAREHOUSES_CONN_CONN_TYPE),
                ]
            ),
        )

    async def __insertWarehouseSenderConn(
        self,
        acursor,
        ORSGeocoder: ORSGeocoder,
        query,
        connType: str,
        warehouseDict: dict,
        warehouseConnDict: dict,
    ) -> None:
        """
        Method to Insert a Warehouse Sender Connection Asynchronously

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param ORSGeocoder ORSGeocoder: ORSGeocoder Object to Calculate the Route Distance between the Two Warehouses
        :param Composed query: SQL Query to Insert a Warehouse Connection
        :param str connType: Location Connection Level
        :param dict warehouseDict: Warehouse Connection Dictionary of the One that Sends the Packages
        :param dict warehouseConnDict: Warehouse Connection Dictionary of the One that Receives the Packages
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        try:
            # Get Route Distance from the Main Warehouse to Insert and the Inserted Warehouse
            routeDistanceSender = ORSGeocoder.getDrivingRouteDistance(
                warehouseDict[DICT_WAREHOUSE_COORDS],
                warehouseConnDict[DICT_WAREHOUSE_COORDS],
            )

            # Check Route Distance Length
            if routeDistanceSender > ROUTE_DISTANCE_MAX:
                raise RouteLimitSurpassed(
                    warehouseConnDict[DICT_WAREHOUSE_COORDS],
                    warehouseDict[DICT_WAREHOUSE_COORDS],
                    routeDistanceSender,
                    ROUTE_DISTANCE_MAX,
                )

        # There's no Road Connection between the Two Warehouses
        except RouteNotFound as err:
            console.print(err, style="warning")
            return

        # The Road Connection between the Two Warehouses is too Long
        except RouteLimitSurpassed as err:
            console.print(err, style="warning")
            return

        # Get Warehouse and Warehouse Connection ID
        warehouseId = warehouseDict[DICT_WAREHOUSE_ID]
        warehouseConnId = warehouseConnDict[DICT_WAREHOUSE_ID]

        # Insert the Given Warehouse as a Sender
        await asyncio.gather(
            acursor.execute(
                query,
                [warehouseId, warehouseConnId, routeDistanceSender, connType],
            )
        )

        if ROUTES_DEBUG_MODE:
            console.print(
                f"Inserted Warehouse Sender Connection from ID {warehouseId} to ID {warehouseConnId} at {connType}-Level\n",
                style="success",
            )

    async def __insertWarehouseReceiverConn(
        self,
        acursor,
        ORSGeocoder: ORSGeocoder,
        query,
        connType: str,
        warehouseDict: dict,
        warehouseConnDict: dict,
    ):
        """
        Asynchronous Method to Insert a Warehouse Receiver Connection Asynchronously

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param ORSGeocoder ORSGeocoder: ORSGeocoder Object to Calculate the Route Distance between the Two Warehouses
        :param Composed query: SQL Query to Insert a Warehouse Connection
        :param str connType: Location Connection Level
        :param dict warehouseDict: Warehouse Connection Dictionary of the One that Receives the Packages
        :param dict warehouseConnDict: Warehouse Connection Dictionary of the One that Sends the Packages
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        try:
            # Get Route Distance from the Inserted Warehouse to the Main Warehouse to Insert
            routeDistanceReceiver = ORSGeocoder.getDrivingRouteDistance(
                warehouseConnDict[DICT_WAREHOUSE_COORDS],
                warehouseDict[DICT_WAREHOUSE_COORDS],
            )

            # Check Route Distance Length
            if routeDistanceReceiver > ROUTE_DISTANCE_MAX:
                raise RouteLimitSurpassed(
                    warehouseConnDict[DICT_WAREHOUSE_COORDS],
                    warehouseDict[DICT_WAREHOUSE_COORDS],
                    routeDistanceReceiver,
                    ROUTE_DISTANCE_MAX,
                )

        # There's no Road Connection between the Two Warehouses
        except RouteNotFound as err:
            console.print(err, style="warning")
            return

        # The Road Connection between the Two Warehouses is too Long
        except RouteLimitSurpassed as err:
            console.print(err, style="warning")
            return

        # Get Warehouse and Warehouse Connection ID
        warehouseId = warehouseDict[DICT_WAREHOUSE_ID]
        warehouseConnId = warehouseConnDict[DICT_WAREHOUSE_ID]

        # Insert the Given Warehouse as a Receiver
        await asyncio.gather(
            acursor.execute(
                query, [warehouseConnId, warehouseId, routeDistanceReceiver, connType]
            )
        )

        if ROUTES_DEBUG_MODE:
            console.print(
                f"Inserted Warehouse Receiver Connection from ID {warehouseConnId} to ID {warehouseId} at {connType}-Level\n",
                style="success",
            )

    async def __insertMainWarehouseConns(
        self,
        acursor,
        ORSGeocoder: ORSGeocoder,
        connType: str,
        warehouseDict: dict,
        warehouseConns: list[dict],
    ):
        """
        Asynchronous Method to Insert All the Warehouse Connections for a Given Main Warehouse Asynchronously

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param ORSGeocoder ORSGeocoder: ORSGeocoder Object to Calculate the Route Distance between the Two Warehouses
        :param str connType: Location Connection Level
        :param dict warehouseDict: Main Warehouse Connection Dictionary
        :param list warehouseConnDict: List of Warehouse Connection Dictionaries that will be Connected with the Main Warehouse
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Query to Insert Warehouse Connections
        query = self.__insertWarehouseConnQuery()

        # Insert Each Warehouse Connection to its Table Asynchronously
        tasks = []
        for warehouseConnDict in warehouseConns:
            # Check the Warehouse Connection ID. Ignore if they're the Same
            if warehouseConnDict[DICT_WAREHOUSE_ID] == warehouseDict[DICT_WAREHOUSE_ID]:
                continue

            # Insert the Main Warehouse Sender Connection
            tasks.append(
                asyncio.create_task(
                    self.__insertWarehouseSenderConn(
                        acursor,
                        ORSGeocoder,
                        query,
                        connType,
                        warehouseDict,
                        warehouseConnDict,
                    )
                )
            )

            # Insert the Main Warehouse Receiver Connection
            tasks.append(
                asyncio.create_task(
                    self.__insertWarehouseReceiverConn(
                        acursor,
                        ORSGeocoder,
                        query,
                        connType,
                        warehouseDict,
                        warehouseConnDict,
                    )
                )
            )

        try:
            await asyncio.gather(*tasks)

        except Exception as err:
            cancelTasks(tasks)
            raise err

    async def insertRegionMainWarehouse(
        self,
        acursor,
        ORSGeocoder: ORSGeocoder,
        countryId: int,
        regionId: int,
        warehouseDict: dict,
    ) -> None:
        """
        Asynchronous Method to Insert All the Region Main Warehouse Connections for a Given Region

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param ORSGeocoder ORSGeocoder: ORSGeocoder Object to Calculate the Route Distance between the Two Warehouses
        :param int countryId: Country ID where the Region is Located
        :param int regionId: Region ID where the Warehouse is Located
        :param dict warehouseDict: New Region Main Warehouse Connection Dictionary
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get All the Region Main Warehouses at the Given Country ID
        regionMainWarehouses = self.getRegionMainWarehouseDicts(countryId)

        # Get All the City Main Warehouses at the Given Region ID
        cityMainWarehouses = self.getCityMainWarehouseDicts(regionId)

        # Set the Region Main Warehouse Connections
        regionMainTask = asyncio.create_task(
            self.__insertMainWarehouseConns(
                acursor,
                ORSGeocoder,
                CONN_TYPE_REGION,
                warehouseDict,
                regionMainWarehouses,
            )
        )

        # Set the City Main Warehouse Connections
        cityMainTask = asyncio.create_task(
            self.__insertMainWarehouseConns(
                acursor,
                ORSGeocoder,
                CONN_TYPE_REGION,
                warehouseDict,
                cityMainWarehouses,
            )
        )

        tasks = [regionMainTask, cityMainTask]
        try:
            await asyncio.gather(*tasks)

        except Exception as err:
            cancelTasks(tasks)
            raise err

        if not ROUTES_DEBUG_MODE:
            console.print()

    async def insertCityMainWarehouse(
        self,
        acursor,
        ORSGeocoder: ORSGeocoder,
        regionId: int,
        cityId: int,
        parentWarehouseDict: dict,
        warehouseDict: dict,
    ) -> None:
        """
        Asynchronous Method to Insert All the City Main Warehouse Connections for a Given City

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param ORSGeocoder ORSGeocoder: ORSGeocoder Object to Calculate the Route Distance between the Two Warehouses
        :param int regionId: Region ID where the City is Located
        :param int cityId: City ID where the Warehouse is Located
        :param dict parentWarehouseDict: Region Main Warehouse Connection Dictionary
        :param dict warehouseDict: New City Main Warehouse Connection Dictionary
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get All the City Main Warehouses at the Given Region ID
        cityMainWarehouses = self.getCityMainWarehouseDicts(regionId)

        # Get All the City Warehouses at the Given City ID
        cityWarehouses = self.getCityWarehouseDicts(cityId)

        # Set the Region Main Warehouse Connection
        regionMainTask = asyncio.create_task(
            self.__insertMainWarehouseConns(
                acursor,
                ORSGeocoder,
                CONN_TYPE_REGION,
                parentWarehouseDict,
                [warehouseDict],
            )
        )

        # Set the City Main Warehouse Connections
        cityMainTask = asyncio.create_task(
            self.__insertMainWarehouseConns(
                acursor,
                ORSGeocoder,
                CONN_TYPE_CITY,
                warehouseDict,
                cityMainWarehouses,
            )
        )

        # Set the City Warehouse Connections
        cityTask = asyncio.create_task(
            self.__insertMainWarehouseConns(
                acursor,
                ORSGeocoder,
                CONN_TYPE_CITY,
                warehouseDict,
                cityWarehouses,
            )
        )

        tasks = [regionMainTask, cityMainTask, cityTask]
        try:
            await asyncio.gather(*tasks)

        except Exception as err:
            cancelTasks(tasks)
            raise err

        if not ROUTES_DEBUG_MODE and RICH_LOGGER_DEBUG_MODE:
            console.print("\n")

    async def insertCityWarehouse(
        self,
        acursor,
        ORSGeocoder: ORSGeocoder,
        warehouseDict: dict,
        warehouseConnDict: dict,
    ):
        """
        Asynchronous Method to Insert the Warehouse Connection with the Given Main Warehouse at the City ID where the Warehouse is Located Asynchronously

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param ORSGeocoder ORSGeocoder: ORSGeocoder Object to Calculate the Route Distance between the Two Warehouses
        :param dict warehouseDict: Warehouse Connection Dictionary
        :param list warehouseConnDict: Warehouse Connection Dictionary that will be Connected with the Warehouse
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Insert the Warehouse Connection to its Table Asynchronously
        await asyncio.gather(
            self.__insertMainWarehouseConns(
                acursor,
                ORSGeocoder,
                CONN_TYPE_CITY,
                warehouseDict,
                [warehouseConnDict],
            )
        )

        if not ROUTES_DEBUG_MODE and RICH_LOGGER_DEBUG_MODE:
            console.print("\n")
