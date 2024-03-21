import sqlite3

from .constants import *


# Default Local GeoPy Database Class
class GeoPyDatabase:
    # Protected Fields
    _dbname = GEOPY_DATABASE_NAME
    _conn = None
    _c = None

    # Constructor
    def __init__(self):
        # Save Connection Data to Protected Fields
        self._conn = sqlite3.connect(self._dbname)
        self._c = self.getCursor()

        # Initialize Rows Counter Table
        self.__initTable()

    # Create GeoPy Rows Counter Table if it doesn't Exist
    def __initTable(self) -> None:
        # Create Table Query
        query = f"CREATE TABLE IF NOT EXISTS {GEOPY_ROWS_COUNTER_TABLENAME} ({GEOPY_TABLENAME} VARCHAR(50) PRIMARY KEY,{GEOPY_COUNTER} INT NOT NULL);"

        # Execute Query
        self._c.execute(query)

        # Insert Tablenames
        tableNames = [
            GEOPY_COUNTRY_NAME_TABLENAME,
            GEOPY_COUNTRY_SEARCH_TABLENAME,
            GEOPY_REGION_NAME_TABLENAME,
            GEOPY_REGION_SEARCH_TABLENAME,
            GEOPY_SUBREGION_TABLENAME,
            GEOPY_SUBREGION_SEARCH_TABLENAME,
            GEOPY_CITY_NAME_TABLENAME,
            GEOPY_CITY_SEARCH_TABLENAME,
            GEOPY_CITY_AREA_NAME_TABLENAME,
            GEOPY_CITY_AREA_SEARCH_TABLENAME,
        ]

        for t in tableNames:
            self.__addTable(t)

    # Add Table to GeoPy Rows Counter Table
    def __addTable(self, tableName: str) -> None:
        # Add Table Query
        query = f"INSERT OR IGNORE INTO {GEOPY_ROWS_COUNTER_TABLENAME} ({GEOPY_TABLENAME}, {GEOPY_COUNTER}) VALUES (?,?)"

        # Execute Query
        self._c.execute(
            query,
            (
                tableName,
                0,
            ),
        )

    # Destructor
    def __del__(self):
        # Commit Command
        self._conn.commit()

        # Close Connection
        if self._c != None:
            self._c.close()
        if self._conn != None:
            self._conn.close()

    # Get Cursor
    def getCursor(self):
        return self._conn.cursor()


