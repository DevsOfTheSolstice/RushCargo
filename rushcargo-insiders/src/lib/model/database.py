from psycopg2 import connect, sql, extras
from rich.console import Console
from rich.table import Table
from pathlib import Path
import os
from dotenv import load_dotenv


from .classes import *
from .constants import *
from .exceptions import *

# Set Custom Theme
console = Console(theme=THEME)


# Get Table with Default values
def getTable(tableName: str, nItems: int):
    # Initialize Rich Table
    return Table(
        title=f"{tableName} Table Query",
        title_style="title",
        header_style="header",
        caption=f"{nItems} Results Fetched",
        caption_style="caption",
        border_style="border",
        box=BOX_STYLE,
        row_styles=["text", "textAlt"],
    )


# Message Printed when there's Nothing Fetched from Query
def noCoincidenceFetched():
    console.print("No Results Fetched", style="warning")


# Message Printed when the User tries to Insert a Row which has Unique Fields that Contains Values
# that have been already Inserted
def uniqueInserted(tableName: str, field: str, value):
    console.print(
        f"Unique '{value}' Already Inserted at '{field}' on {tableName}",
        style="warning",
    )


# Message Printed when the User tries to Insert a Row that Contains Values which Violates
# Unique Constraint of Multiple Columns
def uniqueInsertedMult(tableName: str, field: list[str], value: list):
    fieldStr = ",".join(f for f in field)
    valueStr = ",".join(str(v) for v in value)

    console.print(
        f"({valueStr}) at ({fieldStr}) Violates Unique Constraint on {tableName}",
        style="warning",
    )


# Default Database Class
class Database:
    # Protected Fields
    _host = None
    _dbname = None
    _user = None
    _password = None
    _port = None

    # Public Fields
    conn = None
    c = None

    # Constructor
    def __init__(
        self,
        dbname: str,
        user: str,
        password: str,
        host: str = "localhost",
        port: int = 5432,
    ):
        # Save Connection Data to Protected Fields
        self._host = host
        self._dbname = dbname
        self._user = user
        self._password = password
        self._port = port

        # Connect to Database
        self.conn = connect(
            host=host,
            dbname=dbname,
            user=user,
            password=password,
            port=port,
            sslmode="require",
        )
        self.c = self.getCursor()

    # Destructor
    def __del__(self):
        # Commit Command
        self.conn.commit()

        # Close Connection
        if self.c is not None:
            self.c.close()
        if self.conn is not None:
            self.conn.close()

    # Get Cursor
    def getCursor(self):
        return self.conn.cursor()


# Initialize Database Connection
def initdb():
    # Get Path to 'src' Directory
    src = Path(__file__).parent.parent.parent

    # Get Path to 'rushcargo-insiders' Directory
    main = src.parent

    # Get Path to the .env File for Local Environment Variables
    dotenvPath = main / "venv/.env"

    # Load .env File
    load_dotenv(dotenvPath)

    # Get Database-related Environment Variables
    host = os.getenv("HOST")
    port = os.getenv("PORT")
    dbname = os.getenv("DBNAME")
    user = os.getenv("USER")
    password = os.getenv("PASSWORD")

    # Initialize Database Object
    return Database(dbname, user, password, host, port)


