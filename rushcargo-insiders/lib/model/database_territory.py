import asyncio

from psycopg import sql

from rich.prompt import IntPrompt

from .classes import Country, Region, City
from .constants import *
from .database import console
from .database_tables import (
    BaseTable,
    uniqueInserted,
    uniqueInsertedMult,
    insertedRow,
    getTable,
)

from ..terminal.clear import clear


class CountriesTable(BaseTable):
    """
    Class that Handles the SQL Operations related to the Remote SQL Countries Table
    """

    def __init__(self):
        """
        Countries Remote Table Class Constructor
        """

        # Initialize Base Table Class
        super().__init__(COUNTRIES_TABLE_NAME, COUNTRIES_ID, LOCATIONS_SCHEME_NAME)

    def __getFetchedObjects(self) -> list[Country]:
        """
        Method to Get a List of Fetched Countries Objects from ``self_items``

        :return: List of Fetched Countries Objects
        :rtype: list
        """

        countriesList = []

        for item in self._items:
            # Intialize Country from the SQL Fetched Row
            c = Country.fromFetchedItem(item)
            countriesList.append(c)

        return countriesList

    def __print(self, countriesList: list[Country]) -> None:
        """
        Method that Prints the Fetched Countries from its Remote Table

        :param list countriesList: Fetched Countries Objects to Print
        :return: Nothing
        :rtype: NoneType
        """

        # Number of Countries to Print
        nRows = len(countriesList)

        # Initialize Rich Table
        table = getTable("Countries", nRows)

        # Add Country Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Phone Prefix", justify="left", max_width=PHONE_PREFIX_NCHAR)

        # Add Countries Rows to Rich Table
        for c in countriesList:
            table.add_row(str(c.countryId), c.name, str(c.phonePrefix))

        console.print(table)

    def __insertQuery(self):
        """
        Method that Retuns a Query to Insert a New Country to its Remote Table

        :return: SQL Query to Insert a New Country
        :rtype: Composed
        """

        return sql.SQL(
            "INSERT INTO {schemeName}.{tableName} ({fields}) VALUES (%s, %s)"
        ).format(
            schemeName=sql.Identifier(self._schemeName),
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [sql.Identifier(COUNTRIES_NAME), sql.Identifier(COUNTRIES_PHONE_PREFIX)]
            ),
        )

    async def add(self, aconn, countryName: str) -> None:
        """
        Asynchronous Method to Insert a New Country to the Country Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str countryName: Country Name to Insert
        :returns: None
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Check if the Country has already been Inserted
        getTask = asyncio.create_task(
            self.get(aconn, COUNTRIES_NAME, countryName, False)
        )
        await asyncio.gather(getTask)
        country = getTask.result()

        if country != None:
            uniqueInserted(COUNTRIES_TABLE_NAME, COUNTRIES_NAME, countryName)
            return

        # Ask for the Country Fields
        console.print("Adding New Country...", style="caption")
        phonePrefix = IntPrompt.ask("Enter Phone Prefix")

        # Get Query to Insert the New Country
        insertQuery = self.__insertQuery()

        # Execute the Query and Print a Success Message
        await asyncio.gather(
            aconn.cursor().execute(insertQuery, [countryName, phonePrefix])
        )
        insertedRow(countryName, self._tableName)

    async def get(
        self,
        aconn,
        field: str,
        value,
        printItems: bool = True,
    ) -> list[Country] | None:
        """
        Asynchronous Method to Filter Countries from its Remote Table based on a Given Field-Value Pair

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str field: Country Field that will be Used to Compare in the Country Table
        :param value: Value to Compare
        :param bool printItems: Specifies whether to Print or not the Fetched Items. Default is ``True``
        :return: List of Fetched Countries Objects if the Table isn't Empty. Otherwise, ``None``
        :rtype: list if the Table isn't Empty. Otherwise, NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Fetch Filtered Countries
        queryTask = asyncio.gather(
            BaseTable._get(self, aconn.cursor(), field, value, COUNTRIES_NAME)
        )

        # Clear Terminal
        if printItems:
            clear()

        await queryTask

        # Get the Countries Objects from the Fetched Countries
        countriesList = self.__getFetchedObjects()

        # Print Filtered Countries
        if printItems:
            self.__print(countriesList)

        return None if len(countriesList) == 0 else countriesList

    async def find(self, aconn, field: str, value) -> Country | None:
        """
        Asynchronous Method to Find a Country at its Remote Table based on its Unique Fields

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str field: Country Field that will be Used to Compare in the Country Table
        :param value: Unique Value to Compare
        :return: Country Object if Found. Otherwise, ``None``
        :rtype: Country if Found. Otherwise, NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Country from its Remote Table
        getTask = asyncio.create_task(self.get(aconn, field, value, False))
        await asyncio.gather(getTask)
        country = getTask.result()

        # Get Country Object from the Fetched Item
        if country == None:
            return None

        return country[0]

    async def all(self, aconn, orderBy: str, desc: bool) -> list[Country] | None:
        """
        Asynchronous Method that Prints All the Countries Stored at its Remote Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str orderBy: Country Field that will be Used to Sort the Country Table
        :param bool desc: Specificies whether to Sort in Ascending Order (``False``) or in Descending Order (``True``)
        :return: List of Fetched Countries Objects if the Table isn't Empty. Otherwise, ``None``
        :rtype: list if the Table isn't Empty. Otherwise, NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Fetch All Countries
        queryTask = asyncio.gather(BaseTable._all(self, aconn.cursor(), orderBy, desc))

        # Clear Terminal
        clear()

        await queryTask

        # Get the Countries Objects from the Fetched Countries
        countriesList = self.__getFetchedObjects()

        # Print All Countries
        self.__print(countriesList)

        return None if len(countriesList) == 0 else countriesList

    async def modify(self, aconn, countryId: int, field: str, value) -> None:
        """
        Asynchronous Method to Modify a Country Field to its Remote Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int countryId: Country ID from its Remote Table
        :param str field: Country Field to Modify
        :param value: Country Field Value to be Assigned
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        await asyncio.gather(
            BaseTable._modify(self, aconn.cursor(), countryId, field, value)
        )

    async def remove(self, aconn, countryId: int) -> None:
        """
        Asynchronous Method to Remove a Country Row from its Remote Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int countryId: Country ID from its Remote Table
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        await asyncio.gather(BaseTable._remove(self, aconn.cursor(), countryId))


