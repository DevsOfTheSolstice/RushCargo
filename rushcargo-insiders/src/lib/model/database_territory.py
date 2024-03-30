from psycopg import sql

from rich.prompt import IntPrompt

from .classes import Country, Region, City
from .constants import *
from .database import console
from .database_tables import (
    BaseTable,
    uniqueInserted,
    uniqueInsertedMult,
    noCoincidence,
    insertedRow,
    getTable,
)

from ..io.validator import clear


class CountriesTable(BaseTable):
    """
    Class that Handles the SQL Operations related to the Remote SQL Countries Table
    """

    def __init__(self, remoteCursor):
        """
        Countries Remote Table Class Constructor

        :param Cursor remoteCursor: Remote Database Connection Cursor
        """

        # Initialize Base Table Class
        super().__init__(COUNTRIES_TABLE_NAME, COUNTRIES_ID, remoteCursor)

    def __print(self) -> int:
        """
        Method that Prints the Countries Fetched from its Remote Table

        :return: Number of Fetched Countries
        :rtype: int
        """

        # Number of Countries to Print
        nRows = len(self._items)

        # Initialize Rich Table
        table = getTable("Country", nRows)

        # Add Country Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Phone Prefix", justify="left", max_width=PHONE_PREFIX_NCHAR)

        for item in self._items:
            # Intialize Country from the SQL Row Fetched
            c = Country.fromFetchedItem(item)

            # Add Country Row to Rich Table
            table.add_row(str(c.countryId), c.name, str(c.phonePrefix))

        console.print(table)

        return nRows

    def __insertQuery(self):
        """
        Method that Retuns a Query to Insert a New Country to its Remote Table

        :return: SQL Query to Insert a New Country
        :rtype: Composed
        """

        return sql.SQL("INSERT INTO {tableName} ({fields}) VALUES (%s, %s)").format(
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [sql.Identifier(COUNTRIES_NAME), sql.Identifier(COUNTRIES_PHONE_PREFIX)]
            ),
        )

    def add(self, countryName: str) -> None:
        """
        Method to Insert a New Country to the Country Table

        :param str countryName: Country Name to Insert
        :returns: None
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Check if the Country has already been Inserted
        if self.get(COUNTRIES_NAME, countryName, False):
            uniqueInserted(COUNTRIES_TABLE_NAME, COUNTRIES_NAME, countryName)
            return

        # Ask for the Country Fields
        console.print("Adding New Country...", style="caption")
        phonePrefix = IntPrompt.ask("Enter Phone Prefix")

        # Get Query to Insert the New Country
        insertQuery = self.__insertQuery()

        # Execute the Query and Print a Success Message
        try:
            self._c.execute(insertQuery, [countryName, phonePrefix])
            insertedRow(countryName, self._tableName)

        except Exception as err:
            raise err

    def get(self, field: str, value, printItems: bool = True) -> bool:
        """
        Method to Filter Countries from its Remote Table based on a Given Field-Value Pair

        :param str field: Country Field that will be Used to Compare in the Country Table
        :param value: Value to Compare
        :param bool printItems: Specifies wheter to Print or not the Fetched Items. Default is ``True``
        :return: Returns ``True`` if One or More Items were Fetched. Otherwise, ``False``
        :rtype: bool
        """

        if printItems:
            # Clear Terminal
            clear()

        if not BaseTable._get(self, field, value, COUNTRIES_NAME):
            if printItems:
                noCoincidence()
            return False

        if printItems:
            self.__print()
        return True

    def find(self, field: str, value) -> Country | None:
        """
        Method to Find a Country at its Remote Table based on its Unique Fields

        :param str field: Country Field that will be Used to Compare in the Country Table
        :param value: Unique Value to Compare
        :return: Country Object if Found. Otherwise, ``None``
        :rtype: Country if Found. Otherwise, NoneType
        """

        # Get Country from its Remote Table
        if not self.get(field, value, False):
            return None

        # Get Country Object from the Fetched Item
        return Country.fromFetchedItem(self._items[0])

    def all(self, orderBy: str, desc: bool) -> int:
        """
        Method that Prints the All the Countries Stored at its Remote Table

        :param str orderBy: Country Field that will be Used to Sort the Country Table
        :param bool desc: Specificies wheter to Sort in Ascending Order (``False``) or in Descending Order (``True``)
        :return: Number of Fetched Countries
        :rtype: int
        """

        # Fetch All Countries
        BaseTable._all(self, orderBy, desc)

        # Clear Terminal
        clear()

        # Print All Countries
        return self.__print()

    def modify(self, countryId: int, field: str, value) -> None:
        """
        Method to Modify a Country Field to its Remote Table

        :param int countryId: Country ID from its Remote Table
        :param str field: Country Field to Modify
        :param value: Country Field Value to be Assigned
        :return: Nothing
        :rtype: NoneType
        """

        BaseTable._modify(self, countryId, field, value)

    def remove(self, countryId: int) -> None:
        """
        Method to Remove a Country Row from its Remote Table

        :param int countryId: Country ID from its Remote Table
        :return: Nothing
        :rtype: NoneType
        """

        BaseTable._remove(self, countryId)


class RegionsTable(BaseTable):
    """
    Class that Handles the SQL Operations related to the Remote SQL Regions Table
    """

    def __init__(self, remoteCursor):
        """
        Regions Remote Table Class Constructor

        :param Cursor remoteCursor: Remote Database Connection Cursor
        """

        # Initialize Base Table Class
        super().__init__(REGIONS_TABLE_NAME, REGIONS_ID, remoteCursor)

    def __print(self) -> int:
        """
        Method that Prints the Regions Fetched from its Remote Table

        :return: Number of Fetched Regions
        :rtype: int
        """

        # Number of Regions to Print
        nRows = len(self._items)

        # Initialize Rich Table
        table = getTable("Region", nRows)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Country ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Air Forwarder ID", justify="left", max_width=FORWARDER_NCHAR)
        table.add_column(
            "Ocean Forwarder ID", justify="left", max_width=FORWARDER_NCHAR
        )
        table.add_column("Warehouse ID", justify="left", max_width=WAREHOUSE_NCHAR)

        for item in self._items:
            # Intialize Region from the Fetched Item
            p = Region.fromFetchedItem(item)

            # Add Row to Rich Table
            table.add_row(
                str(p.regionId),
                p.name,
                str(p.countryId),
                str(p.airForwarderId),
                str(p.oceanForwarderId),
                str(p.warehouseId),
            )

        console.print(table)

        return nRows

    def __insertQuery(self):
        """
        Method that Retuns a Query to Insert a New Region to its Remote Table

        :return: SQL Query to Insert a New Region
        :rtype: Composed
        """

        return sql.SQL("INSERT INTO {tableName} ({fields}) VALUES (%s, %s)").format(
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [sql.Identifier(REGIONS_FK_COUNTRY), sql.Identifier(REGIONS_NAME)]
            ),
        )

    def add(self, countryId: int, regionName: str) -> None:
        """
        Method to Insert a New Region to the Region Table

        :param int countryId: Country ID at its Remote Table where the Region is Located
        :param str regionName: Region Name to Insert
        :returns: None
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        regionFields = [REGIONS_FK_COUNTRY, REGIONS_NAME]
        regionValues = [countryId, regionName]

        # Check if the Region Name has already been Inserted for the Given Country
        if self.getMult(regionFields, regionValues, False):
            uniqueInsertedMult(REGIONS_TABLE_NAME, regionFields, regionValues)
            return

        # Ask for the Region Fields
        console.print("Adding New Region...", style="caption")

        # Get Query to Insert the New Region
        query = self.__insertQuery()

        # Execute the Query and Print a Success Message
        try:
            self._c.execute(query, [countryId, regionName])
            insertedRow(regionName, self._tableName)

        except Exception as err:
            raise err

    def get(self, field: str, value, printItems: bool = True) -> bool:
        """
        Method to Filter Regions from its Remote Table based on a Given Field-Value Pair

        :param str field: Region Field that will be Used to Compare in the Region Table
        :param value: Value to Compare
        :param bool printItems: Specifies wheter to Print or not the Fetched Items. Default is ``True``
        :return: Returns ``True`` if One or More Items were Fetched. Otherwise, ``False``
        :rtype: bool
        """

        if printItems:
            # Clear Terminal
            clear()

        if not BaseTable._get(self, field, value, REGIONS_NAME):
            if printItems:
                noCoincidence()
            return False

        if printItems:
            self.__print()
        return True

    def getMult(self, fields: list[str], values: list, printItems: bool = True) -> bool:
        """
        Method to Filter Regions from its Remote Table based on Some Given Field-Value Pair

        :param list fields: Region Fields that will be Used to Compare in the Region Table
        :param list values: Values to Compare
        :param bool printItems: Specifies wheter to Print or not the Fetched Items. Default is ``True``
        :return: Returns ``True`` if One or More Items were Fetched. Otherwise, ``False``
        :rtype: bool
        """

        if not BaseTable._getMult(self, fields, values):
            if printItems:
                noCoincidence()
            return False

        if printItems:
            self.__print()
        return True

    def findMult(self, countryId: int, regionName: str) -> Region | None:
        """
        Method to Find a Region at its Remote Table based on its Name and the Country ID where it's Located

        :param int countryId: Country ID where the Region is Located
        :param str regionName: Region Name to Search for
        :return: Region Object if Found. Otherwise, ``None``
        :rtype: Region if Found. Otherwise, NoneType
        """

        # Get Region from its Remote Table
        if not self.getMult(
            [REGIONS_FK_COUNTRY, REGIONS_NAME], [countryId, regionName], False
        ):
            return None

        # Get Region Object from the Fetched Item
        return Region.fromFetchedItem(self._items[0])

    def find(self, regionId: int) -> Region | None:
        """
        Method to Find a Region at its Remote Table based on its ID

        :param str regionId: Region ID to Search for
        :return: Region Object if Found. Otherwise, ``None``
        :rtype: Region if Found. Otherwise, NoneType
        """

        # Get Region from its Remote Table
        if not self.get(self._tablePKName, regionId, False):
            return None

        # Get Region Object from the Fetched Item
        return Region.fromFetchedItem(self._items[0])

    def all(self, orderBy: str, desc: bool) -> int:
        """
        Method that Prints the All the Regions Stored at its Remote Table

        :param str orderBy: Region Field that will be Used to Sort the Region Table
        :param bool desc: Specificies wheter to Sort in Ascending Order (``False``) or in Descending Order (``True``)
        :return: Number of Fetched Regions
        :rtype: int
        """

        # Fetch All Regions
        BaseTable._all(self, orderBy, desc)

        # Clear Terminal
        clear()

        # Print All Regions
        return self.__print()

    def modify(self, regionId: int, field: str, value) -> None:
        """
        Method to Modify a Region Field to its Remote Table

        :param int regionId: Region ID from its Remote Table
        :param str field: Region Field to Modify
        :param value: Region Field Value to be Assigned
        :return: Nothing
        :rtype: NoneType
        """

        BaseTable._modify(self, regionId, field, value)

    def remove(self, regionId: int) -> None:
        """
        Method to Remove a Region Row from its Remote Table

        :param int regionId: Region ID from its Remote Table
        :return: Nothing
        :rtype: NoneType
        """

        BaseTable._remove(self, regionId)