# Basic Table Class
class BasicTable:
    # Private Fields
    _tableName = None
    _items = None

    # Public Fields
    c = None

    # Constructor
    def __init__(self, tableName: str, database: Database):
        # Assign Table Name
        self._tableName = tableName

        # Get Cursor
        self.c = database.getCursor()

    # Returns Get Query
    def __getQuery(self, field: str):
        return sql.SQL("SELECT * FROM {tableName} WHERE {field} = (%s)").format(
            tableName=sql.Identifier(self._tableName), field=sql.Identifier(field)
        )

    # Returns Get Query with One And Condition
    def __getAndQuery(self, field1: str, field2: str):
        return sql.SQL(
            "SELECT * FROM {tableName} WHERE {field1} = (%s) AND {field2} = (%s)"
        ).format(
            tableName=sql.Identifier(self._tableName),
            field1=sql.Identifier(field1),
            field2=sql.Identifier(field2),
        )

    # Order By Table
    def _orderBy(self, orderBy: str, desc: bool):
        query = None

        # Get Query
        if not desc:
            query = sql.SQL("SELECT * FROM {tableName} ORDER BY {order}").format(
                tableName=sql.Identifier(self._tableName),
                order=sql.Identifier(orderBy),
            )
        else:
            query = sql.SQL("SELECT * FROM {tableName} ORDER BY {order} DESC").format(
                tableName=sql.Identifier(self._tableName),
                order=sql.Identifier(orderBy),
            )

        # Execute Query
        try:
            self.c.execute(query)
        except Exception as err:
            raise (err)

    # Modify Row from Table
    def _modify(self, idField: str, idValue: int, field: str, value):
        # Get Query
        query = sql.SQL(
            "UPDATE {tableName} SET {field} = (%s) WHERE {id} = (%s)"
        ).format(
            tableName=sql.Identifier(self._tableName),
            field=sql.Identifier(field),
            id=sql.Identifier(idField),
        )

        # Execute Query
        try:
            self.c.execute(query, [value, idValue])
            console.print(
                f"Data '{value}' Successfully Assigned to '{field}' at '{idField}' '{idValue}' in {self._tableName} Table",
                style="success",
            )
        except Exception as err:
            raise err

    # Filter Items from Table
    def _get(self, field: str, value) -> bool:
        """
        Returns True if One or More Items were Fetched. Otherwise, False
        """

        # Get Query
        query = self.__getQuery(field)

        # Execute Query
        try:
            self.c.execute(query, [value])
            self._items = self.c.fetchall()
        except Exception as err:
            raise err

        return len(self._items) > 0

    # Filter Items from Table with Multiple WHERE Conditions
    def _getMult(self, field: list[str], value: list) -> bool:
        # Lists MUST have the Same Length
        length = len(field)
        values = None

        if length != len(value):
            raise LenError()

        """
        Returns True if One or More Items were Fetched. Otherwise, False
        """

        query = None

        # Check Number of WHERE Conditions
        if length > 2:
            console.print("Query hasn't been Implemented", style="warning")
            return

        # Get Query
        elif length == 2:
            query = self.__getAndQuery(field[0], field[1])
            values = [value[0], value[1]]

        # Execute Query
        try:
            self.c.execute(query, values)
            self._items = self.c.fetchall()
        except Exception as err:
            raise err

        return len(self._items) > 0

    # Get All Items from Table
    def _all(self, orderBy: str, desc: bool):
        # Fetch Items
        try:
            self._orderBy(orderBy, desc)
            self._items = self.c.fetchall()
        except Exception as err:
            raise err

    # Remove Row from Table
    def _remove(self, idField: str, idValue: int):
        # Get Query
        query = sql.SQL("DELETE FROM {tablename} WHERE {id} = (%s)").format(
            tablename=sql.Identifier(self._tableName), id=sql.Identifier(idField)
        )

        try:
            self.c.execute(query, [idValue])
            console.print(
                f"Row with '{idField}' '{idValue}' Successfully Removed from {self._tableName} Table",
                style="success",
            )
        except Exception as err:
            raise err