class RegionsTable(BaseTable):
    """
    Class that Handles the SQL Operations related to the Remote SQL Regions Table
    """

    def __init__(self):
        """
        Regions Remote Table Class Constructor
        """

        # Initialize Base Table Class
        super().__init__(REGIONS_TABLE_NAME, REGIONS_ID, LOCATIONS_SCHEME_NAME)

    def __getFetchedObjects(self) -> list[Region]:
        """
        Method to Get a List of Fetched Regions Objects from ``self_items``

        :return: List of Fetched Regions Objects
        :rtype: list
        """

        regionsList = []

        for item in self._items:
            # Intialize Region from the SQL Fetched Row
            r = Region.fromFetchedItem(item)
            regionsList.append(r)

        return regionsList

    def __print(self, regionsList: list[Region]) -> None:
        """
        Method that Prints the Fetched Regions from its Remote Table

        :param list regionsList: Fetched Countries Objects to Print
        :return: Nothing
        :rtype: NoneType
        """

        # Number of Regions to Print
        nRows = len(regionsList)

        # Initialize Rich Table
        table = getTable("Regions", nRows)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Country ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Air Forwarder ID", justify="left", max_width=FORWARDER_NCHAR)
        table.add_column(
            "Ocean Forwarder ID", justify="left", max_width=FORWARDER_NCHAR
        )
        table.add_column("Warehouse ID", justify="left", max_width=WAREHOUSE_NCHAR)

        # Add Regions Rows to Rich Table
        for r in regionsList:
            table.add_row(
                str(r.regionId),
                r.name,
                str(r.countryId),
                str(r.airForwarderId),
                str(r.oceanForwarderId),
                str(r.warehouseId),
            )

        console.print(table)

    def __insertQuery(self):
        """
        Method that Retuns a Query to Insert a New Region to its Remote Table

        :return: SQL Query to Insert a New Region
        :rtype: Composed
        """

        return sql.SQL(
            "INSERT INTO {schemeName}.{tableName} ({fields}) VALUES (%s, %s)"
        ).format(
            schemeName=sql.Identifier(self._schemeName),
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [sql.Identifier(REGIONS_FK_COUNTRY), sql.Identifier(REGIONS_NAME)]
            ),
        )

    async def add(self, aconn, countryId: int, regionName: str) -> None:
        """
        Asynchronous Method to Insert a New Region to the Region Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int countryId: Country ID at its Remote Table where the Region is Located
        :param str regionName: Region Name to Insert
        :returns: None
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        regionFields = [REGIONS_FK_COUNTRY, REGIONS_NAME]
        regionValues = [countryId, regionName]

        # Check if the Region Name has already been Inserted for the Given Country
        getMultTask = asyncio.create_task(
            self.getMult(aconn, regionFields, regionValues, False)
        )
        await asyncio.gather(getMultTask)
        region = getMultTask.result()

        if region != None:
            uniqueInsertedMult(REGIONS_TABLE_NAME, regionFields, regionValues)
            return

        # Ask for the Region Fields
        console.print("Adding New Region...", style="caption")

        # Get Query to Insert the New Region
        query = self.__insertQuery()

        # Execute the Query and Print a Success Message
        await asyncio.gather(aconn.cursor().execute(query, [countryId, regionName]))
        insertedRow(regionName, self._tableName)

    async def get(
        self, aconn, field: str, value, printItems: bool = True
    ) -> list[Region] | None:
        """
        Asynchronous Method to Filter Regions from its Remote Table based on a Given Field-Value Pair

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str field: Region Field that will be Used to Compare in the Region Table
        :param value: Value to Compare
        :param bool printItems: Specifies whether to Print or not the Fetched Items. Default is ``True``
        :return: List of Fetched Regions Objects if there's at Least One Coincidence. Otherwise, ``None``
        :rtype: list if there's at Least One Coincidence. Otherwise, NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Fetch Filtered Regions
        queryTask = asyncio.gather(
            BaseTable._get(self, aconn.cursor(), field, value, REGIONS_NAME)
        )

        # Clear Terminal
        if printItems:
            clear()

        await queryTask

        # Get the Regions Objects from the Fetched Regions
        regionsList = self.__getFetchedObjects()

        # Print Filtered Regions
        if printItems:
            self.__print(regionsList)

        return None if len(regionsList) == 0 else regionsList

    async def getMult(
        self, aconn, fields: list[str], values: list, printItems: bool = True
    ) -> list[Region] | None:
        """
        Asynchronous Method to Filter Regions from its Remote Table based on Some Given Field-Value Pair

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param list fields: Region Fields that will be Used to Compare in the Region Table
        :param list values: Values to Compare
        :param bool printItems: Specifies whether to Print or not the Fetched Items. Default is ``True``
        :return: List of Fetched Regions Objects if there's at Least One Coincidence. Otherwise, ``None``
        :rtype: list if there's at Least One Coincidence. Otherwise, NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Fetch Filtered Regions
        queryTask = asyncio.gather(
            BaseTable._getMult(self, aconn.cursor(), fields, values, REGIONS_NAME)
        )

        # Clear Terminal
        if printItems:
            clear()

        await queryTask

        # Get the Regions Objects from the Fetched Regions
        regionsList = self.__getFetchedObjects()

        # Print Filtered Regions
        if printItems:
            self.__print(regionsList)

        return None if len(regionsList) == 0 else regionsList

    async def findMult(self, aconn, countryId: int, regionName: str) -> Region | None:
        """
        Asynchronous Method to Find a Region at its Remote Table based on its Name and the Country ID where it's Located

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int countryId: Country ID where the Region is Located
        :param str regionName: Region Name to Search for
        :return: Region Object if Found. Otherwise, ``None``
        :rtype: Region if Found. Otherwise, NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Region from its Remote Table
        getMultTask = asyncio.create_task(
            self.getMult(
                aconn,
                [REGIONS_FK_COUNTRY, REGIONS_NAME],
                [countryId, regionName],
                False,
            )
        )
        await asyncio.gather(getMultTask)
        region = getMultTask.result()

        # Get Region Object from the Fetched Item
        if region == None:
            return None

        return region[0]

    async def find(self, aconn, regionId: int) -> Region | None:
        """
        Asynchronous Method to Find a Region at its Remote Table based on its ID

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str regionId: Region ID to Search for
        :return: Region Object if Found. Otherwise, ``None``
        :rtype: Region if Found. Otherwise, NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Region from its Remote Table
        getTask = asyncio.create_task(
            self.get(aconn, self._tablePKName, regionId, False)
        )
        await asyncio.gather(getTask)
        region = getTask.result()

        # Get Region Object from the Fetched Item
        if region == None:
            return None

        return region[0]

    async def all(self, aconn, orderBy: str, desc: bool) -> list[Region] | None:
        """
        Method that Prints All the Regions Stored at its Remote Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str orderBy: Region Field that will be Used to Sort the Region Table
        :param bool desc: Specifies whether to Sort in Ascending Order (``False``) or in Descending Order (``True``)
        :return: List of Fetched Regions Objects if the Table isn't Empty. Otherwise, ``None``
        :rtype: list if the Table isn't Empty. Otherwise, NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Fetch All Regions
        queryTask = asyncio.gather(BaseTable._all(self, aconn.cursor(), orderBy, desc))

        # Clear Terminal
        clear()

        await queryTask

        # Get the Regions Objects from the Fetched Regions
        regionsList = self.__getFetchedObjects()

        # Print All Regions
        self.__print(regionsList)

        return None if len(regionsList) == 0 else regionsList

    async def modify(self, aconn, regionId: int, field: str, value) -> None:
        """
        Asynchronous Method to Modify a Region Field to its Remote Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int regionId: Region ID from its Remote Table
        :param str field: Region Field to Modify
        :param value: Region Field Value to be Assigned
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        await asyncio.gather(
            BaseTable._modify(self, aconn.cursor(), regionId, field, value)
        )

    async def remove(self, aconn, regionId: int) -> None:
        """
        Asynchronous Method to Remove a Region Row from its Remote Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int regionId: Region ID from its Remote Table
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        await asyncio.gather(BaseTable._remove(self, aconn.cursor(), regionId))


