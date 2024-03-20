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

        # Initialize Rows Coutner Table
        self.__initTable()

    # Create GeoPy Rows Counter Table if it doesn't Exist
    def __initTable(self) -> None:
        # Create Table Query
        query = "CREATE TABLE IF NOT EXISTS rows_counter (tablename VARCHAR(50) PRIMARY KEY,counter INT NOT NULL);"

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
        query = "INSERT OR IGNORE INTO rows_counter (tablename, counter) VALUES (?,?)"

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
        if self._c is not None:
            self._c.close()
        if self._conn is not None:
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

    # Create GeoPy Country Name Table if it doesn't Exist
    def __initGeoPyCountryNameTable(self):
        # Create Table Query
        query = "CREATE TABLE IF NOT EXISTS country_name (name VARCHAR(50) NOT NULL);"

        # Execute Query
        self._c.execute(query)

    # Create GeoPy Country Search Table if it doesn't Exist
    def __initGeoPyCountrySearchTable(self):
        # Create Table Query
        query = "CREATE TABLE IF NOT EXISTS country_search (search VARCHAR(50) NOT NULL, name_id BIGINT NOT NULL, FOREIGN KEY (name_id) REFERENCES country_name(rowid));"

        # Execute Query
        self._c.execute(query)

    # Fetch One Item and return its Value
    def __fetchone(self):
        # Fetch Item
        self._item = self._item.fetchone()

        # Check Item Fetched
        if self._item is None:
            return None

        return self._item[0]

    # Get Counter from the Given Table
    def __getCounter(self, tableName: str) -> int:
        # Get Table Counter Query
        query = "SELECT counter FROM rows_counter WHERE tablename = ?"

        # Execute Query
        self._item = self._c.execute(query, (tableName,))

        return self.__fetchone()

    # Set Counter to the Given Table
    def __setCounter(self, tableName: str, counter: int):
        # Set Counter Query
        query = "UPDATE rows_counter SET counter = ? WHERE tablename = ?"

        # Execute Query
        self._c.execute(
            query,
            (
                counter,
                tableName,
            ),
        )

    # Get Country Name from GeoPy Country Name Table
    def _getCountryName(self, nameId: int) -> str | None:
        # Check Counter
        if self.__getCounter(GEOPY_COUNTRY_NAME_TABLENAME) == 0:
            return None

        # Get Country Name Query
        query = "SELECT name FROM country_name WHERE rowid = ?"

        # Execute Query
        self._item = self._c.execute(query, (nameId,))

        return self.__fetchone()

    # Get Country Name ID from GeoPy Country Name Table
    def _getCountryNameId(self, name: str) -> int | None:
        # Check Counter
        if self.__getCounter(GEOPY_COUNTRY_NAME_TABLENAME) == 0:
            return None

        # Get Country Name ID Query
        query = "SELECT rowid FROM country_name WHERE name = ?"

        # Execute Query
        self._item = self._c.execute(query, (name,))

        return self.__fetchone()

    # Get First Country Name ID from GeoPy Country Name Table
    def _getFirstCountryNameId(self) -> int | None:
        # Check Counter
        if self.__getCounter(GEOPY_COUNTRY_NAME_TABLENAME) == 0:
            return None

        # Get First Country Name ID Query
        query = "SELECT MIN(rowid) FROM country_name)"

        # Execute Query
        self._item = self._c.execute(query)

        return self.__fetchone()

    # Get First Country Name ID from GeoPy Country Search Table
    def _getFirstCountrySearchId(self) -> int | None:
        # Check Counter
        if self.__getCounter(GEOPY_COUNTRY_SEARCH_TABLENAME) == 0:
            return None

        # Get First Country Search Name ID Query
        query = "SELECT MIN(rowid) FROM country_search)"

        # Execute Query
        self._item = self._c.execute(query)

        return self.__fetchone()

    # Get Country Name ID from GeoPy Country Search Table
    def _getCountrySearchNameId(self, search: str) -> int | None:
        # Check Counter
        if self.__getCounter(GEOPY_COUNTRY_SEARCH_TABLENAME) == 0:
            return None

        # Get Country Name ID Query
        query = "SELECT name_id FROM country_search WHERE search = ?"

        # Execute Query
        self._item = self._c.execute(query, (search,))

        return self.__fetchone()

    # Get Country
    def getCountry(self, search: str) -> str | None:
        nameId = self._getCountrySearchNameId(search)

        # Check Country Name ID
        if nameId is None:
            return None

        return self._getCountryName(nameId)

    # Add Country Name to GeoPy Country Name Table
    def _addCountryName(self, name: str):
        # Add Country Name Query
        query = "INSERT OR IGNORE INTO country_name (name) VALUES (?)"

        # Execute Query
        self._c.execute(query, (name,))

        counter = self.__getCounter(GEOPY_COUNTRY_NAME_TABLENAME) + 1

        # Remove First-in Country while counter is Greater than the Maximum Amount Allowed
        while counter > GEOPY_COUNTRY_MAX:
            # Get Country Name Id
            countryNameId = self._getFirstCountryNameId()

            self._removeRegionCountryNameId(countryNameId)
            self._removeCountrySearchNameId(countryNameId)
            self._removeCountryName()
            counter -= 1

        # Execute Query
        print(self._c.execute("SELECT * FROM country_name").fetchall()[0])

        # Set Country Table Counter
        self.__setCounter(GEOPY_COUNTRY_NAME_TABLENAME, counter)

    # Add Country Search Name to GeoPy Country Search Table
    def _addCountrySearch(self, search: str, nameId: int) -> tuple:
        # Add Country Search Name Query
        query = "INSERT OR IGNORE INTO country_search (search, name_id) VALUES (?,?)"

        # Execute Query
        self._c.execute(
            query,
            (
                search,
                nameId,
            ),
        )

        counter = self.__getCounter(GEOPY_COUNTRY_SEARCH_TABLENAME) + 1

        # Remove First-in Country Search while counter is Greater than the Maximum Amount Allowed
        while counter > GEOPY_COUNTRY_MAX * GEOPY_LOCATION_SEARCH_MAX:
            self._removeCountrySearch()
            counter -= 1

        print(self._c.execute("SELECT * FROM country_search").fetchall()[0])

        # Set Country Search Table Counter
        self.__setCounter(GEOPY_COUNTRY_SEARCH_TABLENAME, counter)

    # Add Country
    def addCountry(self, search: str, name: str):
        # Add Country Name if it hasn't being Inserted
        self._addCountryName(name)

        # Get Country Name ID
        nameId = self._getCountryNameId(name)

        # Add Country Search
        self._addCountrySearch(search, nameId)

    # Remove First-in Country Name ID from GeoPy Country Name Table
    def _removeCountryName(self):
        # Check Counter
        if self.__getCounter(GEOPY_COUNTRY_NAME_TABLENAME) == 0:
            return

        # Remove Country Name Query
        query = "DELETE FROM country_name WHERE rowid = ?"

        # Execute Query
        self._c.execute(query, (self._getFirstCountryNameId(),))

    # Remove First-in Country Search ID from GeoPy Country Search Table
    def _removeCountrySearch(self):
        # Check Counter
        if self.__getCounter(GEOPY_COUNTRY_SEARCH_TABLENAME) == 0:
            return

        # Remove Country Search Query
        query = "DELETE FROM country_search WHERE rowid = ?"

        # Execute Query
        self._c.execute(query, (self._getFirstCountrySearchId(),))

    # Remove Country Searches for a Given Country Name ID
    def _removeCountrySearchNameId(self, nameId: int):
        # Remove Country Searches Query
        query = "DELETE FROM country_search WHERE name_id = ?"

        # Execute Query
        self._c.execute(query, (nameId,))
