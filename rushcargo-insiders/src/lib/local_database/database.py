import sqlite3

from .constants import *


# Functions that Returns Some Generic Table-related Strings
def getLocationNameIdColumn(locationName: str) -> str:
    return f"{locationName}_{GEOPY_NAME_ID}"


def getNameTableName(locationName: str) -> str:
    return f"{locationName}_{GEOPY_NAME}"


def getSearchTableName(locationName: str) -> str:
    return f"{locationName}_{GEOPY_SEARCH}"


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

        # Insert Table Names to Rows Counter Table
        self.__addTable(GEOPY_ROOT_TABLENAME)

        for t in GEOPY_CHILD_TABLENAMES:
            self.__addTable(t)

    # Add Table to GeoPy Rows Counter Table
    def __addTable(self, locationName: str) -> None:
        # Add Table Query
        query = f"INSERT OR IGNORE INTO {GEOPY_ROWS_COUNTER_TABLENAME} ({GEOPY_TABLENAME}, {GEOPY_COUNTER}) VALUES (?,?)"

        # Execute Query
        self._c.executemany(
            query,
            [
                (
                    getNameTableName(locationName),
                    0,
                ),
                (
                    getSearchTableName(locationName),
                    0,
                ),
            ],
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
class GeoPyTables:
    # Protected Fields
    _c = None
    _item = None

    # Constructor
    def __init__(self, cursor):
        # Get Cursor
        self._c = cursor

        # Create GeoPy Root Table if doesn't Exist
        parentTableName = GEOPY_ROOT_TABLENAME
        self.__initGeoPyRootTable(parentTableName)

        # Create GeoPy Child Table if doesn't Exist
        for t in GEOPY_CHILD_TABLENAMES:
            self.__initGeoPyChildTable(t, parentTableName)
            parentTableName = t

    # Create GeoPy Root Name and/or Search Tables if it doesn't Exist
    def __initGeoPyRootTable(self, locationName: str) -> None:
        locationNameId = getLocationNameIdColumn(locationName)
        nameTableName = getNameTableName(locationName)
        searchTableName = getSearchTableName(locationName)

        # Create Location Name Table Query
        queryName = f"CREATE TABLE IF NOT EXISTS {nameTableName} ({GEOPY_NAME} VARCHAR(50) NOT NULL)"

        # Create Location Search Table Query
        querySearch = f"CREATE TABLE IF NOT EXISTS {searchTableName} ({GEOPY_SEARCH} VARCHAR(50) NOT NULL, {locationNameId} BIGINT NOT NULL, FOREIGN KEY ({locationNameId}) REFERENCES {nameTableName}({GEOPY_ROWID}))"

        # Execute Query to Create Location Name Table
        self._c.execute(queryName)

        # Execute Query to Create Location Search Table
        self._c.execute(querySearch)

        # Debug Message
        if GEOPY_DEBUG_MODE:
            self.__debug(locationName)

    # Create GeoPy Child Name and/or Search Table if it doesn't Exist
    def __initGeoPyChildTable(self, locationName: str, parentLocationName: str) -> None:
        locationNameId = getLocationNameIdColumn(locationName)
        parentLocationNameId = getLocationNameIdColumn(parentLocationName)
        nameTableName = getNameTableName(locationName)
        parentNameTableName = getNameTableName(parentLocationName)
        searchTableName = getSearchTableName(locationName)

        # Create Location Name Table Query
        queryName = f"CREATE TABLE IF NOT EXISTS {nameTableName} ({GEOPY_NAME} VARCHAR(50) NOT NULL, {parentLocationNameId} BIGINT NOT NULL, FOREIGN KEY ({parentLocationNameId}) REFERENCES {parentNameTableName}({GEOPY_ROWID}));"

        # Create Location Search Table Query
        querySearch = f"CREATE TABLE IF NOT EXISTS {searchTableName} ({GEOPY_SEARCH} VARCHAR(50) NOT NULL, {locationNameId} BIGINT NOT NULL, FOREIGN KEY ({locationNameId}) REFERENCES {nameTableName}({GEOPY_ROWID}));"

        # Execute Query to Create Location Name Table
        self._c.execute(queryName)

        # Execute Query to Create Location Search Table
        self._c.execute(querySearch)

        # Debug Message
        if GEOPY_DEBUG_MODE:
            self.__debug(locationName)

    # Print Debug
    def __debug(self, locationName: str) -> None:
        tables = [getNameTableName(locationName), getSearchTableName(locationName)]

        # Print Location Name and Search Tables
        for t in tables:
            print(f"\n{t}")
            print(self._c.execute(f"SELECT * FROM {t}").fetchall())

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
    def __getName(self, locationName: str, nameId: int) -> str | None:
        nameTableName = getNameTableName(locationName)

        # Check Counter
        if self.__getCounter(nameTableName) == 0:
            return None

        # Get Location Name Query
        query = f"SELECT {GEOPY_NAME} FROM {nameTableName} WHERE {GEOPY_ROWID} = ?"

        # Execute Query
        self._item = self._c.execute(query, (nameId,))

        return self.__fetchone()

    # Get Root Name ID Query
    def __getRootNameId(self, locationName: str, name: str) -> int | None:
        nameTableName = getNameTableName(locationName)

        # Check Counter
        if self.__getCounter(nameTableName) == 0:
            return None

        # Get Root Location Name ID Query from Root Location Name Table
        query = f"SELECT {GEOPY_ROWID} FROM {nameTableName} WHERE {GEOPY_NAME} = ?"

        # Execute Query
        self._item = self._c.execute(query, (name,))

        return self.__fetchone()

    # Get Child Name ID Query
    def __getChildNameId(
        self, locationName: str, parentLocationName: str, name: str, parentRowid: int
    ) -> int | None:
        nameTableName = getNameTableName(locationName)
        parentLocationNameId = getLocationNameIdColumn(parentLocationName)

        # Check Counter
        if self.__getCounter(nameTableName) == 0:
            return None

        # Get Child Location Name ID Query from Child Location Name Table
        query = f"SELECT {GEOPY_ROWID} FROM {nameTableName} WHERE {GEOPY_NAME} = ? AND {parentLocationNameId} = ?"

        # Execute Query
        self._item = self._c.execute(
            query,
            (
                name,
                parentRowid,
            ),
        )

        return self.__fetchone()

    # Get Root Search Name ID Query
    def __getRootSearchNameId(self, locationName: str, search: str) -> int | None:
        searchTableName = getSearchTableName(locationName)
        locationNameId = getLocationNameIdColumn(locationName)

        # Check Counter
        if self.__getCounter(searchTableName) == 0:
            return None

        # Get Root Location Name ID Query from Root Location Search Table
        query = (
            f"SELECT {locationNameId} FROM {searchTableName} WHERE {GEOPY_SEARCH} = ?"
        )

        # Execute Query
        self._item = self._c.execute(query, (search,))

        return self.__fetchone()

    # Get Child Search Name ID Query
    def __getChildSearchNameId(
        self, locationName: str, parentLocationName: str, search: str, parentRowid: int
    ) -> int | None:
        searchTableName = getSearchTableName(locationName)
        nameTableName = getNameTableName(locationName)
        locationNameId = getLocationNameIdColumn(locationName)
        parentLocationNameId = getLocationNameIdColumn(parentLocationName)

        # Check Counter
        if self.__getCounter(searchTableName) == 0:
            return None

        # Get Child Location Name ID Query from Child Location Search Table
        query = f"SELECT {locationNameId} FROM {nameTableName} {GEOPY_NAME} INNER JOIN (SELECT * FROM {searchTableName} WHERE {GEOPY_SEARCH} = ?) {GEOPY_SEARCH} ON {GEOPY_NAME}.{GEOPY_ROWID} = {GEOPY_SEARCH}.{locationNameId} WHERE {parentLocationNameId} = ?"

        # Execute Query
        self._item = self._c.execute(
            query,
            (
                search,
                parentRowid,
            ),
        )

        return self.__fetchone()

    # Get First Location Query
    def __getFirst(self, tableName: str) -> int:
        # Check Counter
        if self.__getCounter(tableName) == 0:
            return None

        # Get First Location Query
        query = f"SELECT MIN({GEOPY_ROWID}) FROM {tableName}"

        # Execute Query
        self._item = self._c.execute(query)

        return self.__fetchone()

    # Remove Name ID Location Query
    def __removeNameId(self, tableName: str, rowid: int) -> None:
        # Remove Location Query
        queryRemove = f"DELETE FROM {tableName} WHERE {GEOPY_ROWID} = ?"

        # Execute Query
        self._c.execute(queryRemove, (rowid,))

        # Get Table Counter
        counter = self.__getCounter(tableName)

        # Decrease Counter
        self.__setCounter(tableName, counter - 1)

    # Remove Locations from a Given Name ID Query
    def __removeLocationsNameId(
        self, tableName: str, fieldName: str, nameId: int
    ) -> None:
        fieldLocationNameId = getLocationNameIdColumn(fieldName)

        # Get Number of Locations to Remove Query
        queryNumber = f"SELECT COUNT(*) FROM {tableName} WHERE {GEOPY_ROWID} IN (SELECT {GEOPY_ROWID} FROM {tableName} WHERE {fieldLocationNameId} = ?)"

        # Remove Locations Query
        queryRemove = f"DELETE FROM {tableName} WHERE {fieldLocationNameId} = ?"

        # Execute Query to Get Number of Locations to Remove
        self._item = self._c.execute(queryNumber, (nameId,))

        # Fetch Number of Queries that were Removed
        number = self.__fetchone()
        counter = self.__getCounter(tableName)

        # Decrease Counter
        self.__setCounter(tableName, counter - number)

        # Execute Query to Remove Locations
        self._c.execute(queryRemove, (nameId,))

    # Get Locations from a Given Parent Location to be Removed that are being Stored
    def __getLocationsToRemove(
        self, locationName: str, parentLocationName: str, parentRowid: int
    ) -> list[int]:
        nameTableName = getNameTableName(locationName)
        parentLocationNameId = getLocationNameIdColumn(parentLocationName)

        # Get Locations to Remove Query
        queryToRemove = f"SELECT {GEOPY_ROWID} FROM {nameTableName} WHERE {parentLocationNameId} = ?"

        # Get Number of Locations to Remove Query
        queryNumber = f"SELECT COUNT(*) FROM {nameTableName} WHERE {GEOPY_ROWID} IN (SELECT {GEOPY_ROWID} FROM {nameTableName} WHERE {parentLocationNameId} = ?)"

        # Execute Query to Get the Number of Locations to Remove
        self._item = self._c.execute(queryNumber, (parentRowid,))

        # Fetch Number of Queries that were Removed
        number = self.__fetchone()
        counter = self.__getCounter(nameTableName)

        # Decrease Counter
        self.__setCounter(nameTableName, counter - number)

        # Execute Query to Get Locations to Remove
        return self._c.execute(queryToRemove, (parentRowid,)).fetchall()

    # Remove Locations Searches for a Given Parent Location Name ID Query
    def __removeLocationsSearches(
        self,
        locationName: str,
        parentLocationName: str,
        parentRowid: int,
    ) -> None:
        searchTableName = getSearchTableName(locationName)
        nameTableName = getNameTableName(locationName)
        locationNameId = getLocationNameIdColumn(locationName)
        parentLocationNameId = getLocationNameIdColumn(parentLocationName)

        # Get Locations Searches to Remove Query
        querySearch = f"DELETE FROM {searchTableName} WHERE {GEOPY_ROWID} IN (SELECT {GEOPY_SEARCH}.{GEOPY_ROWID} FROM {searchTableName} {GEOPY_SEARCH} INNER JOIN {nameTableName} {GEOPY_NAME} ON {GEOPY_SEARCH}.{locationNameId} = {GEOPY_NAME}.{GEOPY_ROWID} WHERE {parentLocationNameId} = ?)"

        # Get Number of Locations Searches to Remove Query
        queryNumber = f"SELECT COUNT(*) FROM {searchTableName} WHERE {GEOPY_ROWID} IN (SELECT {GEOPY_SEARCH}.{GEOPY_ROWID} FROM {searchTableName} {GEOPY_SEARCH} INNER JOIN {nameTableName} {GEOPY_NAME} ON {GEOPY_SEARCH}.{locationNameId} = {GEOPY_NAME}.{GEOPY_ROWID} WHERE {parentLocationNameId} = ?)"

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
        return self.__getName(GEOPY_COUNTRY_TABLENAME, countryNameId)

    # Get Country Name ID from GeoPy Country Name Table
    def getCountryNameId(self, name: str) -> int | None:
        return self.__getRootNameId(GEOPY_COUNTRY_TABLENAME, name)

    # Get Country Name ID from GeoPy Country Search Table
    def getCountrySearchNameId(self, search: str) -> int | None:
        return self.__getRootSearchNameId(GEOPY_COUNTRY_TABLENAME, search)

    # Get First Country Name ID from GeoPy Country Name Table
    def _getFirstCountryNameId(self) -> int | None:
        return self.__getFirst(getNameTableName(GEOPY_COUNTRY_TABLENAME))

    # Get First Country Search ID from GeoPy Country Search Table
    def _getFirstCountrySearchId(self) -> int | None:
        return self.__getFirst(getSearchTableName(GEOPY_COUNTRY_TABLENAME))

    # Add Country Name to GeoPy Country Name Table
    def _addCountryName(self, name: str) -> None:
        nameTableName = getNameTableName(GEOPY_COUNTRY_TABLENAME)

        # Add Country Name Query
        query = f"INSERT OR IGNORE INTO {nameTableName} ({GEOPY_NAME}) VALUES (?)"

        # Execute Query
        self._c.execute(query, (name,))

        counter = self.__getCounter(nameTableName) + 1

        # Remove First-in Country while counter is Greater than the Maximum Amount Allowed
        while counter > GEOPY_COUNTRY_MAX:
            self._removeFirstCountryName()
            counter -= 1

        # Set Country Table Counter
        self.__setCounter(nameTableName, counter)

    # Add Country Search Name to GeoPy Country Search Table
    def _addCountrySearch(self, search: str, countryNameId: int) -> tuple:
        searchTableName = getSearchTableName(GEOPY_COUNTRY_TABLENAME)
        locationNameId = getLocationNameIdColumn(GEOPY_COUNTRY_TABLENAME)

        # Add Country Search Name Query
        query = f"INSERT OR IGNORE INTO {searchTableName} ({GEOPY_SEARCH}, {locationNameId}) VALUES (?,?)"

        # Execute Query
        self._c.execute(
            query,
            (
                search,
                countryNameId,
            ),
        )

        counter = self.__getCounter(searchTableName) + 1

        # Remove First-in Country Search while counter is Greater than the Maximum Amount Allowed
        while counter > GEOPY_COUNTRY_MAX * GEOPY_LOCATION_SEARCH_MAX:
            self._removeFirstCountrySearch()
            counter -= 1

        # Set Country Search Table Counter
        self.__setCounter(searchTableName, counter)

    # Add Country
    def addCountry(self, search: str, name: str) -> None:
        # Add Country Name if it hasn't being Inserted
        self._addCountryName(name)

        # Get Country Name ID
        countryNameId = self.getCountryNameId(name)

        # Add Country Search
        self._addCountrySearch(search, countryNameId)

    # Remove First-in Country Name ID from GeoPy Country Name Table
    def _removeFirstCountryName(self) -> None:
        nameTableName = getNameTableName(GEOPY_COUNTRY_TABLENAME)

        # Get Country Name Id
        countryNameId = self._getFirstCountryNameId()

        self._removeCountryProvincesNameId(countryNameId)
        self._removeCountrySearchNameId(countryNameId)

        # Check Counter
        if self.__getCounter(nameTableName) == 0:
            return

        # Remove Country Name Query
        self.__removeNameId(nameTableName, countryNameId)

    # Remove First-in Country Search ID from GeoPy Country Search Table
    def _removeFirstCountrySearch(self) -> None:
        self.__removeNameId(
            getSearchTableName(GEOPY_COUNTRY_TABLENAME), self._getFirstCountrySearchId()
        )

    # Remove Country Searches for a Given Country Name ID
    def _removeCountrySearchNameId(self, countryNameId: int) -> None:
        self.__removeLocationsNameId(
            getSearchTableName(GEOPY_COUNTRY_TABLENAME),
            GEOPY_COUNTRY_TABLENAME,
            countryNameId,
        )

    # Get Province Name from GeoPy Province Name Table
    def getProvinceName(self, provinceNameId: int) -> str | None:
        return self.__getName(GEOPY_PROVINCE_TABLENAME, provinceNameId)

    # Get Province Name ID from GeoPy Province Name Table
    def getProvinceNameId(self, countryNameId: int, name: str) -> int | None:
        return self.__getChildNameId(
            GEOPY_PROVINCE_TABLENAME, GEOPY_COUNTRY_TABLENAME, name, countryNameId
        )

    # Get Province Name ID from GeoPy Province Search Table
    def getProvinceSearchNameId(
        self, countryNameId: int, provinceSearch: str
    ) -> int | None:
        return self.__getChildSearchNameId(
            GEOPY_PROVINCE_TABLENAME,
            GEOPY_COUNTRY_TABLENAME,
            provinceSearch,
            countryNameId,
        )

    # Get First Province Name ID from GeoPy Province Name Table
    def _getFirstProvinceNameId(self) -> int | None:
        return self.__getFirst(getNameTableName(GEOPY_PROVINCE_TABLENAME))

    # Get First Province Search ID from GeoPy Province Search Table
    def _getFirstProvinceSearchId(self) -> int | None:
        return self.__getFirst(getSearchTableName(GEOPY_PROVINCE_TABLENAME))

    # Add Province Name to GeoPy Province Name Table
    def _addProvinceName(self, countryNameId: int, provinceName: str) -> None:
        nameTableName = getNameTableName(GEOPY_PROVINCE_TABLENAME)
        parentLocationNameId = getLocationNameIdColumn(GEOPY_COUNTRY_TABLENAME)

        # Add Province Name Query
        query = f"INSERT OR IGNORE INTO {nameTableName} ({GEOPY_NAME}, {parentLocationNameId}) VALUES (?,?)"

        # Execute Query
        self._c.execute(
            query,
            (
                provinceName,
                countryNameId,
            ),
        )

        counter = self.__getCounter(nameTableName) + 1

        # Remove First-in Province while counter is Greater than the Maximum Amount Allowed
        while counter > GEOPY_PROVINCE_MAX:
            self._removeFirstProvinceName()
            counter -= 1

        # Set Province Table Counter
        self.__setCounter(nameTableName, counter)

    # Add Province Search Name to GeoPy Province Search Table
    def _addProvinceSearch(self, search: str, nameId: int) -> tuple:
        searchTableName = getSearchTableName(GEOPY_PROVINCE_TABLENAME)
        searchLocationNameId = getLocationNameIdColumn(GEOPY_PROVINCE_TABLENAME)

        # Add Province Search Name Query
        query = f"INSERT OR IGNORE INTO {searchTableName} ({GEOPY_SEARCH}, {searchLocationNameId}) VALUES (?,?)"

        # Execute Query
        self._c.execute(
            query,
            (
                search,
                nameId,
            ),
        )

        counter = self.__getCounter(searchTableName) + 1

        # Remove First-in Province Search while counter is Greater than the Maximum Amount Allowed
        while counter > GEOPY_PROVINCE_MAX * GEOPY_LOCATION_SEARCH_MAX:
            self._removeFirstProvinceSearch()
            counter -= 1

        # Set Province Search Table Counter
        self.__setCounter(searchTableName, counter)

    # Add Province
    def addProvince(
        self, countryNameId: int, provinceSearch: str, provinceName: str
    ) -> None:
        # Add Province Name if it hasn't being Inserted
        self._addProvinceName(countryNameId, provinceName)

        # Get Province Name ID
        provinceNameId = self.getProvinceNameId(countryNameId, provinceName)

        # Add Province Search
        self._addProvinceSearch(provinceSearch, provinceNameId)

    # Remove First-in Province Name ID from GeoPy Province Name Table
    def _removeFirstProvinceName(self) -> None:
        nameTableName = getNameTableName(GEOPY_PROVINCE_TABLENAME)

        # Get Province Name Id
        provinceNameId = self._getFirstProvinceNameId()

        self._removeProvinceRegionsNameId([provinceNameId])
        self._removeProvinceSearchNameId(provinceNameId)

        # Check Counter
        if self.__getCounter(nameTableName) == 0:
            return

        # Remove Province Name Query
        self.__removeNameId(nameTableName, provinceNameId)

    # Remove First-in Province Search ID from GeoPy Province Search Table
    def _removeFirstProvinceSearch(self) -> None:
        self.__removeNameId(
            getSearchTableName(GEOPY_PROVINCE_TABLENAME),
            self._getFirstProvinceSearchId(),
        )

    # Remove Province Searches for a Given Province Name ID
    def _removeProvinceSearchNameId(self, provinceNameId: int) -> None:
        self.__removeLocationsNameId(
            getSearchTableName(GEOPY_PROVINCE_TABLENAME),
            GEOPY_PROVINCE_TABLENAME,
            provinceNameId,
        )

    # Remove Provinces for a Given Country Name ID
    def _removeCountryProvincesNameId(self, countryNameId: int) -> None:
        # Remove Regions
        provinces = self.__getLocationsToRemove(
            GEOPY_PROVINCE_TABLENAME, GEOPY_COUNTRY_TABLENAME, countryNameId
        )
        self._removeProvinceRegionsNameId(provinces)

        # Remove Provinces Searches
        self.__removeLocationsSearches(
            GEOPY_PROVINCE_TABLENAME,
            GEOPY_COUNTRY_TABLENAME,
            countryNameId,
        )

        # Remove Provinces
        self.__removeLocationsNameId(
            getNameTableName(GEOPY_PROVINCE_TABLENAME),
            GEOPY_COUNTRY_TABLENAME,
            countryNameId,
        )

    # Get Region Name from GeoPy Region Name Table
    def getRegionName(self, regionNameId: int) -> str | None:
        return self.__getName(GEOPY_REGION_TABLENAME, regionNameId)

    # Get Region Name ID from GeoPy Region Name Table
    def getRegionNameId(self, provinceNameId: int, name: str) -> int | None:
        return self.__getChildNameId(
            GEOPY_REGION_TABLENAME, GEOPY_PROVINCE_TABLENAME, name, provinceNameId
        )

    # Get Region Name ID from GeoPy Region Search Table
    def getRegionSearchNameId(
        self, provinceNameId: int, regionSearch: str
    ) -> int | None:
        return self.__getChildSearchNameId(
            GEOPY_REGION_TABLENAME,
            GEOPY_PROVINCE_TABLENAME,
            regionSearch,
            provinceNameId,
        )

    # Get First Region Name ID from GeoPy Region Name Table
    def _getFirstRegionNameId(self) -> int | None:
        return self.__getFirst(getNameTableName(GEOPY_REGION_TABLENAME))

    # Get First Region Search ID from GeoPy Region Search Table
    def _getFirstRegionSearchId(self) -> int | None:
        return self.__getFirst(getSearchTableName(GEOPY_REGION_TABLENAME))

    # Add Region Name to GeoPy Region Name Table
    def _addRegionName(self, provinceNameId: int, regionName: str) -> None:
        nameTableName = getNameTableName(GEOPY_REGION_TABLENAME)
        parentLocationNameId = getLocationNameIdColumn(GEOPY_PROVINCE_TABLENAME)

        # Add Region Name Query
        query = f"INSERT OR IGNORE INTO {nameTableName} ({GEOPY_NAME}, {parentLocationNameId}) VALUES (?,?)"

        # Execute Query
        self._c.execute(
            query,
            (
                regionName,
                provinceNameId,
            ),
        )

        counter = self.__getCounter(nameTableName) + 1

        # Remove First-in Region while counter is Greater than the Maximum Amount Allowed
        while counter > GEOPY_REGION_MAX:
            self._removeFirstRegionName()
            counter -= 1

        # Set Region Table Counter
        self.__setCounter(nameTableName, counter)

    # Add Region Search Name to GeoPy Region Search Table
    def _addRegionSearch(self, search: str, nameId: int) -> tuple:
        searchTableName = getSearchTableName(GEOPY_REGION_TABLENAME)
        searchLocationNameId = getLocationNameIdColumn(GEOPY_REGION_TABLENAME)

        # Add Region Search Name Query
        query = f"INSERT OR IGNORE INTO {searchTableName} ({GEOPY_SEARCH}, {searchLocationNameId}) VALUES (?,?)"

        # Execute Query
        self._c.execute(
            query,
            (
                search,
                nameId,
            ),
        )

        counter = self.__getCounter(searchTableName) + 1

        # Remove First-in Region Search while counter is Greater than the Maximum Amount Allowed
        while counter > GEOPY_REGION_MAX * GEOPY_LOCATION_SEARCH_MAX:
            self._removeFirstRegionSearch()
            counter -= 1

        # Set Region Search Table Counter
        self.__setCounter(searchTableName, counter)

    # Add Region
    def addRegion(
        self, provinceNameId: int, regionSearch: str, regionName: str
    ) -> None:
        # Add Region Name if it hasn't being Inserted
        self._addRegionName(provinceNameId, regionName)

        # Get Region Name ID
        regionNameId = self.getRegionNameId(provinceNameId, regionName)

        # Add Region Search
        self._addRegionSearch(regionSearch, regionNameId)

    # Remove First-in Region Name ID from GeoPy Region Name Table
    def _removeFirstRegionName(self) -> None:
        nameTableName = getNameTableName(GEOPY_REGION_TABLENAME)

        # Get Region Name Id
        regionNameId = self._getFirstRegionNameId()

        self._removeRegionCitiesNameId([regionNameId])
        self._removeRegionSearchNameId(regionNameId)

        # Check Counter
        if self.__getCounter(nameTableName) == 0:
            return

        # Remove Region Name Query
        self.__removeNameId(nameTableName, regionNameId)

    # Remove First-in Region Search ID from GeoPy Region Search Table
    def _removeFirstRegionSearch(self) -> None:
        self.__removeNameId(
            getSearchTableName(GEOPY_REGION_TABLENAME),
            self._getFirstRegionSearchId(),
        )

    # Remove Region Searches for a Given Region Name ID
    def _removeRegionSearchNameId(self, regionNameId: int) -> None:
        self.__removeLocationsNameId(
            getSearchTableName(GEOPY_REGION_TABLENAME),
            GEOPY_REGION_TABLENAME,
            regionNameId,
        )

    # Remove Regions for a Given Province Name ID
    def _removeProvinceRegionsNameId(self, provinces: list[tuple[str]]) -> None:
        for p in provinces:
            provinceNameId = p[0]

            # Remove Cities
            regions = self.__getLocationsToRemove(
                GEOPY_REGION_TABLENAME, GEOPY_PROVINCE_TABLENAME, provinceNameId
            )
            self._removeRegionCitiesNameId(regions)

            # Remove Regions Searches

            self.__removeLocationsSearches(
                GEOPY_REGION_TABLENAME,
                GEOPY_PROVINCE_TABLENAME,
                provinceNameId,
            )

            # Remove Regions
            self.__removeLocationsNameId(
                getNameTableName(GEOPY_REGION_TABLENAME),
                GEOPY_PROVINCE_TABLENAME,
                provinceNameId,
            )

    # Get City Name from GeoPy City Name Table
    def getCityName(self, cityNameId: int) -> str | None:
        return self.__getName(GEOPY_CITY_TABLENAME, cityNameId)

    # Get City Name ID from GeoPy City Name Table
    def getCityNameId(self, regionNameId: int, name: str) -> int | None:
        return self.__getChildNameId(
            GEOPY_CITY_TABLENAME, GEOPY_REGION_TABLENAME, name, regionNameId
        )

    # Get City Name ID from GeoPy City Search Table
    def getCitySearchNameId(self, regionNameId: int, citySearch: str) -> int | None:
        return self.__getChildSearchNameId(
            GEOPY_CITY_TABLENAME,
            GEOPY_REGION_TABLENAME,
            citySearch,
            regionNameId,
        )

    # Get First City Name ID from GeoPy City Name Table
    def _getFirstCityNameId(self) -> int | None:
        return self.__getFirst(getNameTableName(GEOPY_CITY_TABLENAME))

    # Get First City Search ID from GeoPy City Search Table
    def _getFirstCitySearchId(self) -> int | None:
        return self.__getFirst(getSearchTableName(GEOPY_CITY_TABLENAME))

    # Add City Name to GeoPy City Name Table
    def _addCityName(self, regionNameId: int, cityName: str) -> None:
        nameTableName = getNameTableName(GEOPY_CITY_TABLENAME)
        parentLocationNameId = getLocationNameIdColumn(GEOPY_REGION_TABLENAME)

        # Add City Name Query
        query = f"INSERT OR IGNORE INTO {nameTableName} ({GEOPY_NAME}, {parentLocationNameId}) VALUES (?,?)"

        # Execute Query
        self._c.execute(
            query,
            (
                cityName,
                regionNameId,
            ),
        )

        counter = self.__getCounter(nameTableName) + 1

        # Remove First-in City while counter is Greater than the Maximum Amount Allowed
        while counter > GEOPY_CITY_MAX:
            self._removeFirstCityName()
            counter -= 1

        # Set City Table Counter
        self.__setCounter(nameTableName, counter)

    # Add City Search Name to GeoPy City Search Table
    def _addCitySearch(self, search: str, nameId: int) -> tuple:
        searchTableName = getSearchTableName(GEOPY_CITY_TABLENAME)
        searchLocationNameId = getLocationNameIdColumn(GEOPY_CITY_TABLENAME)

        # Add City Search Name Query
        query = f"INSERT OR IGNORE INTO {searchTableName} ({GEOPY_SEARCH}, {searchLocationNameId}) VALUES (?,?)"

        # Execute Query
        self._c.execute(
            query,
            (
                search,
                nameId,
            ),
        )

        counter = self.__getCounter(searchTableName) + 1

        # Remove First-in City Search while counter is Greater than the Maximum Amount Allowed
        while counter > GEOPY_CITY_MAX * GEOPY_LOCATION_SEARCH_MAX:
            self._removeFirstCitySearch()
            counter -= 1

        # Set City Search Table Counter
        self.__setCounter(searchTableName, counter)

    # Add City
    def addCity(self, regionNameId: int, citySearch: str, cityName: str) -> None:
        # Add City Name if it hasn't being Inserted
        self._addCityName(regionNameId, cityName)

        # Get City Name ID
        cityNameId = self.getCityNameId(regionNameId, cityName)

        # Add City Search
        self._addCitySearch(citySearch, cityNameId)

    # Remove First-in City Name ID from GeoPy City Name Table
    def _removeFirstCityName(self) -> None:
        nameTableName = getNameTableName(GEOPY_CITY_TABLENAME)

        # Get City Name Id
        cityNameId = self._getFirstCityNameId()

        self._removeCityCityAreasNameId([cityNameId])
        self._removeCitySearchNameId(cityNameId)

        # Check Counter
        if self.__getCounter(nameTableName) == 0:
            return

        # Remove City Name Query
        self.__removeNameId(nameTableName, cityNameId)

    # Remove First-in City Search ID from GeoPy City Search Table
    def _removeFirstCitySearch(self) -> None:
        self.__removeNameId(
            getSearchTableName(GEOPY_CITY_TABLENAME),
            self._getFirstCitySearchId(),
        )

    # Remove City Searches for a Given City Name ID
    def _removeCitySearchNameId(self, cityNameId: int) -> None:
        self.__removeLocationsNameId(
            getSearchTableName(GEOPY_CITY_TABLENAME),
            GEOPY_CITY_TABLENAME,
            cityNameId,
        )

    # Remove Cities for a Given Region Name ID
    def _removeRegionCitiesNameId(self, regions: list[tuple[str]]) -> None:
        for r in regions:
            regionNameId = r[0]

            # Remove City Areas
            areas = self.__getLocationsToRemove(
                GEOPY_CITY_TABLENAME, GEOPY_REGION_TABLENAME, regionNameId
            )
            self._removeCityCityAreasNameId(areas)

            # Remove Cities Searches
            self.__removeLocationsSearches(
                GEOPY_CITY_TABLENAME,
                GEOPY_REGION_TABLENAME,
                regionNameId,
            )

            # Remove Cities
            self.__removeLocationsNameId(
                getNameTableName(GEOPY_CITY_TABLENAME),
                GEOPY_REGION_TABLENAME,
                regionNameId,
            )

    # Get City Area Name from GeoPy City Area Name Table
    def getCityAreaName(self, areaNameId: int) -> str | None:
        return self.__getName(GEOPY_CITY_AREA_TABLENAME, areaNameId)

    # Get City Area Name ID from GeoPy City Area Name Table
    def getCityAreaNameId(self, cityNameId: int, name: str) -> int | None:
        return self.__getChildNameId(
            GEOPY_CITY_AREA_TABLENAME, GEOPY_CITY_TABLENAME, name, cityNameId
        )

    # Get City Area Name ID from GeoPy City Area Search Table
    def getCityAreaSearchNameId(self, cityNameId: int, areaSearch: str) -> int | None:
        return self.__getChildSearchNameId(
            GEOPY_CITY_AREA_TABLENAME,
            GEOPY_CITY_TABLENAME,
            areaSearch,
            cityNameId,
        )

    # Get First City Area Name ID from GeoPy City Area Name Table
    def _getFirstCityAreaNameId(self) -> int | None:
        return self.__getFirst(getNameTableName(GEOPY_CITY_AREA_TABLENAME))

    # Get First City Area Search ID from GeoPy City Area Search Table
    def _getFirstCityAreaSearchId(self) -> int | None:
        return self.__getFirst(getSearchTableName(GEOPY_CITY_AREA_TABLENAME))

    # Add City Area Name to GeoPy City Area Name Table
    def _addCityAreaName(self, cityNameId: int, areaName: str) -> None:
        nameTableName = getNameTableName(GEOPY_CITY_AREA_TABLENAME)
        parentLocationNameId = getLocationNameIdColumn(GEOPY_CITY_TABLENAME)

        # Add City Area Name Query
        query = f"INSERT OR IGNORE INTO {nameTableName} ({GEOPY_NAME}, {parentLocationNameId}) VALUES (?,?)"

        # Execute Query
        self._c.execute(
            query,
            (
                areaName,
                cityNameId,
            ),
        )

        counter = self.__getCounter(nameTableName) + 1

        # Remove First-in City Area while counter is Greater than the Maximum Amount Allowed
        while counter > GEOPY_CITY_AREA_MAX:
            self._removeFirstCityAreaName()
            counter -= 1

        # Set City Area Table Counter
        self.__setCounter(nameTableName, counter)

    # Add City Area Search Name to GeoPy City Area Search Table
    def _addCityAreaSearch(self, search: str, nameId: int) -> tuple:
        searchTableName = getSearchTableName(GEOPY_CITY_AREA_TABLENAME)
        searchLocationNameId = getLocationNameIdColumn(GEOPY_CITY_AREA_TABLENAME)

        # Add City Area Search Name Query
        query = f"INSERT OR IGNORE INTO {searchTableName} ({GEOPY_SEARCH}, {searchLocationNameId}) VALUES (?,?)"

        # Execute Query
        self._c.execute(
            query,
            (
                search,
                nameId,
            ),
        )

        counter = self.__getCounter(searchTableName) + 1

        # Remove First-in City Area Search while counter is Greater than the Maximum Amount Allowed
        while counter > GEOPY_CITY_AREA_MAX * GEOPY_LOCATION_SEARCH_MAX:
            self._removeFirstCityAreaSearch()
            counter -= 1

        # Set City Area Search Table Counter
        self.__setCounter(searchTableName, counter)

    # Add City Area
    def addCityArea(self, cityNameId: int, areaSearch: str, areaName: str) -> None:
        # Add City Area Name if it hasn't being Inserted
        self._addCityAreaName(cityNameId, areaName)

        # Get City Area Name ID
        areaNameId = self.getCityAreaNameId(cityNameId, areaName)

        # Add City Area Search
        self._addCityAreaSearch(areaSearch, areaNameId)

    # Remove First-in City Area Name ID from GeoPy City Area Name Table
    def _removeFirstCityAreaName(self) -> None:
        nameTableName = getNameTableName(GEOPY_CITY_AREA_TABLENAME)

        # Get City Area Name Id
        areaNameId = self._getFirstCityAreaNameId()

        self._removeCityAreaSearchNameId(areaNameId)

        # Check Counter
        if self.__getCounter(nameTableName) == 0:
            return

        # Remove City Area Name Query
        self.__removeNameId(nameTableName, areaNameId)

    # Remove First-in City Area Search ID from GeoPy City Area Search Table
    def _removeFirstCityAreaSearch(self) -> None:
        self.__removeNameId(
            getSearchTableName(GEOPY_CITY_AREA_TABLENAME),
            self._getFirstCityAreaSearchId(),
        )

    # Remove City Area Searches for a Given City Area Name ID
    def _removeCityAreaSearchNameId(self, areaNameId: int) -> None:
        self.__removeLocationsNameId(
            getSearchTableName(GEOPY_CITY_AREA_TABLENAME),
            GEOPY_CITY_AREA_TABLENAME,
            areaNameId,
        )

    # Remove City Areas for a Given City Name ID
    def _removeCityCityAreasNameId(self, cities: list[tuple[str]]) -> None:
        for c in cities:
            cityNameId = c[0]

            # Remove City Areas
            areas = self.__getLocationsToRemove(
                GEOPY_CITY_AREA_TABLENAME, GEOPY_CITY_TABLENAME, cityNameId
            )
            self._removeCityCityAreasNameId(areas)

            # Remove City Areas Searches
            self.__removeLocationsSearches(
                GEOPY_CITY_AREA_TABLENAME,
                GEOPY_CITY_TABLENAME,
                cityNameId,
            )

            # Remove City Areas
            self.__removeLocationsNameId(
                getNameTableName(GEOPY_CITY_AREA_TABLENAME),
                GEOPY_CITY_TABLENAME,
                cityNameId,
            )