class CitiesTable(BaseTable):
    """
    Class that Handles the SQL Operations related to the Remote SQL Cities Table
    """

    def __init__(self):
        """
        Cities Table Remote Class Constructor
        """

        # Initialize Base Table Class
        super().__init__(CITIES_TABLE_NAME, CITIES_ID, LOCATIONS_SCHEME_NAME)

    def __getFetchedObjects(self) -> list[City]:
        """
        Method to Get a List of Fetched Cities Objects from ``self_items``

        :return: List of Fetched Cities Objects
        :rtype: list
        """

        citiesList = []

        for item in self._items:
            # Intialize City from the SQL Fetched Row
            c = City.fromFetchedItem(item)
            citiesList.append(c)

        return citiesList

    def __print(self, citiesList: list[City]) -> None:
        """
        Method that Prints the Fetched Cities from its Remote Table

        :param list citiesList: Fetched Countries Objects to Print
        :return: Nothing
        :rtype: NoneType
        """

        # Number of Cities to Print
        nRows = len(citiesList)

        # Initialize Rich Table
        table = getTable("Cities", nRows)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Region ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Warehouse ID", justify="left", max_width=WAREHOUSE_NCHAR)

        # Add Cities Rows to Rich Table
        for c in citiesList:
            table.add_row(str(c.cityId), c.name, str(c.regionId), str(c.warehouseId))

        console.print(table)

    def __insertQuery(self):
        """
        Method that Retuns a Query to Insert a New City to its Remote Table

        :return: SQL Query to Insert a New City
        :rtype: Composed
        """

        return sql.SQL(
            "INSERT INTO {schemeName}.{tableName} ({fields}) VALUES (%s, %s)"
        ).format(
            schemeName=sql.Identifier(self._schemeName),
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [sql.Identifier(CITIES_FK_REGION), sql.Identifier(CITIES_NAME)]
            ),
        )

    async def add(self, aconn, regionId: int, cityName: str) -> None:
        """
        Asynchronous Method to Insert a New City to the City Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int regionId: Region ID at its Remote Table where the City is Located
        :param str cityName: City Name to Insert
        :returns: None
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        cityFields = [CITIES_FK_REGION, CITIES_NAME]
        cityValues = [regionId, cityName]

        # Check if the City Name has already been Inserted for the Given Region
        getMultTask = asyncio.create_task(
            self.getMult(aconn, cityFields, cityValues, False)
        )
        await asyncio.gather(getMultTask)
        city = getMultTask.result()

        if city != None:
            uniqueInsertedMult(CITIES_TABLE_NAME, cityFields, cityValues)
            return

        # Ask for the City Fields
        console.print("Adding New City...", style="caption")

        # Get Query to Insert the New City
        query = self.__insertQuery()

        # Execute the Query and Print a Success Message
        await asyncio.gather(aconn.cursor().execute(query, [regionId, cityName]))
        insertedRow(cityName, self._tableName)

    async def get(
        self, aconn, field: str, value, printItems: bool = True
    ) -> list[City] | None:
        """
        Asynchronous Method to Filter Cities from its Remote Table based on a Given Field-Value Pair

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str field: City Field that will be Used to Compare in the City Table
        :param value: Value to Compare
        :param bool printItems: Specifies whether to Print or not the Fetched Items. Default is ``True``
        :return: List of Fetched Cities Objects if there's at Least One Coincidence, ``None``
        :rtype: list if there's at Least One Coincidence. Otherwise, NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Fetch Filtered Cities
        queryTask = asyncio.gather(
            BaseTable._get(self, aconn.cursor(), field, value, CITIES_NAME)
        )

        # Clear Terminal
        if printItems:
            clear()

        await queryTask

        # Get the Cities Objects from the Fetched Cities
        citiesList = self.__getFetchedObjects()

        # Print Filtered Cities
        if printItems:
            self.__print(citiesList)

        return None if len(citiesList) == 0 else citiesList

    async def getMult(
        self, aconn, fields: list[str], values: list, printItems: bool = True
    ) -> list[City] | None:
        """
        Asynchronous Method to Filter Cities from its Remote Table based on Some Given Field-Value Pair

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param list fields: City Fields that will be Used to Compare in the City Table
        :param list values: Values to Compare
        :param bool printItems: Specifies whether to Print or not the Fetched Items. Default is ``True``
        :return: List of Fetched Cities Objects if there's at Least One Coincidence, ``None``
        :rtype: list if there's at Least One Coincidence. Otherwise, NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Fetch Filtered Cities
        queryTask = asyncio.gather(
            BaseTable._getMult(self, aconn.cursor(), fields, values, CITIES_NAME)
        )

        # Clear Terminal
        if printItems:
            clear()

        await queryTask

        # Get the Cities Objects from the Fetched Cities
        citiesList = self.__getFetchedObjects()

        # Print Filtered Cities
        if printItems:
            self.__print(citiesList)

        return None if len(citiesList) == 0 else citiesList

    async def findMult(self, aconn, regionId: int, cityName: str) -> City | None:
        """
        Asynchronous Method to Find a City at its Remote Table based on its Name and the Region ID where it's Located

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int regionId: Region ID where the City is Located
        :param str cityName: City Name to Search for
        :return: City Object if Found. Otherwise, ``None``
        :rtype: City if Found. Otherwise, NoneType
        """

        # Get City from its Remote Table
        getTask = asyncio.create_task(
            self.getMult(
                aconn, [CITIES_FK_REGION, CITIES_NAME], [regionId, cityName], False
            )
        )
        await asyncio.gather(getTask)
        city = getTask.result()

        # Get City Object from the Fetched Item
        if city == None:
            return None

        return city[0]

    async def find(self, aconn, cityId: int) -> City | None:
        """
        Asynchronous Method to Find a City at its Remote Table based on its ID

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str cityId: City ID to Search for
        :return: City Object if Found. Otherwise, ``None``
        :rtype: City if Found. Otherwise, NoneType
        """

        # Get City from its Remote Table
        getTask = asyncio.create_task(self.get(aconn, self._tablePKName, cityId, False))
        await asyncio.gather(getTask)
        city = getTask.result()

        # Get City Object from the Fetched Item
        if city == None:
            return None

        return city[0]

    async def all(self, aconn, orderBy: str, desc: bool) -> list[City] | None:
        """
        Method that Prints All the Cities Stored at its Remote Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param str orderBy: City Field that will be Used to Sort the City Table
        :param bool desc: Specificies whether to Sort in Ascending Order (``False``) or in Descending Order (``True``)
        :return: List of Fetched Cities Objects if the Table isn't Empty. Otherwise, ``None``
        :rtype: list if the Table isn't Empty. Otherwise, NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Fetch All Cities
        queryTask = asyncio.gather(BaseTable._all(self, aconn.cursor(), orderBy, desc))

        # Clear Terminal
        clear()

        await queryTask

        # Get the Cities Objects from the Fetched Cities
        citiesList = self.__getFetchedObjects()

        # Print All Cities
        self.__print(citiesList)

        return None if len(citiesList) == 0 else citiesList

    async def modify(self, aconn, cityId: int, field: str, value) -> None:
        """
        Asynchronous Method to Modify a City Field to its Remote Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int cityId: City ID from its Remote Table
        :param str field: City Field to Modify
        :param value: City Field Value to be Assigned
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        await asyncio.gather(
            BaseTable._modify(self, aconn.cursor(), cityId, field, value)
        )

    async def remove(self, aconn, cityId: int) -> None:
        """
        Asynchronous Method to Remove a City Row from its Remote Table

        :param aconn: Asynchronous Pool Connection with the Remote Database
        :param int cityId: City ID from its Remote Table
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        await asyncio.gather(BaseTable._remove(self, aconn.cursor(), cityId))