# Country Table Class
class CountryTable(BasicTable):
    # Constructor
    def __init__(self, database: Database):
        # Initialize Basic Table Class
        super().__init__(COUNTRY_TABLENAME, database)

    # Print Items
    def __print(self):
        c = None

        # Number of Items
        nItems = len(self._items)

        # No Results
        if nItems == 0:
            noCoincidenceFetched()
            return

        # Initialize Rich Table
        table = getTable("Country", nItems)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Phone Prefix", justify="left", max_width=PHONE_PREFIX_NCHAR)

        # Loop Over Items
        for item in self._items:
            # Intialize Country from Item Fetched
            c = Country.fromItemFetched(item)

            # Add Row to Rich Table
            table.add_row(str(c.countryId), c.name, str(c.phonePrefix))

        # Print New Line
        console.print("\n")

        # Print Table
        console.print(table)

    # Get Insert Query
    def __getInsertQuery(self):
        return sql.SQL("INSERT INTO {tableName} ({fields}) VALUES (%s, %s)").format(
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [sql.Identifier(COUNTRY_NAME), sql.Identifier(COUNTRY_PHONE_PREFIX)]
            ),
        )

    # Insert Country to Table
    def add(self, c: Country):
        # Get Query
        query = self.__getInsertQuery()

        # Execute Query
        try:
            self.c.execute(query, [c.name, c.phonePrefix])
            console.print(
                f"{c.name} Successfully Inserted to {self._tableName} Table",
                style="success",
            )
        except Exception as err:
            raise err

    # Insert Multiple Countries to Table
    def addMany(self, countries: list[Country]):
        # Get Query
        query = self.__getInsertQuery()

        countriesTuple = []
        countriesName = []

        # Create Tuples List from Countries List, and Countries Name List
        for c in countries:
            countriesTuple.append([c.name, c.phonePrefix])
            countriesName.append(c.name)

        # Execute Query
        try:
            extras.execute_values(
                self.c, query.as_string(self.c), countriesTuple, page_size=100
            )
            console.print(
                f"{' '.join(countriesName)} Successfully Inserted to {self._tableName} Table",
                style="success",
            )
        except Exception as err:
            raise err

    # Filter Items from Country Table
    def get(self, field: str, value, printItems: bool = True) -> int:
        if not BasicTable._get(self, field, value):
            return False

        # Print Items
        if printItems:
            self.__print()
        return True

    # Find Country
    def find(self, field: str, value) -> Country | None:
        """
        Returns Country Object if it was Found. Otherwise, False

        NOTE: All Columns from this Table Contain Unique Values
        """

        # Get Country
        if not self._get(field, value):
            return None

        # Get Country from Item Fetched
        return Country.fromItemFetched(self._items[0])

    # Get All Items from Country Table
    def all(self, orderBy: str, desc: bool):
        BasicTable._all(self, orderBy, desc)

        # Print Items
        self.__print()

    # Modify Row from Country Table
    def modify(self, cid: int, field: str, value):
        BasicTable._modify(self, COUNTRY_ID, cid, field, value)

    # Remove Row from Country Table
    def remove(self, cid: int):
        BasicTable._remove(self, COUNTRY_ID, cid)


# Region Table Class
class RegionTable(BasicTable):
    # Constructor
    def __init__(self, database: Database):
        # Initialize Basic Table Class
        super().__init__(REGION_TABLENAME, database)

    # Print Items
    def __print(self):
        r = None

        # Number of Items
        nItems = len(self._items)

        # No Results
        if nItems == 0:
            noCoincidenceFetched()
            return

        # Initialize Rich Table
        table = getTable("Region", nItems)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Country ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Air Forwarder ID", justify="left", max_width=FORWARDER_NCHAR)
        table.add_column(
            "Ocean Forwarder ID", justify="left", max_width=FORWARDER_NCHAR
        )

        # Loop Over Items
        for item in self._items:
            # Intialize Region from Item Fetched
            r = Region.fromItemFetched(item)

            # Add Row to Rich Table
            table.add_row(
                str(r.regionId),
                str(r.countryId),
                r.name,
                str(r.airForwarderId),
                str(r.oceanForwarderId),
            )

        # Print New Line
        console.print("\n")

        # Print Table
        console.print(table)

    # Get Insert Query
    def __getInsertQuery(self):
        return sql.SQL("INSERT INTO {tableName} ({fields}) VALUES (%s, %s)").format(
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [sql.Identifier(REGION_FK_COUNTRY), sql.Identifier(REGION_NAME)]
            ),
        )

    # Insert Region to Table
    def add(self, r: Region):
        # Get Query
        query = self.__getInsertQuery()

        # Execute Query
        try:
            self.c.execute(query, [r.countryId, r.name])
            console.print(
                f"{r.name} Successfully Inserted to {self._tableName} Table",
                style="success",
            )
        except Exception as err:
            raise err

    # Insert Multiple Regions to Table
    def addMany(self, regions: list[Region]):
        # Get Query
        query = self.__getInsertQuery()

        regionsTuple = []
        regionsName = []

        # Create Tuples List from Regions List, and Regions Name List
        for r in regions:
            regionsTuple.append([r.countryId, r.name])
            regionsName.append(r.name)

        # Execute Query
        try:
            extras.execute_values(
                self.c, query.as_string(self.c), regionsTuple, page_size=100
            )
            console.print(
                f"{' '.join(regionsName)} Successfully Inserted to {self._tableName} Table",
                style="success",
            )
        except Exception as err:
            raise err

    # Filter Items from Region Table
    def get(self, field: str, value, printItems: bool = True):
        if not BasicTable._get(self, field, value):
            return False

        # Print Items
        if printItems:
            self.__print()
        return True

    # Filter Items with Multiple Conditions from Region Table
    def getMult(self, field: list[str], value: list, printItems: bool = True) -> bool:
        if not BasicTable._getMult(self, field, value):
            return False

        # Print Items
        if printItems:
            self.__print()
        return True

    # Find Region
    def find(self, countryId: int, regionName: str) -> Region | None:
        """
        Returns Region Object if it was Found. Otherwise, False
        """

        # Get Region
        if not self.getMult(
            [REGION_FK_COUNTRY, REGION_NAME], [countryId, regionName], False
        ):
            return None

        # Get Region Fields from Item Fetched
        return Region.fromItemFetched(self._items[0])

    # Get All Items from Region Table
    def all(self, orderBy: str, desc: bool):
        BasicTable._all(self, orderBy, desc)

        # Print Items
        self.__print()

    # Modify Row from Region Table
    def modify(self, rid: int, field: str, value):
        BasicTable._modify(self, REGION_ID, rid, field, value)

    # Remove Row from Region Table
    def remove(self, rid: int):
        BasicTable._remove(self, REGION_ID, rid)