class CitiesTable(BaseTable):
    """
    Class that Handles the SQL Operations related to the Remote SQL Cities Table
    """

    def __init__(self, remoteCursor):
        """
        Cities Table Remote Class Constructor

        :param Cursor remoteCursor: Remote Database Connection Cursor
        """

        # Initialize Base Table Class
        super().__init__(CITIES_TABLE_NAME, CITIES_ID, remoteCursor)

    def __print(self) -> int:
        """
        Method that Prints the Cities Fetched from its Remote Table

        :return: Number of Fetched Cities
        :rtype: int
        """

        # Number of Cities to Print
        nRows = len(self._items)

        # Initialize Rich Table
        table = getTable("City", nRows)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Region ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Warehouse ID", justify="left", max_width=WAREHOUSE_NCHAR)

        for item in self._items:
            # Intialize City from the Fetched Item
            c = City.fromFetchedItem(item)

            # Add Row to Rich Table
            table.add_row(str(c.cityId), c.name, str(c.regionId), str(c.warehouseId))

        console.print(table)

        return nRows

    def __insertQuery(self):
        """
        Method that Retuns a Query to Insert a New City to its Remote Table

        :return: SQL Query to Insert a New City
        :rtype: Composed
        """

        return sql.SQL("INSERT INTO {tableName} ({fields}) VALUES (%s, %s)").format(
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [sql.Identifier(CITIES_FK_REGION), sql.Identifier(CITIES_NAME)]
            ),
        )

    def add(self, regionId: int, cityName: str) -> None:
        """
        Method to Insert a New City to the City Table

        :param int regionId: Region ID at its Remote Table where the City is Located
        :param str cityName: City Name to Insert
        :returns: None
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        cityFields = [CITIES_FK_REGION, CITIES_NAME]
        cityValues = [regionId, cityName]

        # Check if the City Name has already been Inserted for the Given Region
        if self.getMult(cityFields, cityValues, False):
            uniqueInsertedMult(CITIES_TABLE_NAME, cityFields, cityValues)
            return

        # Ask for the City Fields
        console.print("Adding New City...", style="caption")

        # Get Query to Insert the New City
        query = self.__insertQuery()

        # Execute the Query and Print a Success Message
        try:
            self._c.execute(query, [regionId, cityName])
            insertedRow(cityName, self._tableName)

        except Exception as err:
            raise err

    def get(self, field: str, value, printItems: bool = True) -> bool:
        """
        Method to Filter Cities from its Remote Table based on a Given Field-Value Pair

        :param str field: City Field that will be Used to Compare in the City Table
        :param value: Value to Compare
        :param bool printItems: Specifies wheter to Print or not the Fetched Items. Default is ``True``
        :return: Returns ``True`` if One or More Items were Fetched. Otherwise, ``False``
        :rtype: bool
        """

        if printItems:
            # Clear Terminal
            clear()

        if not BaseTable._get(self, field, value, CITIES_NAME):
            if printItems:
                noCoincidence()
            return False

        if printItems:
            self.__print()
        return True

    def getMult(self, fields: list[str], values: list, printItems: bool = True) -> bool:
        """
        Method to Filter Cities from its Remote Table based on Some Given Field-Value Pair

        :param list fields: City Fields that will be Used to Compare in the City Table
        :param list values: Values to Compare
        :param bool printItems: Specifies wheter to Print or not the Fetched Items. Default is ``True``
        :return: Returns ``True`` if One or More Items were Fetched. Otherwise, ``False``
        :rtype: bool
        """

        if not BaseTable._getMult(self, fields, values):
            if printItems:
                noCoincidence()
            return False

        if printItems:
            self.__print()
        return True

    def findMult(self, regionId: int, cityName: str) -> City | None:
        """
        Method to Find a City at its Remote Table based on its Name and the Region ID where it's Located

        :param int regionId: Region ID where the City is Located
        :param str cityName: City Name to Search for
        :return: City Object if Found. Otherwise, ``None``
        :rtype: City if Found. Otherwise, NoneType
        """

        # Get City from its Remote Table
        if not self.getMult([CITIES_FK_REGION, CITIES_NAME], [regionId, cityName], False):
            return None

        # Get City Object from Fetched Item
        return City.fromFetchedItem(self._items[0])

    def find(self, cityId: int) -> City | None:
        """
        Method to Find a City at its Remote Table based on its ID

        :param str cityId: City ID to Search for
        :return: City Object if Found. Otherwise, ``None``
        :rtype: City if Found. Otherwise, NoneType
        """

        # Get City from its Remote Table
        if not self.get(self._tablePKName, cityId, False):
            return None

        # Get City Object from the Fetched Item
        return City.fromFetchedItem(self._items[0])

    def all(self, orderBy: str, desc: bool) -> int:
        """
        Method that Prints the All the Cities Stored at its Remote Table

        :param str orderBy: City Field that will be Used to Sort the City Table
        :param bool desc: Specificies wheter to Sort in Ascending Order (``False``) or in Descending Order (``True``)
        :return: Number of Fetched Cities
        :rtype: int
        """

        # Fetch All Cities
        BaseTable._all(self, orderBy, desc)

        # Clear Terminal
        clear()

        # Print All Cities
        return self.__print()

    def modify(self, cityId: int, field: str, value) -> None:
        """
        Method to Modify a City Field to its Remote Table

        :param int cityId: City ID from its Remote Table
        :param str field: City Field to Modify
        :param value: City Field Value to be Assigned
        :return: Nothing
        :rtype: NoneType
        """

        BaseTable._modify(self, cityId, field, value)

    def remove(self, cityId: int) -> None:
        """
        Method to Remove a City Row from its Remote Table

        :param int cityId: City ID from its Remote Table
        :return: Nothing
        :rtype: NoneType
        """

        BaseTable._remove(self, cityId)
