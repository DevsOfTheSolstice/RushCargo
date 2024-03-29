import sqlite3

from .constants import *


def getLocationNameIdColumn(locationTypeName: str) -> str:
    """
    Function to Get Location Name ID Column at Local Database

    :param str locationTypeName: Location Type Name
    """

    return f"{locationTypeName}_{NOMINATIM_NAME_ID}"


def getNameTableName(locationTypeName: str) -> str:
    """
    Function to Get Location Table Name at Local Database

    :param str locationTypeName: Location Type Name
    """

    return f"{locationTypeName}_{NOMINATIM_NAME}"


def getSearchTableName(locationTypeName: str) -> str:
    """
    Function to Get Location Searches Table Name at Local Database

    :param str locationTypeName: Location Type Name
    """

    return f"{locationTypeName}_{NOMINATIM_SEARCH}"


class NominatimDatabase:
    """
    Local Nominatim GeoPy Database Class
    """

    # Database Connection
    __dbname = NOMINATIM_DATABASE_NAME
    __conn = None
    __c = None

    def __init__(self):
        """
        Nominatim GeoPy Database Class Constructor
        """

        # Store Database Connection
        self.__conn = sqlite3.connect(self.__dbname)
        self.__c = self.getCursor()

        # Initialize Rows Counter Table
        self.__initTable()

    def __initTable(self) -> None:
        """
        Method to Crate Nominatim GeoPy Rows Counter Table if It doesn't Exist

        :return: Nothing
        :rtype: NoneType
        """

        # Query to Create the Rows Counter Table in the Local Database
        query = f"CREATE TABLE IF NOT EXISTS {NOMINATIM_ROWS_COUNTER_TABLENAME} ({NOMINATIM_TABLENAME} VARCHAR(50) PRIMARY KEY,{NOMINATIM_COUNTER} INT NOT NULL);"

        # Execute the Query
        self.__c.execute(query)

        # Insert Table Names to Rows Counter Table
        self.__addTable(NOMINATIM_ROOT_TABLENAME)

        for t in NOMINATIM_CHILD_TABLENAMES:
            self.__addTable(t)

    def __addTable(self, locationTypeName: str) -> None:
        """
        Method to Add Row that Represents a Location Type Table to Nominatim Geopy Rows Counter Table

        :param str locationTypeName: Location Type Table Name
        :return: Nothing
        :rtype: NoneType
        """

        # Query to Add a Given Table to the Local Database
        query = f"INSERT OR IGNORE INTO {NOMINATIM_ROWS_COUNTER_TABLENAME} ({NOMINATIM_TABLENAME}, {NOMINATIM_COUNTER}) VALUES (?,?)"

        # Execute Queries
        self.__c.executemany(
            query,
            [
                (
                    getNameTableName(locationTypeName),
                    0,
                ),
                (
                    getSearchTableName(locationTypeName),
                    0,
                ),
            ],
        )

    def __del__(self):
        """
        Nominatim GeoPy Database Class Destructor
        """

        # Commit Command
        self.__conn.commit()

        # Close Connection
        if self.__c != None:
            self.__c.close()

        if self.__conn != None:
            self.__conn.close()

    # Get Cursor
    def getCursor(self):
        """
        Method to Get Remote Database Connection Cursor

        :return: Remote Database Connection Cursor
        :rtype: Cursor[TupleRow]
        """

        return self.__conn.cursor()