# City Table Class
class CityTable(BasicTable):
    # Constructor
    def __init__(self, database: Database):
        # Initialize Basic Table Class
        super().__init__(CITY_TABLENAME, database)

    # Print Items
    def __print(self):
        c = None

        # Number of Items
        nItems = len(self._items)

        # No Results
        if nItems == 0:
            noCoincidenceFetched()
            return

        # Initialize Rich Table
        table = getTable("City", nItems)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Region ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Warehouse ID", justify="left", max_width=WAREHOUSE_NCHAR)

        # Loop Over Items
        for item in self._items:
            # Intialize Region from Item Fetched
            c = City.fromItemFetched(item)

            # Add Row to Rich Table
            table.add_row(str(c.cityId), str(c.regionId), c.name, str(c.warehouseId))

        # Print New Line
        console.print("\n")

        # Print Table
        console.print(table)

    # Get Insert Query
    def __getInsertQuery(self):
        return sql.SQL("INSERT INTO {tableName} ({fields}) VALUES (%s, %s)").format(
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [sql.Identifier(CITY_FK_REGION), sql.Identifier(CITY_NAME)]
            ),
        )

    # Insert City to Table
    def add(self, c: City):
        # Get Query
        query = self.__getInsertQuery()

        # Execute Query
        try:
            self.c.execute(query, [c.regionId, c.name])
            console.print(
                f"{c.name} Successfully Inserted to {self._tableName} Table",
                style="success",
            )
        except Exception as err:
            raise err

    # Insert Multiple Cities to Table
    def addMany(self, cities: list[City]):
        # Get Query
        query = self.__getInsertQuery()

        citiesTuple = []
        citiesName = []

        # Create Tuples List from Cities List, and Cities Name List
        for c in cities:
            citiesTuple.append([c.regionId, c.name])
            citiesName.append(c.name)

        # Execute Query
        try:
            extras.execute_values(
                self.c, query.as_string(self.c), citiesTuple, page_size=100
            )
            console.print(
                f"{' '.join(citiesName)} Successfully Inserted to {self._tableName} Table",
                style="success",
            )
        except Exception as err:
            raise err

    # Filter Items from City Table
    def get(self, field: str, value, printItems: bool = True):
        if not BasicTable._get(self, field, value):
            return False

        # Print Items
        if printItems:
            self.__print()
        return True

    # Filter Items with Multiple Conditions from City Table
    def getMult(self, field: list[str], value: list, printItems: bool = True) -> bool:
        if not BasicTable._getMult(self, field, value):
            return False

        # Print Items
        if printItems:
            self.__print()
        return True

    # Get All Items from City Table
    def all(self, orderBy: str, desc: bool):
        BasicTable._all(self, orderBy, desc)

        # Print Items
        self.__print()

    # Modify Row from City Table
    def modify(self, cid: int, field: str, value):
        BasicTable._modify(self, CITY_ID, cid, field, value)

    # Remove Row from City Table
    def remove(self, cid: int):
        BasicTable._remove(self, CITY_ID, cid)
