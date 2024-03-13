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
    def modify(self, idField: str, idValue: int, field: str, value):
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
    def get(self, field: str, value):
        # Get Query
        query = sql.SQL("SELECT * FROM {tableName} WHERE {field} = (%s)").format(
            tableName=sql.Identifier(self._tableName), field=sql.Identifier(field)
        )

        # Execute Query
        try:
            self.c.execute(query, [value])
            self._items = self.c.fetchall()
        except Exception as err:
            raise err

    # Get All Items from Table
    def all(self, orderBy: str, desc: bool):
        # Fetch Items
        try:
            self._orderBy(orderBy, desc)
            self._items = self.c.fetchall()
        except Exception as err:
            raise err

    # Remove Row from Table
    def remove(self, idField: str, idValue: int):
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
    # Insert Country to Table
    def add(self, c: Country):
        # Get Query
        query = sql.SQL(
            "INSERT INTO {tableName} ({name}, {phone_prefix}) VALUES (%s, %s)"
        ).format(
            tableName=sql.Identifier(self._tableName),
            name=sql.Identifier(COUNTRY_NAME),
            phone_prefix=sql.Identifier(COUNTRY_PHONE_PREFIX),
        )

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
        query = sql.SQL(
            "INSERT INTO {tableName} ({name}, {phone_prefix}) VALUES %s"
        ).format(
            tableName=sql.Identifier(self._tableName),
            name=sql.Identifier(COUNTRY_NAME),
            phone_prefix=sql.Identifier(COUNTRY_PHONE_PREFIX),
        )

        countriesTuple = []
        countriesName = []

        # Create  Touples List from Countries List, and Countries Name List
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

    # Filter Items from  Country Table
    def get(self, field: str, value):
        BasicTable.get(self, field, value)

        # Print Items
        self.__print()

    # Get All Items from Country Table
    def all(self, orderBy: str, desc: bool):
        BasicTable.all(self, orderBy, desc)

        # Print Items
        self.__print()

    # Modify Row from Country Table
    def modify(self, cid: int, field: str, value):
        BasicTable.modify(self, COUNTRY_ID, cid, field, value)

    # Remove Row from Country Table
    def remove(self, cid: int):
        BasicTable.remove(self, COUNTRY_ID, cid)

        # TO DEVELOP: Check Regions that Depended on this Country

    # Constructor
    def __init__(self, database: Database):
        # Initialize Basic Table Class
        super().__init__(COUNTRY_TABLENAME, database)

    # Print Items
    def __print(self):
        # Number of Items
        nItems = len(self._items)

        # Initialize Rich Table
        table = Table(
            title="Country Table Query",
            title_style="title",
            header_style="header",
            caption=f"{nItems} Results Fetched",
            caption_style="caption",
            border_style="border",
            box=BOX_STYLE,
            row_styles=["text", "textAlt"],
        )

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Phone Prefix", justify="left", max_width=PHONE_PREFIX_NCHAR)

        # Check Items
        if self._items is None:
            console.print("Error: No Items Fetched", style="warning")
            return

        # Loop Over Items
        for item in self._items:
            table.add_row(str(item[0]), item[1], str(item[2]))

        # Print New Line
        console.print("\n")

        # Print Table
        console.print(table)