class NominatimTables:
    """
    Nominatim GeoPy Location Tables Class
    """

    # Database Connection
    __c = None

    # Protected Fields
    _item = None

    def __init__(self, cursor):
        """
        Nominatim GeoPy Location Tables Class Constructor

        :param Cursor cursor: Local Database Connection Cursor
        """

        # Store Dtabase Connection Cursor
        self.__c = cursor

        # Create Nominatim GeoPy Root Table if It doesn't Exist
        parentTableName = NOMINATIM_ROOT_TABLENAME
        self.__initGeoPyRootTable(parentTableName)

        # Create Nominatim GeoPy Child Tables if They don't Exist
        for t in NOMINATIM_CHILD_TABLENAMES:
            self.__initGeoPyChildTable(t, parentTableName)
            parentTableName = t

    def __initGeoPyRootTable(self, locationTypeName: str) -> None:
        """
        Method to Create Nominatim Geopy Root Name and/or Search Table if It doesn't Exist

        :param str locationTypeName: Location Type Name
        :return: Nothing
        :rtype: NoneType
        """

        # Get Table Names and Columns Name
        locationTypeNameId = getLocationNameIdColumn(locationTypeName)
        nameTableName = getNameTableName(locationTypeName)
        searchTableName = getSearchTableName(locationTypeName)

        # Query to Create Root Location Name Table
        queryName = f"CREATE TABLE IF NOT EXISTS {nameTableName} ({NOMINATIM_NAME} VARCHAR(50) NOT NULL)"

        # Query to Create Root Location Search Table
        querySearch = f"CREATE TABLE IF NOT EXISTS {searchTableName} ({NOMINATIM_SEARCH} VARCHAR(50) NOT NULL, {locationTypeNameId} BIGINT NOT NULL, FOREIGN KEY ({locationTypeNameId}) REFERENCES {nameTableName}({NOMINATIM_ROWID}))"

        # Execute the Query to Create Root Location Name Table and Root Location Search Table
        self.__c.execute(queryName)
        self.__c.execute(querySearch)

        # Print Debug Message
        if NOMINATIM_DEBUG_MODE:
            self.__debug(locationTypeName)

    def __initGeoPyChildTable(
        self, locationTypeName: str, parentLocationTypeName: str
    ) -> None:
        """
        Method to Create Nominatim Geopy Child Name and/or Search Table if It doesn't Exist

        :param str locationTypeName: Location Type Name
        :param str parentLocationTypeName: Parent Location Type Name for the Given Location
        :return: Nothing
        :rtype: NoneType
        """

        # Get Table Names and Columns Name
        locationNameId = getLocationNameIdColumn(locationTypeName)
        parentLocationTypeNameId = getLocationNameIdColumn(parentLocationTypeName)
        nameTableName = getNameTableName(locationTypeName)
        parentNameTableName = getNameTableName(parentLocationTypeName)
        searchTableName = getSearchTableName(locationTypeName)

        # query to Create Child Location Name Table
        queryName = f"CREATE TABLE IF NOT EXISTS {nameTableName} ({NOMINATIM_NAME} VARCHAR(50) NOT NULL, {parentLocationTypeNameId} BIGINT NOT NULL, FOREIGN KEY ({parentLocationTypeNameId}) REFERENCES {parentNameTableName}({NOMINATIM_ROWID}));"

        # Query to Create Location Search Table
        querySearch = f"CREATE TABLE IF NOT EXISTS {searchTableName} ({NOMINATIM_SEARCH} VARCHAR(50) NOT NULL, {locationNameId} BIGINT NOT NULL, FOREIGN KEY ({locationNameId}) REFERENCES {nameTableName}({NOMINATIM_ROWID}));"

        # Execute the Query to Create Child Location Name Table and Child Location Search Table
        self.__c.execute(queryName)
        self.__c.execute(querySearch)

        # Print Debug Message
        if NOMINATIM_DEBUG_MODE:
            self.__debug(locationTypeName)

    def __debug(self, locationTypeName: str) -> None:
        """
        Method that Prints a Debug Message to Check if the Nominatim Tables Auto-Insertion and Auto-Deletion Functions Work Fine

        :param str locationTypeName: Location Type Name
        :return: Nothing
        :rtype: NoneType
        """

        # List of Location Name Table and Location Search Table
        tables = [
            getNameTableName(locationTypeName),
            getSearchTableName(locationTypeName),
        ]

        # Print Location Name and Search Table Rows
        for t in tables:
            print(f"\n{t}")
            print(self.__c.execute(f"SELECT * FROM {t}").fetchall())

    def __fetchone(self):
        """
        Method to Fetch One Item from ``self._item`` and Return its Value. If there is nNo Item to Fetch, returns ``None``

        :return: First Fetch Item (If Found). Otherwise, ``None``
        :rtype: Any, if the First Item was Fetched. Otherwise, NoneType
        """

        # Fetch Item
        self._item = self._item.fetchone()

        # Check Fetched Item
        if self._item == None:
            return None

        return self._item[0]

    def __getCounter(self, tableName: str) -> int:
        """
        Method to Get the Counter of a Given Table at Rows Counter Table

        :param str tableName: Table Name that's being Checked
        :return: Table Name Rows Counter
        :rtype: int
        """

        # Query to Get Table Counter at Rows Counter Table
        query = f"SELECT {NOMINATIM_COUNTER} FROM {NOMINATIM_ROWS_COUNTER_TABLENAME} WHERE {NOMINATIM_TABLENAME} = ?"

        # Execute the Query
        self._item = self.__c.execute(query, (tableName,))

        return self.__fetchone()

    def __setCounter(self, tableName: str, counter: int):
        """
        Method to Set the Counter of a Given Table at Rows Counter Table

        :param str tableName: Table Name that's being Checked
        :param int counter: Table Name Rows Counter
        """

        # Query to Set Table Counter at Rows Counter Table
        query = f"UPDATE {NOMINATIM_ROWS_COUNTER_TABLENAME} SET {NOMINATIM_COUNTER} = ? WHERE {NOMINATIM_TABLENAME} = ?"

        # Execute the Query
        self.__c.execute(
            query,
            (
                counter,
                tableName,
            ),
        )

    def __getName(self, locationTypeName: str, nameId: int) -> str | None:
        """
        Method that Gets the Location Name at a Given Location Name Table through its ID

        :param str locationTypeName: Location Type Name that is being Searched
        :param int nameId: Location Name ID that is being Searched
        :return: Location Name Fetched if it was Found. Otherwise, ``None``
        :rtype: str if the Location Name was Found. Otherwise, NoneType
        """

        nameTableName = getNameTableName(locationTypeName)

        # Check Counter
        if self.__getCounter(nameTableName) == 0:
            return None

        # Query to Get the Location Name at a Given Location Name Table
        query = (
            f"SELECT {NOMINATIM_NAME} FROM {nameTableName} WHERE {NOMINATIM_ROWID} = ?"
        )

        # Execute the Query
        self._item = self.__c.execute(query, (nameId,))

        return self.__fetchone()

    def __getRootNameId(self, locationTypeName: str, name: str) -> int | None:
        """
        Method that Gets the Root Location Name ID at its Location Name Table through its ID

        :param str locationTypeName: Location Type Name that is being Searched
        :param str name: Location Name that is being Searched
        :return: Root Location Name ID Fetched if it was Found. Otherwise, ``None``
        :rtype: str if the Root Location Name ID was Found. Otherwise, NoneType
        """

        nameTableName = getNameTableName(locationTypeName)

        # Check Counter
        if self.__getCounter(nameTableName) == 0:
            return None

        # Query to Get Root Location Name ID from its Location Name Table
        query = (
            f"SELECT {NOMINATIM_ROWID} FROM {nameTableName} WHERE {NOMINATIM_NAME} = ?"
        )

        # Execute the Query
        self._item = self.__c.execute(query, (name,))

        return self.__fetchone()

    def __getChildNameId(
        self,
        locationTypeName: str,
        parentLocationName: str,
        name: str,
        parentRowid: int,
    ) -> int | None:
        """
        Method that Gets the Child Location Name ID at a Given Location Name Table through its Parent ID

        :param str locationTypeName: Location Type Name that is being Searched
        :param str parentLocationName: Parent Location Name of the One that is being Searched
        :param str name: Location Name that is being Searched
        :param int parentRowid: Parent Location SQLite rowid at its Location name Table of the One that is being Searched
        :return: Child Location Name ID Fetched if it was Found. Otherwise, ``None``
        :rtype: str if the Child Location Name ID was Found. Otherwise, NoneType
        """

        nameTableName = getNameTableName(locationTypeName)
        parentLocationNameId = getLocationNameIdColumn(parentLocationName)

        # Check Counter
        if self.__getCounter(nameTableName) == 0:
            return None

        # Query to Get the Child Location Name ID from its Location Name Table
        query = f"SELECT {NOMINATIM_ROWID} FROM {nameTableName} WHERE {NOMINATIM_NAME} = ? AND {parentLocationNameId} = ?"

        # Execute the Query
        self._item = self.__c.execute(
            query,
            (
                name,
                parentRowid,
            ),
        )

        return self.__fetchone()

    def __getRootSearchNameId(self, locationTypeName: str, search: str) -> int | None:
        """
        Method that Gets the Root Location Name ID at its Location Search Table

        :param str locationTypeName: Location Type Name that is being Searched
        :param str search: Search that is being Processed
        :return: Root Location Name ID Fetched if it was Found. Otherwise, ``None``
        :rtype: int if the Root Location Name ID was Found. Otherwise, NoneType
        """

        searchTableName = getSearchTableName(locationTypeName)
        locationNameId = getLocationNameIdColumn(locationTypeName)

        # Check Counter
        if self.__getCounter(searchTableName) == 0:
            return None

        # Query to Get the Root Location Name ID from its Location Search Table
        query = f"SELECT {locationNameId} FROM {searchTableName} WHERE {NOMINATIM_SEARCH} = ?"

        # Execute the Query
        self._item = self.__c.execute(query, (search,))

        return self.__fetchone()

    def __getChildSearchNameId(
        self,
        locationTypeName: str,
        parentLocationName: str,
        search: str,
        parentRowid: int,
    ) -> int | None:
        """
        Method that Gets the Child Location Name ID at its Location Search Table

        :param str locationTypeName: Location Type Name that is being Searched
        :param str parentLocationName: Parent Location Name of the One that is being Searched
        :param str search: Search that is being Processed
        :param int parentRowid: Parent Location SQLite rowid at its Location Name Table of the One that is being Searched
        :return: Child Location Name ID Fetched if it was Found. Otherwise, ``None``
        :rtype: int if the Child Location Name ID was Found. Otherwise, NoneType
        """

        searchTableName = getSearchTableName(locationTypeName)
        nameTableName = getNameTableName(locationTypeName)
        locationNameId = getLocationNameIdColumn(locationTypeName)
        parentLocationNameId = getLocationNameIdColumn(parentLocationName)

        # Check Counter
        if self.__getCounter(searchTableName) == 0:
            return None

        # Query to Get the Child Location Name ID Query from its Location Search Table
        query = f"SELECT {locationNameId} FROM {nameTableName} {NOMINATIM_NAME} INNER JOIN (SELECT * FROM {searchTableName} WHERE {NOMINATIM_SEARCH} = ?) {NOMINATIM_SEARCH} ON {NOMINATIM_NAME}.{NOMINATIM_ROWID} = {NOMINATIM_SEARCH}.{locationNameId} WHERE {parentLocationNameId} = ?"

        # Execute the Query
        self._item = self.__c.execute(
            query,
            (
                search,
                parentRowid,
            ),
        )

        return self.__fetchone()

    def __getFirst(self, tableName: str) -> int:
        """
        Method to Get the First rowid (in being Inserted) from a Given Table

        :param str tableName: Table Name that is being Checked
        :return: First rowid at the Given Table
        :rtype: int
        """

        # Check Counter
        if self.__getCounter(tableName) == 0:
            return None

        # Query to Get the Minimum rowid from a Given Table
        query = f"SELECT MIN({NOMINATIM_ROWID}) FROM {tableName}"

        # Execute the Query
        self._item = self.__c.execute(query)

        return self.__fetchone()

    def __removeNameId(self, tableName: str, rowid: int) -> None:
        """
        Method to Remove a Location from a Given Location Name Table by its rowid

        :param str tableName: Table Name that is being Checked
        :param int rowid: Location rowid to Remove
        :return: Nothing
        :rtype: NoneType
        """

        # Query to Remove a Location from a Given Location Name Table
        queryRemove = f"DELETE FROM {tableName} WHERE {NOMINATIM_ROWID} = ?"

        # Execute the Query
        self.__c.execute(queryRemove, (rowid,))

        # Decrease the Counter
        counter = self.__getCounter(tableName)
        self.__setCounter(tableName, counter - 1)

    def __removeLocationsNameId(
        self, tableName: str, fieldName: str, nameId: int
    ) -> None:
        """
        Method to Remove Locations from a Given Table by the Location Name ID that is Referencing

        :param str tableName: Table Name that is being Checked
        :param str fieldName: Field Name of the Column that Stores the Location Name ID of its Parent Location
        :param int nameId: Location Name ID References to Remove at the Given Table
        :return: Nothing
        :rtype: NoneType
        """

        fieldLocationNameId = getLocationNameIdColumn(fieldName)

        # Query to Get the Number of Locations to Remove
        queryNumber = f"SELECT COUNT(*) FROM {tableName} WHERE {NOMINATIM_ROWID} IN (SELECT {NOMINATIM_ROWID} FROM {tableName} WHERE {fieldLocationNameId} = ?)"

        # Query to Remove the Locations by the Location Name ID that is Referencing
        queryRemove = f"DELETE FROM {tableName} WHERE {fieldLocationNameId} = ?"

        # Execute the Query to Get Number of Locations to Remove
        self._item = self.__c.execute(queryNumber, (nameId,))

        # Fetch the Number of Queries that were Removed
        number = self.__fetchone()
        counter = self.__getCounter(tableName)

        # Execute the Query to Remove Locations
        self.__c.execute(queryRemove, (nameId,))

        # Decrease the Counter
        self.__setCounter(tableName, counter - number)

    def __getChildLocationsToRemove(
        self, locationTypeName: str, parentLocationName: str, parentRowid: int
    ) -> list[tuple[int]]:
        """
        Method to Get the Child Locations to Remove from a Given Table by the Parent Location Name ID that is Referencing

        :param str locationTypeName: Location Type Name that is being Checked
        :param str parentTableName: Parent Location Name Table that is being Referenced by its Child Table
        :param int parentId: Parent Location rowid to Remove at the Given Table
        :return: Tuple List of the Locations rowid to Remove
        :rtype: list[tuple[int]]
        """

        nameTableName = getNameTableName(locationTypeName)
        parentLocationNameId = getLocationNameIdColumn(parentLocationName)

        # Query to Get the Child Locations to Remove
        queryToRemove = f"SELECT {NOMINATIM_ROWID} FROM {nameTableName} WHERE {parentLocationNameId} = ?"

        # Query to Get the Number of Childs Locations to Remove
        queryNumber = f"SELECT COUNT(*) FROM {nameTableName} WHERE {NOMINATIM_ROWID} IN (SELECT {NOMINATIM_ROWID} FROM {nameTableName} WHERE {parentLocationNameId} = ?)"

        # Execute the Query to Get the Number of Locations to Remove
        self._item = self.__c.execute(queryNumber, (parentRowid,))

        # Fetch the Number of Queries that were Removed
        number = self.__fetchone()
        counter = self.__getCounter(nameTableName)

        # Decrease the Counter
        self.__setCounter(nameTableName, counter - number)

        # Execute the Query to Get the Child Locations to Remove
        return self.__c.execute(queryToRemove, (parentRowid,)).fetchall()

    # Remove Locations Searches for a Given Parent Location Name ID Query
    def __removeChildLocationsSearches(
        self,
        locationTypeName: str,
        parentLocationName: str,
        parentRowid: int,
    ) -> None:
        """
        Method to Remove the Child Locations from its Location Search Table by the Parent Location Name ID that is Referencing

        :param str locationTypeName: Location Type Name that is being Checked
        :param str parentTableName: Parent Location Name Table that is being Referenced by its Child Tables
        :param int parentId: Parent Location rowid to Remove at the Given Location Search Table
        :return: Nothing
        :rtype: NoneType
        """

        searchTableName = getSearchTableName(locationTypeName)
        nameTableName = getNameTableName(locationTypeName)
        locationNameId = getLocationNameIdColumn(locationTypeName)
        parentLocationNameId = getLocationNameIdColumn(parentLocationName)

        # Query to Get the Locations Searches to Remove
        querySearch = f"DELETE FROM {searchTableName} WHERE {NOMINATIM_ROWID} IN (SELECT {NOMINATIM_SEARCH}.{NOMINATIM_ROWID} FROM {searchTableName} {NOMINATIM_SEARCH} INNER JOIN {nameTableName} {NOMINATIM_NAME} ON {NOMINATIM_SEARCH}.{locationNameId} = {NOMINATIM_NAME}.{NOMINATIM_ROWID} WHERE {parentLocationNameId} = ?)"

        # Query to Get the Number of Locations Searches to Remove
        queryNumber = f"SELECT COUNT(*) FROM {searchTableName} WHERE {NOMINATIM_ROWID} IN (SELECT {NOMINATIM_SEARCH}.{NOMINATIM_ROWID} FROM {searchTableName} {NOMINATIM_SEARCH} INNER JOIN {nameTableName} {NOMINATIM_NAME} ON {NOMINATIM_SEARCH}.{locationNameId} = {NOMINATIM_NAME}.{NOMINATIM_ROWID} WHERE {parentLocationNameId} = ?)"

        # Execute the Query to Get the Number of Child Locations Searches to Remove
        self._item = self.__c.execute(queryNumber, (parentRowid,))

        # Fetch the Number of Queries that were Removed
        number = self.__fetchone()
        counter = self.__getCounter(searchTableName)

        # Execute the Query to Remove Child Locations Searches
        self.__c.execute(querySearch, (parentRowid,))

        # Decrease the Counter
        self.__setCounter(searchTableName, counter - number)

    def getCountryName(self, countryNameId: int) -> str | None:
        """
        Method to Get a Country Name from its Location Name Table by its Name ID

        :param int countryNameId: Country Name ID Used to Uniquely Identify the Country Name
        :return: Country Name if it was Found. Otherwise, ``None``
        :rtype: str if the Country was Found. Otherwise, NoneType
        """

        return self.__getName(NOMINATIM_COUNTRY_TABLENAME, countryNameId)

    def getCountryNameId(self, name: str) -> int | None:
        """
        Method to Get a Country Name ID from its Location Name Table by its Name

        :param str name: Country Name Used to Uniquely Identify the Country
        :return: Country Name ID if it was Found. Otherwise, ``None``
        :rtype: int if the Country was Found. Otherwise, NoneType
        """

        return self.__getRootNameId(NOMINATIM_COUNTRY_TABLENAME, name)

    def getCountrySearchNameId(self, search: str) -> int | None:
        """
        Method to Get a Country Name ID from its Location Search Table by a Given Search

        :param str search: Country Search
        :return: Country Name ID if it was Found. Otherwise, ``None``
        :rtype: int if the Country was Found. Otherwise, NoneType
        """

        return self.__getRootSearchNameId(NOMINATIM_COUNTRY_TABLENAME, search)

    def _getFirstCountryNameId(self) -> int | None:
        """
        Method to Get a the First Country Name ID (in being Inserted) from its Location Name Table

        :return: Country Name ID if it was Found. Otherwise, ``None``
        :rtype: int if the Country was Found. Otherwise, NoneType
        """

        return self.__getFirst(getNameTableName(NOMINATIM_COUNTRY_TABLENAME))

    def _getFirstCountrySearchId(self) -> int | None:
        """
        Method to Get a the First Country Search ID (in being Inserted) from its Location Search Table

        :return: Country Search ID if it was Found. Otherwise, ``None``
        :rtype: int if the Country was Found. Otherwise, NoneType
        """

        return self.__getFirst(getSearchTableName(NOMINATIM_COUNTRY_TABLENAME))

    def _addCountryName(self, name: str) -> None:
        """
        Method to Insert a Country Name to its Location Name Table

        :param str name: Country Name to Insert
        :return: Nothing
        :rtype: NoneType
        """

        nameTableName = getNameTableName(NOMINATIM_COUNTRY_TABLENAME)

        # Query to Add a Country Name to its Location Name Table
        query = f"INSERT OR IGNORE INTO {nameTableName} ({NOMINATIM_NAME}) VALUES (?)"

        # Execute the Query
        self.__c.execute(query, (name,))

        counter = self.__getCounter(nameTableName) + 1

        # Remove First-in Country while counter is Greater than the Maximum Amount Allowed
        while counter > NOMINATIM_COUNTRY_MAX:
            self._removeFirstCountryName()
            counter -= 1

        # Set Country Table Counter
        self.__setCounter(nameTableName, counter)

    def _addCountrySearch(self, search: str, nameId: int) -> None:
        """
        Method to Insert a Country Search to its Location Search Table that is Linked to a Given Country Name

        :param str search: Country Search to Insert
        :param int nameId: Country ID that is Linked to the Given Search
        :return: Nothing
        :rtype: NoneType
        """

        searchTableName = getSearchTableName(NOMINATIM_COUNTRY_TABLENAME)
        locationNameId = getLocationNameIdColumn(NOMINATIM_COUNTRY_TABLENAME)

        # Query to Add a Country Search to its Location Search Table
        query = f"INSERT OR IGNORE INTO {searchTableName} ({NOMINATIM_SEARCH}, {locationNameId}) VALUES (?,?)"

        # Execute the Query
        self.__c.execute(
            query,
            (
                search,
                nameId,
            ),
        )

        counter = self.__getCounter(searchTableName) + 1

        # Remove First-in Country Search while counter is Greater than the Maximum Amount Allowed
        while counter > NOMINATIM_COUNTRY_MAX * NOMINATIM_LOCATION_SEARCH_MAX:
            self._removeFirstCountrySearch()
            counter -= 1

        # Set Country Search Table Counter
        self.__setCounter(searchTableName, counter)

    def addCountry(self, search: str, name: str) -> None:
        """
        Method to Insert a Country to its Location Search and Name Table

        :param str search: Country Search to Insert
        :param int name: Country Name to Insert
        :return: Nothing
        :rtype: NoneType
        """

        # Add Country Name if it hasn't being Inserted
        self._addCountryName(name)

        # Add Country Search
        countryNameId = self.getCountryNameId(name)
        self._addCountrySearch(search, countryNameId)

    def _removeFirstCountryName(self) -> None:
        """
        Method to Remove the First-in Country Name from its Location Name Table

        :return: Nothing
        :rtype: NoneType
        """

        nameTableName = getNameTableName(NOMINATIM_COUNTRY_TABLENAME)

        countryNameId = self._getFirstCountryNameId()

        # Remove Country's Provinces and Linked Searches
        self._removeCountryProvincesNameId(countryNameId)
        self._removeCountrySearchNameId(countryNameId)

        # Check Counter
        if self.__getCounter(nameTableName) == 0:
            return

        # Remove Country Name
        self.__removeNameId(nameTableName, countryNameId)

    def _removeFirstCountrySearch(self) -> None:
        """
        Method to Remove the First-in Country Search from its Location Search Table

        :return: Nothing
        :rtype: NoneType
        """

        self.__removeNameId(
            getSearchTableName(NOMINATIM_COUNTRY_TABLENAME),
            self._getFirstCountrySearchId(),
        )

    def _removeCountrySearchNameId(self, countryNameId: int) -> None:
        """
        Method to Remove the Country Searches from its Location Search Table

        :param int countryNameId: Country ID Linked to the Searches to Remove
        :return: Nothing
        :rtype: NoneType
        """

        self.__removeLocationsNameId(
            getSearchTableName(NOMINATIM_COUNTRY_TABLENAME),
            NOMINATIM_COUNTRY_TABLENAME,
            countryNameId,
        )

    def getProvinceName(self, provinceNameId: int) -> str | None:
        """
        Method to Get a Province Name from its Location Name Table by its Name ID

        :param int provinceNameId: Province Name ID Used to Uniquely Identify the Province Name
        :return: Province Name if it was Found. Otherwise, ``None``
        :rtype: str if the Province was Found. Otherwise, NoneType
        """

        return self.__getName(NOMINATIM_PROVINCE_TABLENAME, provinceNameId)

    def getProvinceNameId(self, countryNameId: int, name: str) -> int | None:
        """
        Method to Get a Province Name ID from its Location Name Table by its Name and the Country where it's Located

        :param int countryNameId: Country Name ID where the Province is Located
        :param str name: Province Name Used to Uniquely Identify the Province at the Given Country
        :return: Province Name ID if it was Found. Otherwise, ``None``
        :rtype: int if the Province was Found. Otherwise, NoneType
        """

        return self.__getChildNameId(
            NOMINATIM_PROVINCE_TABLENAME,
            NOMINATIM_COUNTRY_TABLENAME,
            name,
            countryNameId,
        )

    def getProvinceSearchNameId(
        self, countryNameId: int, provinceSearch: str
    ) -> int | None:
        """
        Method to Get a Province Name ID from its Location Search Table by a Given Search

        :param int countryNameId: Country Name ID where the Province is Located
        :param str provinceSearch: Province Search
        :return: Province Name ID if it was Found. Otherwise, ``None``
        :rtype: int if the Province was Found. Otherwise, NoneType
        """

        return self.__getChildSearchNameId(
            NOMINATIM_PROVINCE_TABLENAME,
            NOMINATIM_COUNTRY_TABLENAME,
            provinceSearch,
            countryNameId,
        )

    def _getFirstProvinceNameId(self) -> int | None:
        """
        Method to Get a the First Province Name ID (in being Inserted) from its Location Name Table

        :return: Province Name ID if it was Found. Otherwise, ``None``
        :rtype: int if the Province was Found. Otherwise, NoneType
        """

        return self.__getFirst(getNameTableName(NOMINATIM_PROVINCE_TABLENAME))

    def _getFirstProvinceSearchId(self) -> int | None:
        """
        Method to Get a the First Province Search ID (in being Inserted) from its Location Search Table

        :return: Province Search ID if it was Found. Otherwise, ``None``
        :rtype: int if the Province was Found. Otherwise, NoneType
        """

        return self.__getFirst(getSearchTableName(NOMINATIM_PROVINCE_TABLENAME))

    def _addProvinceName(self, countryNameId: int, provinceName: str) -> None:
        """
        Method to Insert a Province Name to its Location Name Table at a Given Country

        :param int countryNameId: Country ID at its Location Name Table where the Province is Located
        :param str provinceName: Province Name to Insert
        :return: Nothing
        :rtype: NoneType
        """

        nameTableName = getNameTableName(NOMINATIM_PROVINCE_TABLENAME)
        parentLocationNameId = getLocationNameIdColumn(NOMINATIM_COUNTRY_TABLENAME)

        # Query to Add a Province Name to its Location Name Table
        query = f"INSERT OR IGNORE INTO {nameTableName} ({NOMINATIM_NAME}, {parentLocationNameId}) VALUES (?,?)"

        # Execute the Query
        self.__c.execute(
            query,
            (
                provinceName,
                countryNameId,
            ),
        )

        counter = self.__getCounter(nameTableName) + 1

        # Remove First-in Province while counter is Greater than the Maximum Amount Allowed
        while counter > NOMINATIM_PROVINCE_MAX:
            self._removeFirstProvinceName()
            counter -= 1

        # Set Province Table Counter
        self.__setCounter(nameTableName, counter)

    def _addProvinceSearch(self, search: str, nameId: int) -> tuple:
        """
        Method to Insert a Province Search to its Location Search Table that is Linked to a Given Province Name

        :param str search: Province Search to Insert
        :param int nameId: Province ID that is Linked to the Given Search
        :return: Nothing
        :rtype: NoneType
        """

        searchTableName = getSearchTableName(NOMINATIM_PROVINCE_TABLENAME)
        searchLocationNameId = getLocationNameIdColumn(NOMINATIM_PROVINCE_TABLENAME)

        # Query to Add a Province Search to its Location Search Table
        query = f"INSERT OR IGNORE INTO {searchTableName} ({NOMINATIM_SEARCH}, {searchLocationNameId}) VALUES (?,?)"

        # Execute the Query
        self.__c.execute(
            query,
            (
                search,
                nameId,
            ),
        )

        counter = self.__getCounter(searchTableName) + 1

        # Remove First-in Province Search while counter is Greater than the Maximum Amount Allowed
        while counter > NOMINATIM_PROVINCE_MAX * NOMINATIM_LOCATION_SEARCH_MAX:
            self._removeFirstProvinceSearch()
            counter -= 1

        # Set Province Search Table Counter
        self.__setCounter(searchTableName, counter)

    def addProvince(
        self, countryNameId: int, provinceSearch: str, provinceName: str
    ) -> None:
        """
        Method to Insert a Province to its Location Search and Name Table at a Given Country

        :param int countryNameId: Country ID at its Location Name Table where the Province is Located
        :param str provinceSearch: Province Search to Insert
        :param int provinceName: Province Name to Insert
        :return: Nothing
        :rtype: NoneType
        """

        # Add Province Name if it hasn't being Inserted
        self._addProvinceName(countryNameId, provinceName)

        # Add Province Search
        provinceNameId = self.getProvinceNameId(countryNameId, provinceName)
        self._addProvinceSearch(provinceSearch, provinceNameId)

    def _removeFirstProvinceName(self) -> None:
        """
        Method to Remove the First-in Province Name from its Location Name Table

        :return: Nothing
        :rtype: NoneType
        """

        nameTableName = getNameTableName(NOMINATIM_PROVINCE_TABLENAME)

        provinceNameId = self._getFirstProvinceNameId()

        # Remove Province's Regions and Linked Searches
        self._removeProvinceRegionsNameId([provinceNameId])
        self._removeProvinceSearchNameId(provinceNameId)

        # Check Counter
        if self.__getCounter(nameTableName) == 0:
            return

        # Remove Province Name
        self.__removeNameId(nameTableName, provinceNameId)

    def _removeFirstProvinceSearch(self) -> None:
        """
        Method to Remove the First-in Province Search from its Location Search Table

        :return: Nothing
        :rtype: NoneType
        """

        self.__removeNameId(
            getSearchTableName(NOMINATIM_PROVINCE_TABLENAME),
            self._getFirstProvinceSearchId(),
        )

    def _removeProvinceSearchNameId(self, provinceNameId: int) -> None:
        """
        Method to Remove the Province Searches from its Location Search Table

        :param int provinceNameId: Province ID Linked to the Searches to Remove
        :return: Nothing
        :rtype: NoneType
        """

        self.__removeLocationsNameId(
            getSearchTableName(NOMINATIM_PROVINCE_TABLENAME),
            NOMINATIM_PROVINCE_TABLENAME,
            provinceNameId,
        )

    def _removeCountryProvincesNameId(self, countryNameId: int) -> None:
        """
        Method to Remove the Country's Provinces' Regions, Linked Searches and Names from its Tables

        :param int countryNameId: Country ID at Location Name Table where the Provinces are Located
        :return: Nothing
        :rtype: NoneType
        """

        # Remove Provinces' Regions
        provinces = self.__getChildLocationsToRemove(
            NOMINATIM_PROVINCE_TABLENAME, NOMINATIM_COUNTRY_TABLENAME, countryNameId
        )
        self._removeProvinceRegionsNameId(provinces)

        # Remove Provinces Linked Searches
        self.__removeChildLocationsSearches(
            NOMINATIM_PROVINCE_TABLENAME,
            NOMINATIM_COUNTRY_TABLENAME,
            countryNameId,
        )

        # Remove Provinces
        self.__removeLocationsNameId(
            getNameTableName(NOMINATIM_PROVINCE_TABLENAME),
            NOMINATIM_COUNTRY_TABLENAME,
            countryNameId,
        )

    def getRegionName(self, regionNameId: int) -> str | None:
        """
        Method to Get a Region Name from its Location Name Table by its Name ID

        :param int regionNameId: Region Name ID Used to Uniquely Identify the Region Name
        :return: Region Name if it was Found. Otherwise, ``None``
        :rtype: str if the Region was Found. Otherwise, NoneType
        """

        return self.__getName(NOMINATIM_REGION_TABLENAME, regionNameId)

    def getRegionNameId(self, provinceNameId: int, name: str) -> int | None:
        """
        Method to Get a Province Name ID from its Location Name Table by its Name and the Province where it's Located

        :param int provinceNameId: Province Name ID where the Region is Located
        :param str name: Region Name Used to Uniquely Identify the Region at the Given Province
        :return: Region Name ID if it was Found. Otherwise, ``None``
        :rtype: int if the Region was Found. Otherwise, NoneType
        """

        return self.__getChildNameId(
            NOMINATIM_REGION_TABLENAME,
            NOMINATIM_PROVINCE_TABLENAME,
            name,
            provinceNameId,
        )

    def getRegionSearchNameId(
        self, provinceNameId: int, regionSearch: str
    ) -> int | None:
        """
        Method to Get a Region Name ID from its Location Search Table by a Given Search

        :param int provinceNameId: Province Name ID where the Region is Located
        :param str regionSearch: Region Search
        :return: Region Name ID if it was Found. Otherwise, ``None``
        :rtype: int if the Region was Found. Otherwise, NoneType
        """

        return self.__getChildSearchNameId(
            NOMINATIM_REGION_TABLENAME,
            NOMINATIM_PROVINCE_TABLENAME,
            regionSearch,
            provinceNameId,
        )

    def _getFirstRegionNameId(self) -> int | None:
        """
        Method to Get a the First Region Name ID (in being Inserted) from its Location Name Table

        :return: Region Name ID if it was Found. Otherwise, ``None``
        :rtype: int if the Region was Found. Otherwise, NoneType
        """

        return self.__getFirst(getNameTableName(NOMINATIM_REGION_TABLENAME))

    def _getFirstRegionSearchId(self) -> int | None:
        """
        Method to Get a the First Region Search ID (in being Inserted) from its Location Search Table

        :return: Region Search ID if it was Found. Otherwise, ``None``
        :rtype: int if the Region was Found. Otherwise, NoneType
        """

        return self.__getFirst(getSearchTableName(NOMINATIM_REGION_TABLENAME))

    def _addRegionName(self, provinceNameId: int, regionName: str) -> None:
        """
        Method to Insert a Region Name to its Location Name Table at a Given Province

        :param int provinceNameId: Province ID at its Location Name Table where the Region is Located
        :param str regionName: Region Name to Insert
        :return: Nothing
        :rtype: NoneType
        """

        nameTableName = getNameTableName(NOMINATIM_REGION_TABLENAME)
        parentLocationNameId = getLocationNameIdColumn(NOMINATIM_PROVINCE_TABLENAME)

        # Query to Add a Region Name to its Location Name Table
        query = f"INSERT OR IGNORE INTO {nameTableName} ({NOMINATIM_NAME}, {parentLocationNameId}) VALUES (?,?)"

        # Execute the Query
        self.__c.execute(
            query,
            (
                regionName,
                provinceNameId,
            ),
        )

        counter = self.__getCounter(nameTableName) + 1

        # Remove First-in Region while counter is Greater than the Maximum Amount Allowed
        while counter > NOMINATIM_REGION_MAX:
            self._removeFirstRegionName()
            counter -= 1

        # Set Region Table Counter
        self.__setCounter(nameTableName, counter)

    def _addRegionSearch(self, search: str, nameId: int) -> None:
        """
        Method to Insert a Region Search to its Location Search Table that is Linked to a Given Region Name

        :param str search: Region Search to Insert
        :param int nameId: Region ID that is Linked to the Given Search
        :return: Nothing
        :rtype: NoneType
        """

        searchTableName = getSearchTableName(NOMINATIM_REGION_TABLENAME)
        searchLocationNameId = getLocationNameIdColumn(NOMINATIM_REGION_TABLENAME)

        # Query to Add a Region Search to its Location Search Table
        query = f"INSERT OR IGNORE INTO {searchTableName} ({NOMINATIM_SEARCH}, {searchLocationNameId}) VALUES (?,?)"

        # Execute the Query
        self.__c.execute(
            query,
            (
                search,
                nameId,
            ),
        )

        counter = self.__getCounter(searchTableName) + 1

        # Remove First-in Region Search while counter is Greater than the Maximum Amount Allowed
        while counter > NOMINATIM_REGION_MAX * NOMINATIM_LOCATION_SEARCH_MAX:
            self._removeFirstRegionSearch()
            counter -= 1

        # Set Region Search Table Counter
        self.__setCounter(searchTableName, counter)

    def addRegion(
        self, provinceNameId: int, regionSearch: str, regionName: str
    ) -> None:
        """
        Method to Insert a Region to its Location Search and Name Table at a Given Province

        :param int provinceNameId: Province ID at its Location Name Table where the Region is Located
        :param str regionSearch: Region Search to Insert
        :param int regionName: Region Name to Insert
        :return: Nothing
        :rtype: NoneType
        """

        # Add Region Name if it hasn't being Inserted
        self._addRegionName(provinceNameId, regionName)

        # Add Region Search
        regionNameId = self.getRegionNameId(provinceNameId, regionName)
        self._addRegionSearch(regionSearch, regionNameId)

    def _removeFirstRegionName(self) -> None:
        """
        Method to Remove the First-in Region Name from its Location Name Table

        :return: Nothing
        :rtype: NoneType
        """

        nameTableName = getNameTableName(NOMINATIM_REGION_TABLENAME)

        regionNameId = self._getFirstRegionNameId()

        # Remove Region's Cities and Linked Searches
        self._removeRegionCitiesNameId([regionNameId])
        self._removeRegionSearchNameId(regionNameId)

        # Check Counter
        if self.__getCounter(nameTableName) == 0:
            return

        # Remove Region Name
        self.__removeNameId(nameTableName, regionNameId)

    def _removeFirstRegionSearch(self) -> None:
        """
        Method to Remove the First-in Region Search from its Location Search Table

        :return: Nothing
        :rtype: NoneType
        """

        self.__removeNameId(
            getSearchTableName(NOMINATIM_REGION_TABLENAME),
            self._getFirstRegionSearchId(),
        )

    def _removeRegionSearchNameId(self, regionNameId: int) -> None:
        """
        Method to Remove the Region Searches from its Location Search Table

        :param int countryNameId: Region ID Linked to the Searches to Remove
        :return: Nothing
        :rtype: NoneType
        """

        self.__removeLocationsNameId(
            getSearchTableName(NOMINATIM_REGION_TABLENAME),
            NOMINATIM_REGION_TABLENAME,
            regionNameId,
        )

    def _removeProvinceRegionsNameId(self, provinces: list[tuple[int]]) -> None:
        """
        Method to Remove the Provinces' Regions' Cities, Linked Searches and Names from its Tables

        :param list provinces: Provinces ID at Location Name Table where the Regions are Located
        :return: Nothing
        :rtype: NoneType
        """

        for p in provinces:
            provinceNameId = p[0]

            # Remove Provinces' Cities
            regions = self.__getChildLocationsToRemove(
                NOMINATIM_REGION_TABLENAME, NOMINATIM_PROVINCE_TABLENAME, provinceNameId
            )
            self._removeRegionCitiesNameId(regions)

            # Remove Regions Linked Searches
            self.__removeChildLocationsSearches(
                NOMINATIM_REGION_TABLENAME,
                NOMINATIM_PROVINCE_TABLENAME,
                provinceNameId,
            )

            # Remove Regions
            self.__removeLocationsNameId(
                getNameTableName(NOMINATIM_REGION_TABLENAME),
                NOMINATIM_PROVINCE_TABLENAME,
                provinceNameId,
            )

    def getCityName(self, cityNameId: int) -> str | None:
        """
        Method to Get a City Name from its Location Name Table by its Name ID

        :param int countryNameId: City Name ID Used to Uniquely Identify the City Name
        :return: City Name if it was Found. Otherwise, ``None``
        :rtype: str if the City was Found. Otherwise, NoneType
        """

        return self.__getName(NOMINATIM_CITY_TABLENAME, cityNameId)

    def getCityNameId(self, regionNameId: int, name: str) -> int | None:
        """
        Method to Get a City Name ID from its Location Name Table by its Name and the Region where it's Located

        :param int regionNameId: Region Name ID where the City is Located
        :param str name: City Name Used to Uniquely Identify the City at the Given Region
        :return: City Name ID if it was Found. Otherwise, ``None``
        :rtype: int if the City was Found. Otherwise, NoneType
        """

        return self.__getChildNameId(
            NOMINATIM_CITY_TABLENAME, NOMINATIM_REGION_TABLENAME, name, regionNameId
        )

    def getCitySearchNameId(self, regionNameId: int, citySearch: str) -> int | None:
        """
        Method to Get a City Name ID from its Location Search Table by a Given Search

        :param int regionNameId: Region Name ID where the City is Located
        :param str citySearch: City Search
        :return: City Name ID if it was Found. Otherwise, ``None``
        :rtype: int if the City was Found. Otherwise, NoneType
        """

        return self.__getChildSearchNameId(
            NOMINATIM_CITY_TABLENAME,
            NOMINATIM_REGION_TABLENAME,
            citySearch,
            regionNameId,
        )

    def _getFirstCityNameId(self) -> int | None:
        """
        Method to Get a the First City Name ID (in being Inserted) from its Location Name Table

        :return: City Name ID if it was Found. Otherwise, ``None``
        :rtype: int if the City was Found. Otherwise, NoneType
        """

        return self.__getFirst(getNameTableName(NOMINATIM_CITY_TABLENAME))

    def _getFirstCitySearchId(self) -> int | None:
        """
        Method to Get a the First City Search ID (in being Inserted) from its Location Search Table

        :return: City Search ID if it was Found. Otherwise, ``None``
        :rtype: int if the City was Found. Otherwise, NoneType
        """

        return self.__getFirst(getSearchTableName(NOMINATIM_CITY_TABLENAME))

    def _addCityName(self, regionNameId: int, cityName: str) -> None:
        """
        Method to Insert a City Name to its Location Name Table at a Given Region

        :param int regionNameId: Region ID at its Location Name Table where the City is Located
        :param str cityName: City Name to Insert
        :return: Nothing
        :rtype: NoneType
        """

        nameTableName = getNameTableName(NOMINATIM_CITY_TABLENAME)
        parentLocationNameId = getLocationNameIdColumn(NOMINATIM_REGION_TABLENAME)

        # Query to Add a City Name to its Location Name Table
        query = f"INSERT OR IGNORE INTO {nameTableName} ({NOMINATIM_NAME}, {parentLocationNameId}) VALUES (?,?)"

        # Execute the Query
        self.__c.execute(
            query,
            (
                cityName,
                regionNameId,
            ),
        )

        counter = self.__getCounter(nameTableName) + 1

        # Remove First-in City while counter is Greater than the Maximum Amount Allowed
        while counter > NOMINATIM_CITY_MAX:
            self._removeFirstCityName()
            counter -= 1

        # Set City Table Counter
        self.__setCounter(nameTableName, counter)

    def _addCitySearch(self, search: str, nameId: int) -> None:
        """
        Method to Insert a City Search to its Location Search Table that is Linked to a Given City Name

        :param str search: City Search to Insert
        :param int nameId: City ID that is Linked to the Given Search
        :return: Nothing
        :rtype: NoneType
        """

        searchTableName = getSearchTableName(NOMINATIM_CITY_TABLENAME)
        searchLocationNameId = getLocationNameIdColumn(NOMINATIM_CITY_TABLENAME)

        # Query to Add a City Search to its Location Search Table
        query = f"INSERT OR IGNORE INTO {searchTableName} ({NOMINATIM_SEARCH}, {searchLocationNameId}) VALUES (?,?)"

        # Execute the Query
        self.__c.execute(
            query,
            (
                search,
                nameId,
            ),
        )

        counter = self.__getCounter(searchTableName) + 1

        # Remove First-in City Search while counter is Greater than the Maximum Amount Allowed
        while counter > NOMINATIM_CITY_MAX * NOMINATIM_LOCATION_SEARCH_MAX:
            self._removeFirstCitySearch()
            counter -= 1

        # Set City Search Table Counter
        self.__setCounter(searchTableName, counter)

    def addCity(self, regionNameId: int, citySearch: str, cityName: str) -> None:
        """
        Method to Insert a City to its Location Search and Name Table at a Given Province

        :param int regionNameId: Province ID at its Location Name Table where the City is Located
        :param str citySearch: City Search to Insert
        :param int cityName: City Name to Insert
        :return: Nothing
        :rtype: NoneType
        """

        # Add City Name if it hasn't being Inserted
        self._addCityName(regionNameId, cityName)

        # Get City Name ID
        cityNameId = self.getCityNameId(regionNameId, cityName)

        # Add City Search
        self._addCitySearch(citySearch, cityNameId)

    def _removeFirstCityName(self) -> None:
        """
        Method to Remove the First-in City Name from its Location Name Table

        :return: Nothing
        :rtype: NoneType
        """

        nameTableName = getNameTableName(NOMINATIM_CITY_TABLENAME)

        cityNameId = self._getFirstCityNameId()

        # Remove City Linked Searches
        self._removeCitySearchNameId(cityNameId)

        # Check Counter
        if self.__getCounter(nameTableName) == 0:
            return

        # Remove City Name
        self.__removeNameId(nameTableName, cityNameId)

    def _removeFirstCitySearch(self) -> None:
        """
        Method to Remove the First-in City Search from its Location Search Table

        :return: Nothing
        :rtype: NoneType
        """

        self.__removeNameId(
            getSearchTableName(NOMINATIM_CITY_TABLENAME),
            self._getFirstCitySearchId(),
        )

    def _removeCitySearchNameId(self, cityNameId: int) -> None:
        """
        Method to Remove the City Searches from its Location Search Table

        :param int cityNameId: City ID Linked to the Searches to Remove
        :return: Nothing
        :rtype: NoneType
        """

        self.__removeLocationsNameId(
            getSearchTableName(NOMINATIM_CITY_TABLENAME),
            NOMINATIM_CITY_TABLENAME,
            cityNameId,
        )

    def _removeRegionCitiesNameId(self, regions: list[tuple[str]]) -> None:
        """
        Method to Remove the Regions' Cities Linked Searches and Names from its Tables

        :param list regions: Regions ID at Location Name Table where the Cities are Located
        :return: Nothing
        :rtype: NoneType
        """


        for r in regions:
            regionNameId = r[0]

            # Remove Cities Linked Searches
            self.__removeChildLocationsSearches(
                NOMINATIM_CITY_TABLENAME,
                NOMINATIM_REGION_TABLENAME,
                regionNameId,
            )

            # Remove Cities
            self.__removeLocationsNameId(
                getNameTableName(NOMINATIM_CITY_TABLENAME),
                NOMINATIM_REGION_TABLENAME,
                regionNameId,
            )