# GeoPy Location Table Clas
class GeoPyTable:
    # Protected Fields
    _c = None
    _item = None

    # Constructor
    def __init__(self, database: GeoPyDatabase):
        # Get Cursor
        self._c = database.getCursor()

        # Create GeoPy Table if doesn't Exist
        self.__initGeoPyCountryNameTable()
        self.__initGeoPyCountrySearchTable()
        self.__initGeoPyRegionNameTable()
        self.__initGeoPyRegionSearchTable()

    # Print Debug
    def __debug(self, tableName: str):
        print(f"\n{tableName}")
        print(self._c.execute(f"SELECT * FROM {tableName}").fetchall())

    # Create GeoPy Country Name Table if it doesn't Exist
    def __initGeoPyCountryNameTable(self):
        # Create Table Query
        query = f"CREATE TABLE IF NOT EXISTS {GEOPY_COUNTRY_NAME_TABLENAME} ({GEOPY_NAME} VARCHAR(50) NOT NULL);"

        # Execute Query
        self._c.execute(query)

        # Debug Message
        if GEOPY_DEBUG_MODE:
            self.__debug(GEOPY_COUNTRY_NAME_TABLENAME)

    # Create GeoPy Country Search Table if it doesn't Exist
    def __initGeoPyCountrySearchTable(self):
        # Create Table Query
        query = f"CREATE TABLE IF NOT EXISTS {GEOPY_COUNTRY_SEARCH_TABLENAME} ({GEOPY_SEARCH} VARCHAR(50) NOT NULL, {GEOPY_COUNTRY_NAME_ID} BIGINT NOT NULL, FOREIGN KEY ({GEOPY_COUNTRY_NAME_ID}) REFERENCES {GEOPY_COUNTRY_NAME_TABLENAME}({GEOPY_ROWID}));"

        # Execute Query
        self._c.execute(query)

        # Debug Message
        if GEOPY_DEBUG_MODE:
            self.__debug(GEOPY_COUNTRY_SEARCH_TABLENAME)

    # Create GeoPy Region Name Table if it doesn't Exist
    def __initGeoPyRegionNameTable(self):
        # Create Table Query
        query = f"CREATE TABLE IF NOT EXISTS {GEOPY_REGION_NAME_TABLENAME} ({GEOPY_NAME} VARCHAR(50) NOT NULL, {GEOPY_COUNTRY_NAME_ID} BIGINT NOT NULL, FOREIGN KEY ({GEOPY_COUNTRY_NAME_ID}) REFERENCES {GEOPY_COUNTRY_NAME_TABLENAME}({GEOPY_ROWID}));"

        # Execute Query
        self._c.execute(query)

        # Debug Message
        if GEOPY_DEBUG_MODE:
            self.__debug(GEOPY_REGION_NAME_TABLENAME)

    # Create GeoPy Region Search Table if it doesn't Exist
    def __initGeoPyRegionSearchTable(self):
        # Create Table Query
        query = f"CREATE TABLE IF NOT EXISTS {GEOPY_REGION_SEARCH_TABLENAME} ({GEOPY_SEARCH} VARCHAR(50) NOT NULL, {GEOPY_REGION_NAME_ID} BIGINT NOT NULL, FOREIGN KEY ({GEOPY_REGION_NAME_ID}) REFERENCES {GEOPY_REGION_NAME_TABLENAME}({GEOPY_ROWID}));"

        # Execute Query
        self._c.execute(query)

        # Debug Message
        if GEOPY_DEBUG_MODE:
            self.__debug(GEOPY_REGION_SEARCH_TABLENAME)

    # Fetch One Item and return its Value
    def __fetchone(self):
        # Fetch Item
        self._item = self._item.fetchone()

        # Check Item Fetched
        if self._item == None:
            return None

        return self._item[0]

    # Get Counter from the Given Table
    def __getCounter(self, tableName: str) -> int:
        # Get Table Counter Query
        query = f"SELECT {GEOPY_COUNTER} FROM {GEOPY_ROWS_COUNTER_TABLENAME} WHERE {GEOPY_TABLENAME} = ?"

        # Execute Query
        self._item = self._c.execute(query, (tableName,))

        return self.__fetchone()

    # Set Counter to the Given Table
    def __setCounter(self, tableName: str, counter: int):
        # Set Counter Query
        query = f"UPDATE {GEOPY_ROWS_COUNTER_TABLENAME} SET {GEOPY_COUNTER} = ? WHERE {GEOPY_TABLENAME} = ?"

        # Execute Query
        self._c.execute(
            query,
            (
                counter,
                tableName,
            ),
        )

    # Get Name Query
    def __getName(self, tableName: str, nameId: int):
        # Get Location Name Query
        query = f"SELECT {GEOPY_NAME} FROM {tableName} WHERE {GEOPY_ROWID} = ?"

        # Execute Query
        self._item = self._c.execute(query, (nameId,))

        return self.__fetchone()

    # Get First Location Query
    def __getFirst(self, tableName: str):
        # Get First Location Query
        query = f"SELECT MIN({GEOPY_ROWID}) FROM {tableName}"

        # Execute Query
        self._item = self._c.execute(query)

        return self.__fetchone()

    # Remove Name ID Location Query
    def __removeNameId(self, tableName: str, rowid: int):
        # Remove Location Query
        queryRemove = f"DELETE FROM {tableName} WHERE {GEOPY_ROWID} = ?"

        # Execute Query
        self._c.execute(queryRemove, (rowid,))

        # Get Table Counter
        counter = self.__getCounter(tableName)

        # Decrease Counter
        self.__setCounter(tableName, counter - 1)

    # Remove Locations from a Given Name ID Query
    def __removeLocationsNameId(self, tableName: str, field: str, nameId: int):
        # Get Number of Locations to Remove Query
        queryNumber = f"SELECT COUNT(*) FROM {tableName} WHERE {GEOPY_ROWID} IN (SELECT {GEOPY_ROWID} FROM {tableName} WHERE {field} = ?)"
        # Remove Locations Query
        queryRemove = f"DELETE FROM {tableName} WHERE {field} = ?"

        # Execute Query to Get Number of Locations to Remove
        self._item = self._c.execute(queryNumber, (nameId,))

        # Fetch Number of Queries that were Removed
        number = self.__fetchone()
        counter = self.__getCounter(tableName)
        print(number, counter)

        # Decrease Counter
        self.__setCounter(tableName, counter - number)

        # Execute Query to Remove Locations
        self._c.execute(queryRemove, (nameId,))

    # Get Child Locations from its Parent Location to be Removed that are being Stored
    def __getChildLocationsToRemove(
        self, tableName: str, parentField: str, parentNameId: int
    ):
        # Get Child Locations to Remove Query
        queryToRemove = f"SELECT {GEOPY_ROWID} FROM {tableName} WHERE {parentField} = ?"

        # Get Number of Locations to Remove Query
        queryNumber = f"SELECT COUNT(*) FROM {tableName} WHERE {parentField} = ?"

        # Execute Query to Get the Number of Locations to Remove
        self._item = self._c.execute(queryNumber, (parentNameId,))

        # Fetch Number of Queries that were Removed
        number = self.__fetchone()
        counter = self.__getCounter(tableName)

        # Decrease Counter
        self.__setCounter(tableName, counter - number)

        # Execute Get Locations to Remove Query
        return self._c.execute(queryToRemove, (parentNameId,)).fetchall()

    # Remove Locations Searches for a Given Parent Location Name ID Query
    def __removeChildLocationsSearches(
        self,
        searchTableName: str,
        nameTableName: str,
        searchNameIdField: str,
        childNameIdField: str,
        parentRowid: int,
    ):
        # Get Child Locations Searches to Remove Query
        querySearch = f"DELETE FROM {searchTableName} WHERE {GEOPY_ROWID} IN (SELECT {GEOPY_SEARCH}.{GEOPY_ROWID} FROM {searchTableName} {GEOPY_SEARCH} INNER JOIN {nameTableName} {GEOPY_NAME} ON {GEOPY_SEARCH}.{searchNameIdField} = {GEOPY_NAME}.{GEOPY_ROWID} WHERE {childNameIdField} = ?)"

        # Get Number of Child Locations Searches to Remove Query
        queryNumber = f"SELECT COUNT(*) FROM {searchTableName} WHERE {GEOPY_ROWID} IN (SELECT {GEOPY_SEARCH}.{GEOPY_ROWID} FROM {searchTableName} {GEOPY_SEARCH} INNER JOIN {nameTableName} {GEOPY_NAME} ON {GEOPY_SEARCH}.{searchNameIdField} = {GEOPY_NAME}.{GEOPY_ROWID} WHERE {childNameIdField} = ?)"

        # Execute Query to Get the Number of Child Locations Searches to Remove
        self._item = self._c.execute(queryNumber, (parentRowid,))

        # Fetch Number of Queries that were Removed
        number = self.__fetchone()
        counter = self.__getCounter(searchTableName)

        # Decrease Counter
        self.__setCounter(searchTableName, counter - number)

        # Execute Query to Remove Child Locations Searches
        self._c.execute(querySearch, (parentRowid,))

    # Get Country Name from GeoPy Country Name Table
    def getCountryName(self, countryNameId: int) -> str | None:
        # Check Counter
        if self.__getCounter(GEOPY_COUNTRY_NAME_TABLENAME) == 0:
            return None

        # Get Country Name
        return self.__getName(GEOPY_COUNTRY_NAME_TABLENAME, countryNameId)

    # Get Country Name ID from GeoPy Country Name Table
    def getCountryNameId(self, name: str) -> int | None:
        # Check Counter
        if self.__getCounter(GEOPY_COUNTRY_NAME_TABLENAME) == 0:
            return None

        # Get Country Name ID Query from Country Name Table
        query = f"SELECT {GEOPY_ROWID} FROM {GEOPY_COUNTRY_NAME_TABLENAME} WHERE {GEOPY_NAME} = ?"

        # Execute Query
        self._item = self._c.execute(query, (name,))

        return self.__fetchone()

    # Get Country Name ID from GeoPy Country Search Table
    def getCountrySearchNameId(self, search: str) -> int | None:
        # Check Counter
        if self.__getCounter(GEOPY_COUNTRY_SEARCH_TABLENAME) == 0:
            return None

        # Get Country Name ID Query from Country Search Table
        query = f"SELECT {GEOPY_COUNTRY_NAME_ID} FROM {GEOPY_COUNTRY_SEARCH_TABLENAME} WHERE {GEOPY_SEARCH} = ?"

        # Execute Query
        self._item = self._c.execute(query, (search,))

        return self.__fetchone()

    # Get First Country Name ID from GeoPy Country Name Table
    def _getFirstCountryNameId(self) -> int | None:
        # Check Counter
        if self.__getCounter(GEOPY_COUNTRY_NAME_TABLENAME) == 0:
            return None

        # Get First Country Query
        return self.__getFirst(GEOPY_COUNTRY_NAME_TABLENAME)

    # Get First Country Search ID from GeoPy Country Search Table
    def _getFirstCountrySearchId(self) -> int | None:
        # Check Counter
        if self.__getCounter(GEOPY_COUNTRY_SEARCH_TABLENAME) == 0:
            return None

        # Get First Country Search Query
        return self.__getFirst(GEOPY_COUNTRY_SEARCH_TABLENAME)

    # Add Country Name to GeoPy Country Name Table
    def _addCountryName(self, name: str):
        # Add Country Name Query
        query = f"INSERT OR IGNORE INTO {GEOPY_COUNTRY_NAME_TABLENAME} ({GEOPY_NAME}) VALUES (?)"

        # Execute Query
        self._c.execute(query, (name,))

        counter = self.__getCounter(GEOPY_COUNTRY_NAME_TABLENAME) + 1

        # Remove First-in Country while counter is Greater than the Maximum Amount Allowed
        while counter > GEOPY_COUNTRY_MAX:
            self._removeFirstCountryName()
            counter -= 1

        # Set Country Table Counter
        self.__setCounter(GEOPY_COUNTRY_NAME_TABLENAME, counter)

    # Add Country Search Name to GeoPy Country Search Table
    def _addCountrySearch(self, search: str, countryNameId: int) -> tuple:
        # Add Country Search Name Query
        query = f"INSERT OR IGNORE INTO {GEOPY_COUNTRY_SEARCH_TABLENAME} ({GEOPY_SEARCH}, {GEOPY_COUNTRY_NAME_ID}) VALUES (?,?)"

        # Execute Query
        self._c.execute(
            query,
            (
                search,
                countryNameId,
            ),
        )

        counter = self.__getCounter(GEOPY_COUNTRY_SEARCH_TABLENAME) + 1

        # Remove First-in Country Search while counter is Greater than the Maximum Amount Allowed
        while counter > GEOPY_COUNTRY_MAX * GEOPY_LOCATION_SEARCH_MAX:
            self._removeFirstCountrySearch()
            counter -= 1

        # Set Country Search Table Counter
        self.__setCounter(GEOPY_COUNTRY_SEARCH_TABLENAME, counter)

    # Add Country
    def addCountry(self, search: str, name: str):
        # Add Country Name if it hasn't being Inserted
        self._addCountryName(name)

        # Get Country Name ID
        countryNameId = self.getCountryNameId(name)

        # Add Country Search
        self._addCountrySearch(search, countryNameId)

    # Remove First-in Country Name ID from GeoPy Country Name Table
    def _removeFirstCountryName(self):
        # Get Country Name Id
        countryNameId = self._getFirstCountryNameId()

        self._removeCountryRegionsNameId(countryNameId)
        self._removeCountrySearchNameId(countryNameId)

        # Check Counter
        if self.__getCounter(GEOPY_COUNTRY_NAME_TABLENAME) == 0:
            return

        # Remove Country Name Query
        self.__removeNameId(GEOPY_COUNTRY_NAME_TABLENAME, countryNameId)

    # Remove First-in Country Search ID from GeoPy Country Search Table
    def _removeFirstCountrySearch(self):
        # Remove Country Search Query
        self.__removeNameId(
            GEOPY_COUNTRY_SEARCH_TABLENAME, self._getFirstCountrySearchId()
        )

    # Remove Country Searches for a Given Country Name ID
    def _removeCountrySearchNameId(self, countryNameId: int):
        # Remove Country Searches Query
        self.__removeLocationsNameId(
            GEOPY_COUNTRY_SEARCH_TABLENAME, GEOPY_COUNTRY_NAME_ID, countryNameId
        )

    # Get Region Name from GeoPy Region Name Table
    def getRegionName(self, regionNameId: int) -> str | None:
        # Check Counter
        if self.__getCounter(GEOPY_REGION_NAME_TABLENAME) == 0:
            return None

        # Get Region Name
        return self.__getName(GEOPY_REGION_NAME_TABLENAME, regionNameId)

    # Get Region Name ID from GeoPy Region Name Table
    def getRegionNameId(self, countryNameId: int, name: str) -> int | None:
        # Check Counter
        if self.__getCounter(GEOPY_REGION_NAME_TABLENAME) == 0:
            return None

        # Get Region Name ID Query from Region Name Table
        query = f"SELECT {GEOPY_ROWID} FROM {GEOPY_REGION_NAME_TABLENAME} WHERE {GEOPY_NAME} = ? AND {GEOPY_COUNTRY_NAME_ID} = ?"

        # Execute Query
        self._item = self._c.execute(
            query,
            (
                name,
                countryNameId,
            ),
        )

        return self.__fetchone()

    # Get Region Name ID from GeoPy Region Search Table
    def getRegionSearchNameId(
        self, countryNameId: int, regionSearch: str
    ) -> int | None:
        # Check Counter
        if self.__getCounter(GEOPY_REGION_SEARCH_TABLENAME) == 0:
            return None

        # Get Region Name ID Query from Region Table
        query = f"SELECT {GEOPY_REGION_NAME_ID} FROM {GEOPY_REGION_NAME_TABLENAME} {GEOPY_NAME} INNER JOIN (SELECT * FROM {GEOPY_REGION_SEARCH_TABLENAME} WHERE {GEOPY_SEARCH} = ?) {GEOPY_SEARCH} ON {GEOPY_NAME}.{GEOPY_ROWID} = {GEOPY_SEARCH}.{GEOPY_REGION_NAME_ID} WHERE {GEOPY_COUNTRY_NAME_ID} = ?"

        # Execute Query
        self._item = self._c.execute(
            query,
            (
                regionSearch,
                countryNameId,
            ),
        )

        return self.__fetchone()

    # Get First Region Name ID from GeoPy Region Name Table
    def _getFirstRegionNameId(self) -> int | None:
        # Check Counter
        if self.__getCounter(GEOPY_REGION_NAME_TABLENAME) == 0:
            return None

        # Get First Region Query
        return self.__getFirst(GEOPY_REGION_NAME_TABLENAME)

    # Get First Region Search ID from GeoPy Region Search Table
    def _getFirstRegionSearchId(self) -> int | None:
        # Check Counter
        if self.__getCounter(GEOPY_REGION_SEARCH_TABLENAME) == 0:
            return None

        # Get First Region Search Query
        return self.__getFirst(GEOPY_REGION_SEARCH_TABLENAME)

    # Add Region Name to GeoPy Region Name Table
    def _addRegionName(self, countryNameId: int, regionName: str):
        # Add Region Name Query
        query = f"INSERT OR IGNORE INTO {GEOPY_REGION_NAME_TABLENAME} ({GEOPY_NAME}, {GEOPY_COUNTRY_NAME_ID}) VALUES (?,?)"

        # Execute Query
        self._c.execute(
            query,
            (
                regionName,
                countryNameId,
            ),
        )

        counter = self.__getCounter(GEOPY_REGION_NAME_TABLENAME) + 1

        # Remove First-in Region while counter is Greater than the Maximum Amount Allowed
        while counter > GEOPY_REGION_MAX:
            self._removeFirstRegionName()
            counter -= 1

        # Set Region Table Counter
        self.__setCounter(GEOPY_REGION_NAME_TABLENAME, counter)

    # Add Region Search Name to GeoPy Region Search Table
    def _addRegionSearch(self, search: str, nameId: int) -> tuple:
        # Add Region Search Name Query
        query = f"INSERT OR IGNORE INTO {GEOPY_REGION_SEARCH_TABLENAME} ({GEOPY_SEARCH}, {GEOPY_REGION_NAME_ID}) VALUES (?,?)"

        # Execute Query
        self._c.execute(
            query,
            (
                search,
                nameId,
            ),
        )

        counter = self.__getCounter(GEOPY_REGION_SEARCH_TABLENAME) + 1

        # Remove First-in Region Search while counter is Greater than the Maximum Amount Allowed
        while counter > GEOPY_REGION_MAX * GEOPY_LOCATION_SEARCH_MAX:
            self._removeFirstRegionSearch()
            counter -= 1

        # Set Country Search Table Counter
        self.__setCounter(GEOPY_REGION_SEARCH_TABLENAME, counter)

    # Add Region
    def addRegion(self, countryNameId: int, regionSearch: str, regionName: str):
        # Add Region Name if it hasn't being Inserted
        self._addRegionName(countryNameId, regionName)

        # Get Region Name ID
        regionNameId = self.getRegionNameId(countryNameId, regionName)

        # Add Region Search
        self._addRegionSearch(regionSearch, regionNameId)

    # Remove First-in Region Name ID from GeoPy Region Name Table
    def _removeFirstRegionName(self):
        # Get Region Name Id
        regionNameId = self._getFirstRegionNameId()

        # self._removeRegionSubregionsNameId(regionNameId)
        self._removeRegionSearchNameId(regionNameId)

        # Check Counter
        if self.__getCounter(GEOPY_REGION_NAME_TABLENAME) == 0:
            return

        # Remove Region Name Query
        self.__removeNameId(GEOPY_REGION_NAME_TABLENAME, regionNameId)

    # Remove First-in Region Search ID from GeoPy Region Search Table
    def _removeFirstRegionSearch(self):
        # Remove Region Search Query
        self.__removeNameId(
            GEOPY_REGION_SEARCH_TABLENAME, self._getFirstRegionSearchId()
        )

    # Remove Region Searches for a Given Region Name ID
    def _removeRegionSearchNameId(self, regionNameId: int):
        # Remove Region Searches Query
        self.__removeLocationsNameId(
            GEOPY_REGION_SEARCH_TABLENAME, GEOPY_REGION_NAME_ID, regionNameId
        )

    # Remove Regions for a Given Country Name ID
    def _removeCountryRegionsNameId(self, countryNameId: str):
        # Remove Regions Searches
        self.__removeChildLocationsSearches(
            GEOPY_REGION_SEARCH_TABLENAME,
            GEOPY_REGION_NAME_TABLENAME,
            GEOPY_REGION_NAME_ID,
            GEOPY_COUNTRY_NAME_ID,
            countryNameId,
        )

        # Remove Subregions
        # regions = self.__getChildLocationsToRemove(
        #    GEOPY_REGION_NAME_TABLENAME, GEOPY_COUNTRY_NAME_ID, countryNameId
        # )
        # self.__removeRegionSubregionsNameId(regions)

        # Remove Regions
        self.__removeLocationsNameId(
            GEOPY_REGION_NAME_TABLENAME, GEOPY_COUNTRY_NAME_ID, countryNameId
        )
