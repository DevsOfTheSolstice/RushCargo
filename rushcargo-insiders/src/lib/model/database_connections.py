import asyncio
from psycopg import sql

from .constants import *

from .database import console

from ..geocoding.constants import NOMINATIM_LONGITUDE, NOMINATIM_LATITUDE
from ..geocoding.routingpy import RoutingPyGeocoder


def getLocationInfo(locationTableName: str) -> tuple[str, str] | None:
    """
    Function to Get the Location Connection Type and Location ID Field for a Given Location Table Name

    :return: Location Connection Type and Location ID Field if Found. Otherwise, ``None``
    :rtype: Tuple if Found. Otherwise, NoneType
    """

    if locationTableName == PROVINCE_TABLENAME:
        return CONN_TYPE_PROVINCE, PROVINCE_ID

    elif locationTableName == REGION_TABLENAME:
        return CONN_TYPE_REGION, REGION_ID

    elif locationTableName == CITY_TABLENAME:
        return CONN_TYPE_CITY, CITY_ID

    return None


class WarehouseConnectionTable:
    """
    Warehouse Connection Remote Table Class
    """

    # Database Connection
    _c = None
    _items = None

    # Table Name and ID Column Name
    _tableName = WAREHOUSE_CONN_TABLENAME
    _tablePKName = WAREHOUSE_CONN_ID

    # Constructor
    def __init__(self, remoteCursor):
        """
        Warehouse Connection Remote Table Class Constructor

        :param Cursor remoteCursor: Remote Database Connection Cursor
        """

        # Store Database Connection Cursor
        self._c = remoteCursor

    def __fetchall(self) -> None:
        """
        Method to Fetch All Items from ``self._items``

        :return: Nothing
        :rtype: NoneType
        """

        # Fetch the Items
        self._items = self._items.fetchall()

    def __getWarehouseDicts(
        self, warehouseConnsList: list[tuple[int, float, float]]
    ) -> list[dict]:
        """
        Method to Get a List of Warehouse Dictionaries, that Contain its ID and Coordinates based on Fetched Warehouse Connections from the Remote Table

        :param list warehouseConnList: List of Fetched Warehouse Connections from the Remote Table
        :return: List of Warehouse Dictionaries that Contain its ID and Coordinates
        :rtype: list
        """

        warehouseList = []

        for w in warehouseConnsList:
            warehouseDict = {}

            warehouseDict[DICT_WAREHOUSES_ID] = w[0]
            warehouseDict[DICT_WAREHOUSES_COORDS] = {
                NOMINATIM_LATITUDE: w[1],
                NOMINATIM_LONGITUDE: w[2],
            }

            warehouseList.append(warehouseDict)

        return warehouseList

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
            "SELECT {locationIdField} FROM {locationTableName} WHERE {warehouseIdField} = (%s)"
        ).format(
            locationIdField=sql.Identifier(locationIdField),
            warehouseIdField=sql.Identifier(warehouseIdField),
            locationTableName=sql.Identifier(tableName),
        )

    def isMainWarehouse(self, warehouseId: int) -> tuple[str, int] | None:
        """
        Method that Returns the Query to Check if a Given Warehouse is Main at Any Location

        :param str warehouseId: Warehouse ID to Compare
        :return: The Table Name where the Given Warehouse ID is the Main One if Found, and the Location ID where It's. Otherwise, ``None``
        :rtype: tuple if the Given Warehouse ID is the Main for Any Location. Otherwise, NoneType
        """

        # Get the Query to Check if the Given Warehouse is the Main One to Any Province
        provinceMainQuery = self.__isMainWarehouseQuery(
            PROVINCE_ID, PROVINCE_TABLENAME, PROVINCE_FK_WAREHOUSE
        )

        # Get the Query to Check if the Given Warehouse is the Main One to Any Region
        regionMainQuery = self.__isMainWarehouseQuery(
            REGION_ID, REGION_TABLENAME, REGION_FK_WAREHOUSE
        )

        # Get the Query to Check if the Given Warehouse is the Main One to Any City
        cityMainQuery = self.__isMainWarehouseQuery(
            CITY_ID, CITY_TABLENAME, CITY_FK_WAREHOUSE
        )

        # Execute the Queries
        try:
            # Check if the Warehouse is the Main One to Any Province
            provinceId = self._c.execute(provinceMainQuery, [warehouseId]).fetchone()

            if provinceId != None:
                return PROVINCE_TABLENAME, provinceId

            # Check if the Warehouse is the Main One to Any Region
            regionId = self._c.execute(regionMainQuery, [warehouseId]).fetchone()

            if regionId != None:
                return REGION_TABLENAME, regionId

            # Check if the Warehouse is the Main One to Any City
            cityId = self._c.execute(cityMainQuery, [warehouseId]).fetchone()

            if cityId != None:
                return CITY_TABLENAME, cityId

            return None

        except Exception as err:
            raise err

    def __removeSenderMainWarehouseQuery(self, locationIdField: str):
        """
        Method that Returns the Query to Remove a Main Warehouse of a Given Location as a Sender from All its Connections

        :param str locationIdField: Location Type ID Field to Compare
        :return: SQL Query
        :rtype: Composed
        """

        return sql.SQL(
            "DELETE FROM {tableName} WHERE EXISTS (SELECT {sendersConnIdField} FROM {sendersViewName} {senders} WHERE {senders}.{locationIdField} = (%s) AND {senders}.{warehouseIdField} = (%s) AND {senders}.{warehouseConnType} = (%s))"
        ).format(
            tableName=sql.Identifier(self._tableName),
            idField=sql.Identifier(self._tablePKName),
            sendersConnIdField=sql.Identifier(SENDERS_WAREHOUSE_CONN_ID),
            sendersViewName=sql.Identifier(WAREHOUSES_SENDERS_VIEWNAME),
            senders=sql.Identifier(SENDERS),
            locationIdField=sql.Identifier(locationIdField),
            warehouseIdField=sql.Identifier(SENDERS_WAREHOUSE_ID),
            warehouseConnType=sql.Identifier(WAREHOUSE_CONN_CONN_TYPE),
        )

    def __removeReceiverMainWarehouseQuery(self, locationIdField: str):
        """
        Method that Returns the Query to Remove a Main Warehouse of a Given Location as a Receiver from All its Connections

        :param str locationIdField: Location Type ID Field to Compare
        :return: SQL Query
        :rtype: Composed
        """

        return sql.SQL(
            "DELETE FROM {tableName} WHERE EXISTS (SELECT {receiversConnIdField} FROM {receiversViewName} {receivers} WHERE {receivers}.{locationIdField} = %s AND {receivers}.{warehouseIdField} = %s AND {receivers}.{warehouseConnType} =%s)"
        ).format(
            tableName=sql.Identifier(self._tableName),
            idField=sql.Identifier(self._tablePKName),
            receiversConnIdField=sql.Identifier(RECEIVERS_WAREHOUSE_CONN_ID),
            receiversViewName=sql.Identifier(WAREHOUSES_RECEIVERS_VIEWNAME),
            receivers=sql.Identifier(RECEIVERS),
            locationIdField=sql.Identifier(locationIdField),
            warehouseIdField=sql.Identifier(RECEIVERS_WAREHOUSE_ID),
            warehouseConnType=sql.Identifier(WAREHOUSE_CONN_CONN_TYPE),
        )

    def __removeMainWarehouse(
        self,
        locationTableName: str,
        locationId: int,
        warehouseId: int,
    ) -> None:
        """
        Method to Remove a Main Warehouse of a Given Location as a Sender and as a Receiver from All of its Warehouse Connections at a Given Location Level

        :param str locationTableName: Location Table Name where the Warehouse is Located and Set as the Main One
        :param str locationId: Location ID at its Table where the Warehouse is Located
        :param int warehouseId: Main Warehouse ID that is going to be Removed from its Warehouse Connections at the Given Location Level
        :return: Nothing
        :rtype: NoneType
        """

        locationType, locationIdField = getLocationInfo(locationTableName)

        # Get Query to Remove the Given Warehouse as a Sender
        senderQuery = self.__removeSenderMainWarehouseQuery(locationIdField)

        # Get Query to Remove the Given Warehouse as a Receiver
        receiverQuery = self.__removeReceiverMainWarehouseQuery(locationIdField)

        # Execute the Query
        try:
            # Remove Given Warehouse as a Sender
            self._c.execute(senderQuery, [locationId, warehouseId, locationType])

            console.print(
                f"Removed Warehouse ID {warehouseId} as a Sender at {locationType}-Level",
                style="success",
            )

            # Remove Given Warehouse as a Receiver
            self._c.execute(receiverQuery, [locationId, warehouseId, locationType])

            console.print(
                f"Removed Warehouse ID {warehouseId} as a Receiver at {locationType}-Level",
                style="success",
            )

        except Exception as err:
            raise err

    def removeProvinceMainWarehouse(self, provinceId: int, warehouseId: int) -> None:
        """
        Method to Remove a Given Province Main Warehouse as a Sender and as a Receiver from All of its Warehouse Connections

        :param str provinceId: Province ID where the Warehouse is Located and Set as the Main One
        :param int warehouseId: Main Warehouse ID that is going to be Removed from its Warehouse Connections at the Given Location Level (Province)
        :return: Nothing
        :rtype: NoneType
        """

        return self.__removeMainWarehouse(PROVINCE_TABLENAME, provinceId, warehouseId)

    def removeRegionMainWarehouse(self, regionId: int, warehouseId: int) -> None:
        """
        Method to Remove a Given Region Main Warehouse as a Sender and as a Receiver from All of its Warehouse Connections

        :param str regionId: Region ID where the Warehouse is Located and Set as the Main One
        :param int warehouseId: Main Warehouse ID that is going to be Removed from its Warehouse Connections at the Given Location Level (Region)
        :return: Nothing
        :rtype: NoneType
        """

        return self.__removeMainWarehouse(REGION_TABLENAME, regionId, warehouseId)

    def removeCityMainWarehouse(self, cityId: int, warehouseId: int) -> None:
        """
        Method to Remove a Given City Main Warehouse as a Sender and as a Receiver from All of its Warehouse Connections

        :param str cityId: City ID where the Warehouse is Located and Set as the Main One
        :param int warehouseId: Main Warehouse ID that is going to be Removed from its Warehouse Connections at the Given Location Level (City)
        :return: Nothing
        :rtype: NoneType
        """

        return self.__removeMainWarehouse(CITY_TABLENAME, cityId, warehouseId)

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
            "SELECT {warehouseIdField}, {warehouseLatCoord}, {warehouseLonCoord} FROM {locationMainWarehousesViewName} WHERE {parentLocationIdField} = (%s)"
        ).format(
            warehouseIdField=sql.Identifier(WAREHOUSE_ID),
            warehouseLatCoord=sql.Identifier(BUILDING_GPS_LATITUDE),
            warehouseLonCoord=sql.Identifier(BUILDING_GPS_LONGITUDE),
            locationMainWarehousesViewName=sql.Identifier(
                locationMainWarehousesViewName
            ),
            parentLocationIdField=sql.Identifier(parentLocationIdField),
        )

    def __getMainWarehouses(self, query, parentLocationId: int) -> list[dict]:
        """
        Method to Get All the Main Warehouses from a Given Parent Location ID

        :param Composed query: SQL Query to Get All the Main Warehouses from the Given Parent Location
        :param str parentLocationId: Parent Location ID to Compare
        :return: List of Warehouse Connection Dictionaries
        :rtype: list
        """

        # Execute the Query and Fetch the Items
        try:
            # Get All Main Warehouses
            self._items = self._c.execute(
                query,
                [parentLocationId],
            )

            self.__fetchall()

        except Exception as err:
            raise err

        # Get List of Warehouse Dictionaries
        warehouseConns = self.__getWarehouseDicts(self._items)

        return warehouseConns

    def getMainProvinceWarehouses(self, countryId: int) -> list[dict]:
        """
        Method to Get All the Province Main Warehouses from a Given Country ID

        :param int countryId: Country ID where the Provinces are Located
        :return: List of Warehouse Connection Dictionaries
        :rtype: list
        """

        # Get Query to Get All the Province Main Warehouses from a Given Country ID
        query = self.__getMainWarehousesQuery(PROVINCE_MAIN_WAREHOUSES, COUNTRY_ID)

        return self.__getMainWarehouses(query, countryId)

    def getMainRegionWarehouses(self, provinceId: int) -> list[dict]:
        """
        Method to Get All the Region Main Warehouses from a Given Province ID

        :param int provinceId: Province ID where the Regions are Located
        :return: List of Warehouse Connection Dictionaries
        :rtype: list
        """

        # Get Query to Get All the Region Main Warehouses from a Given Province ID
        query = self.__getMainWarehousesQuery(REGION_MAIN_WAREHOUSES, PROVINCE_ID)

        return self.__getMainWarehouses(query, provinceId)

    def getMainCityWarehouses(self, regionId: int) -> list[dict]:
        """
        Method to Get All the City Main Warehouses from a Given Region ID

        :param int regionId: Region ID where the Cities are Located
        :return: List of Warehouse Connection Dictionaries
        :rtype: list
        """

        # Get Query to Get All the City Main Warehouses from a Given Region ID
        query = self.__getMainWarehousesQuery(CITY_MAIN_WAREHOUSES, REGION_ID)

        return self.__getMainWarehouses(query, regionId)

    def __getCityWarehousesQuery(self):
        """
        Method that Returns the Query to Get All the Warehouses from a Given City ID

        :return: SQL Query
        :rtype: Composed
        """

        return sql.SQL(
            "SELECT {warehouseIdField}, {warehouseLatCoord}, {warehouseLonCoord} FROM {warehousesViewName} WHERE {cityIdField} = (%s)"
        ).format(
            warehouseIdField=sql.Identifier(WAREHOUSE_ID),
            warehouseLatCoord=sql.Identifier(BUILDING_GPS_LATITUDE),
            warehouseLonCoord=sql.Identifier(BUILDING_GPS_LONGITUDE),
            warehousesViewName=sql.Identifier(WAREHOUSES_VIEWNAME),
            cityIdField=sql.Identifier(CITY_ID),
        )

    def getCityWarehouses(self, cityId: int) -> list[dict]:
        """
        Method to Get All the Warehouses from a Given City ID

        :param int cityId: City ID where the Warehouses are Located
        :return: List of Warehouse Connection Dictionaries
        :rtype: list
        """

        # Get Query to Get All the City Warehouses from a Given City ID
        query = self.__getCityWarehousesQuery()

        # Execute the Query and Fetch the Items
        try:
            # Get All City Warehouses
            self._items = self._c.execute(
                query,
                [cityId],
            )
            self.__fetchall()

        except Exception as err:
            raise err

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
    async def __insertWarehouseSenderConn(
        self,
        routingPyGeocoder: RoutingPyGeocoder,
        query,
        connType: str,
        warehouseDict: dict,
        warehouseConnDict: dict,
    ) -> None:
        """
        Method to Insert a Warehouse Sender Connection Asynchronously

        :param RoutingPyGeocoder routingPyGeocoder: RoutingPyGeocoder Object to Calculate the Route Distance between the Two Warehouses
        :param Composed query: SQL Query to Insert a Warehouse Connection
        :param str connType: Location Connection Level
        :param dict warehouseDict: Warehouse Connection Dictionary of the One that Sends the Packages
        :param dict warehouseConnDict: Warehouse Connection Dictionary of the One that Receives the Packages
        :return: Nothing
        :rtype: NoneType
        """

        # Get Route Distance from the Main Warehouse to Insert and the Inserted Warehouse
        routeDistanceSender = routingPyGeocoder.getRouteDistance(
            warehouseDict[DICT_WAREHOUSES_COORDS],
            warehouseConnDict[DICT_WAREHOUSES_COORDS],
        )

        # Get Warehouse and Warehouse Connection ID
        warehouseId = warehouseDict[DICT_WAREHOUSES_ID]
        warehouseConnId = warehouseConnDict[DICT_WAREHOUSES_ID]

        # Execute the Query
        try:
            # Insert the Given Warehouse as a Sender
            self._c.execute(
                query,
                [warehouseId, warehouseConnId, routeDistanceSender, connType],
            )

            console.print(
                f"Inserted Warehouse Sender Connection from ID {warehouseId} to ID {warehouseConnId} at {connType}-Level",
                style="success",
            )

        except Exception as err:
            raise err

    async def __insertWarehouseReceiverConn(
        self,
        routingPyGeocoder: RoutingPyGeocoder,
        query,
        connType: str,
        warehouseDict: dict,
        warehouseConnDict: dict,
    ):
        """
        Method to Insert a Warehouse Receiver Connection Asynchronously

        :param RoutingPyGeocoder routingPyGeocoder: RoutingPyGeocoder Object to Calculate the Route Distance between the Two Warehouses
        :param Composed query: SQL Query to Insert a Warehouse Connection
        :param str connType: Location Connection Level
        :param dict warehouseDict: Warehouse Connection Dictionary of the One that Receives the Packages
        :param dict warehouseConnDict: Warehouse Connection Dictionary of the One that Sends the Packages
        :return: Nothing
        :rtype: NoneType
        """

        # Get Route Distance from the Inserted Warehouse to the Main Warehouse to Insert
        routeDistanceReceiver = routingPyGeocoder.getRouteDistance(
            warehouseConnDict[DICT_WAREHOUSES_COORDS],
            warehouseDict[DICT_WAREHOUSES_COORDS],
        )

        # Get Warehouse and Warehouse Connection ID
        warehouseId = warehouseDict[DICT_WAREHOUSES_ID]
        warehouseConnId = warehouseConnDict[DICT_WAREHOUSES_ID]

        # Execute the Query
        try:
            # Insert the Given Warehouse as a Receiver
            self._c.execute(
                query, [warehouseConnId, warehouseId, routeDistanceReceiver, connType]
            )

            console.print(
                f"Inserted Warehouse Receiver Connection from ID {warehouseConnId} to ID {warehouseId} at {connType}-Level",
                style="success",
            )

        except Exception as err:
            raise err

    async def __insertMainWarehouseConns(
        self,
        routingPyGeocoder: RoutingPyGeocoder,
        connType: str,
        warehouseDict: dict,
        warehouseConns: list[dict],
    ):
        """
        Method to Insert All the Warehouse Connections for a Given Main Warehouse Asynchronously

        :param RoutingPyGeocoder routingPyGeocoder: RoutingPyGeocoder Object to Calculate the Route Distance between the Two Warehouses
        :param str connType: Location Connection Level
        :param dict warehouseDict: Main Warehouse Connection Dictionary
        :param list warehouseConnDict: List of Warehouse Connection Dictionaries that will be Connected with the Main Warehouse
        :return: Nothing
        :rtype: NoneType
        """

        # Get Query to Insert Warehouse Connections
        query = self.__insertWarehouseConnQuery()

        # Insert Each Warehouse Connection to its Table Asynchronously
        try:
            async with asyncio.TaskGroup() as tg:
                for warehouseConnDict in warehouseConns:
                    # Check the Warehouse Connection ID. Ignore if they're the Same
                    if (
                        warehouseConnDict[DICT_WAREHOUSES_ID]
                        == warehouseDict[DICT_WAREHOUSES_ID]
                    ):
                        continue

                    # Insert the Main Warehouse Sender Connection
                    tg.create_task(
                        self.__insertWarehouseSenderConn(
                            routingPyGeocoder,
                            query,
                            connType,
                            warehouseDict,
                            warehouseConnDict,
                        )
                    )

                    # Insert the Main Warehouse Receiver Connection
                    tg.create_task(
                        self.__insertWarehouseReceiverConn(
                            routingPyGeocoder,
                            query,
                            connType,
                            warehouseDict,
                            warehouseConnDict,
                        )
                    )

                    # Sleep for N Seconds
                    await asyncio.sleep(ASYNC_SLEEP)

        except Exception as err:
            console.print(err, style="warning")

    def insertCityWarehouse(
        self,
        routingPyGeocoder: RoutingPyGeocoder,
        warehouseDict: dict,
        warehouseConnDict: dict,
    ):
        """
        Method to Insert the Warehouse Connection with the Given Main Warehouse at the City ID where the Warehouse is Located Asynchronously

        :param RoutingPyGeocoder routingPyGeocoder: RoutingPyGeocoder Object to Calculate the Route Distance between the Two Warehouses
        :param dict warehouseDict: Warehouse Connection Dictionary
        :param list warehouseConnDict: Warehouse Connection Dictionary that will be Connected with the Warehouse
        :return: Nothing
        :rtype: NoneType
        """

        # Insert the Warehouse Connection to its Table Asynchronously
        self.__insertMainWarehouseConns(routingPyGeocoder, CITY_ID, warehouseDict, [warehouseConnDict])

    def insertProvinceMainWarehouse(
        self,
        routingPyGeocoder: RoutingPyGeocoder,
        countryId: int,
        provinceId: int,
        warehouseDict: dict,
    ) -> None:
        """
        Method to Insert All the Province Main Warehouse Connections for a Given Province

        :param RoutingPyGeocoder routingPyGeocoder: RoutingPyGeocoder Object to Calculate the Route Distance between the Two Warehouses
        :param int countryId: Country ID where the Province is Located
        :param int provinceId: Province ID where the Warehouse is Located
        :param dict warehouseDict: New Province Main Warehouse Connection Dictionary
        :return: Nothing
        :rtype: NoneType
        """

        # Get All the Province Main Warehouses at the Given Country ID
        provinceMainWarehouses = self.getMainProvinceWarehouses(countryId)

        # Get All the Region Main Warehouses at the Given Province ID
        regionMainWarehouses = self.getMainRegionWarehouses(provinceId)

        # Set the Province Main Warehouse Connections
        asyncio.run(
            self.__insertMainWarehouseConns(
                routingPyGeocoder,
                CONN_TYPE_PROVINCE,
                warehouseDict,
                provinceMainWarehouses,
            )
        )

        # Set the Region Main Warehouse Connections
        asyncio.run(
            self.__insertMainWarehouseConns(
                routingPyGeocoder,
                CONN_TYPE_PROVINCE,
                warehouseDict,
                regionMainWarehouses,
            )
        )

    def insertRegionMainWarehouse(
        self,
        routingPyGeocoder: RoutingPyGeocoder,
        provinceId: int,
        regionId: int,
        parentWarehouseDict: dict,
        warehouseDict: dict,
    ) -> None:
        """
        Method to Insert All the Region Main Warehouse Connections for a Given Region

        :param RoutingPyGeocoder routingPyGeocoder: RoutingPyGeocoder Object to Calculate the Route Distance between the Two Warehouses
        :param int provinceId: Province ID where the Region is Located
        :param int regionId: Region ID where the Warehouse is Located
        :param dict parentWarehouseDict: Province Main Warehouse Connection Dictionary
        :param dict warehouseDict: New Region Main Warehouse Connection Dictionary
        :return: Nothing
        :rtype: NoneType
        """

        # Get All the Region Main Warehouses at the Given Province ID
        regionMainWarehouses = self.getMainRegionWarehouses(provinceId)

        # Get All City the Main Warehouses at the Given Region ID
        cityMainWarehouses = self.getMainCityWarehouses(regionId)

        # Set the Province Main Warehouse Connection
        asyncio.run(
            self.__insertMainWarehouseConns(
                routingPyGeocoder,
                CONN_TYPE_PROVINCE,
                parentWarehouseDict,
                [warehouseDict],
            )
        )

        # Set the Region Main Warehouse Connections
        asyncio.run(
            self.__insertMainWarehouseConns(
                routingPyGeocoder,
                CONN_TYPE_REGION,
                warehouseDict,
                regionMainWarehouses,
            )
        )

        # Set the City Main Warehouse Connections
        asyncio.run(
            self.__insertMainWarehouseConns(
                routingPyGeocoder,
                CONN_TYPE_REGION,
                warehouseDict,
                cityMainWarehouses,
            )
        )

    def insertCityMainWarehouse(
        self,
        routingPyGeocoder: RoutingPyGeocoder,
        regionId: int,
        cityId: int,
        parentWarehouseDict: dict,
        warehouseDict: dict,
    ) -> None:
        """
        Method to Insert All the City Main Warehouse Connections for a Given City

        :param RoutingPyGeocoder routingPyGeocoder: RoutingPyGeocoder Object to Calculate the Route Distance between the Two Warehouses
        :param int regionId: Region ID where the City is Located
        :param int cityId: City ID where the Warehouse is Located
        :param dict parentWarehouseDict: Region Main Warehouse Connection Dictionary
        :param dict warehouseDict: New City Main Warehouse Connection Dictionary
        :return: Nothing
        :rtype: NoneType
        """

        # Get All the City Main Warehouses at the Given Region ID
        cityMainWarehouses = self.getMainCityWarehouses(regionId)

        # Get All the City Warehouses at the Given City ID
        cityWarehouses = self.getCityWarehouses(cityId)

        # Set the Region Main Warehouse Connection
        asyncio.run(
            self.__insertMainWarehouseConns(
                routingPyGeocoder,
                CONN_TYPE_REGION,
                parentWarehouseDict,
                [warehouseDict],
            )
        )

        # Set the City Main Warehouse Connections
        asyncio.run(
            self.__insertMainWarehouseConns(
                routingPyGeocoder,
                CONN_TYPE_CITY,
                warehouseDict,
                cityMainWarehouses,
            )
        )

        # Set the City Warehouse Connections
        asyncio.run(
            self.__insertMainWarehouseConns(
                routingPyGeocoder,
                CONN_TYPE_CITY,
                warehouseDict,
                cityWarehouses,
            )
        )
