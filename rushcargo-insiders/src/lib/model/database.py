from psycopg2 import connect, sql, extras
from rich.console import Console
from rich.table import Table

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


# Country Table Class
class CountryTable:
    # Private Fields
    __tableName = COUNTRY_TABLENAME
    __items = None

    # Public Fields
    c = None

    # Remove Country from Table
    def remove(self, cid: int):

        query = sql.SQL("DELETE FROM {tablename} WHERE {id} = (%s)").format(
            tablename=sql.Identifier(self.__tableName), id=sql.Identifier(COUNTRY_ID)
        )

        try:
            self.c.execute(query, [cid])
            console.print(
                f"Country with '{COUNTRY_ID}' '{cid}' Successfully Removed from {self.__tableName} Table",
                style="success",
            )
        except Exception as err:
            console.print(err, style="warning")
            return

        # TO DEVELOP: Check Regions that Depended on this Country

    # Insert Country to Table
    def add(self, c: Country):
        # Get Query
        query = sql.SQL(
            "INSERT INTO {tableName} ({name}, {phone_prefix}) VALUES (%s, %s)"
        ).format(
            tableName=sql.Identifier(self.__tableName),
            name=sql.Identifier(COUNTRY_NAME),
            phone_prefix=sql.Identifier(COUNTRY_PHONE_PREFIX),
        )

        # Execute Query
        try:
            self.c.execute(query, [c.name, c.phonePrefix])
            console.print(
                f"{c.name} Successfully Inserted to {self.__tableName} Table",
                style="success",
            )
        except Exception as err:
            console.print(err, style="warning")

    # Insert Multiple Countries to Table
    def addMany(self, countries: list[Country]):
        # Get Query
        query = sql.SQL(
            "INSERT INTO {tableName} ({name}, {phone_prefix}) VALUES %s"
        ).format(
            tableName=sql.Identifier(self.__tableName),
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
                f"{' '.join(countriesName)} Successfully Inserted to {self.__tableName} Table",
                style="success",
            )
        except Exception as err:
            console.print(err, style="warning")

    # Modify Country by Country ID
    def modify(self, cid: int, field: str, value):
        # Get Query
        query = sql.SQL(
            "UPDATE {tableName} SET {field} = (%s) WHERE {id} = (%s)"
        ).format(
            tableName=sql.Identifier(self.__tableName),
            field=sql.Identifier(field),
            id=sql.Identifier(COUNTRY_ID),
        )

        # Execute Query
        try:
            self.c.execute(query, [value, cid])
            console.print(
                f"Data '{value}' Successfully Assigned to '{field}' at '{COUNTRY_ID}' '{cid}' in {self.__tableName} Table",
                style="success",
            )
        except Exception as err:
            console.print(err, style="warning")

    # Filter Items from Country Table
    def get(self, field: str, value):
        # Get Query
        query = sql.SQL("SELECT * FROM {tableName} WHERE {field} = (%s)").format(
            tableName=sql.Identifier(self.__tableName), field=sql.Identifier(field)
        )

        # Execute Query
        try:
            self.c.execute(query, [value])
            self.__items = self.c.fetchall()
        except Exception as err:
            console.print(err, style="warning")
            return

        # Print Items
        self.__print()

    # Get All Items from Country Table
    def getAll(self, orderBy: str = COUNTRY_ID, desc: bool = False):
        # Fetch Items
        try:
            self.__orderBy(orderBy, desc)
            self.__items = self.c.fetchall()
        except Exception as err:
            console.print(err, style="warning")
            return

        # Print Items
        self.__print()

    # Constructor
    def __init__(self, database: Database):
        # Get Cursor
        self.c = database.getCursor()

    # Sort By Table
    def __orderBy(self, orderBy: str, desc: bool):
        query = None

        # Get Query
        if not desc:
            query = sql.SQL("SELECT * FROM {tableName} ORDER BY {order}").format(
                tableName=sql.Identifier(self.__tableName),
                order=sql.Identifier(orderBy),
            )
        else:
            query = sql.SQL("SELECT * FROM {tableName} ORDER BY {order} DESC").format(
                tableName=sql.Identifier(self.__tableName),
                order=sql.Identifier(orderBy),
            )

        # Execute Query
        try:
            self.c.execute(query)
        except Exception as err:
            raise (err)

    # Print Items
    def __print(self):
        # Number of Items
        nItems = len(self.__items)

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

        table.add_column("Name", justify="left", max_width=COUNTRY_NAME_NCHAR)

        table.add_column("Phone Prefix", justify="left", max_width=PHONE_PREFIX_NCHAR)

        # Check Items
        if self.__items is None:
            console.print("Error: No Items Fetched", style="warning")
            return

        # Loop Over Items
        for item in self.__items:
            table.add_row(str(item[0]), item[1], str(item[2]))

        # Print New Line
        console.print("\n")

        # Print Table
        console.print(table)
