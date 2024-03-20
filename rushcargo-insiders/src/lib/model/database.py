from psycopg import connect, sql
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
def getTable(tableName: str, nItems: int) -> Table:
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
def noCoincidenceFetched() -> None:
    console.print("No Results Fetched", style="warning")


# Message Printed when the User tries to Insert a Row which has Unique Fields that Contains Values
# that have been already Inserted
def uniqueInserted(tableName: str, field: str, value) -> None:
    console.print(
        f"Unique '{value}' Already Inserted at '{field}' on {tableName}",
        style="warning",
    )


# Message Printed when the User tries to Insert a Row that Contains Values which Violates
# Unique Constraint of Multiple Columns
def uniqueInsertedMult(tableName: str, field: list[str], value: list) -> None:
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
    _conn = None
    _c = None

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
        self._conn = connect(
            f"host={host} dbname={dbname} user={user} password={password} port={port} sslmode={'require'}"
        )
        self._c = self.getCursor()

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


# Initialize Database Connection
def initDb() -> tuple[Database, str, str]:
    # Get Path to 'src' Directory
    src = Path(__file__).parent.parent.parent

    # Get Path to 'rushcargo-insiders' Directory
    main = src.parent

    # Get Path to the .env File for Local Environment Variables
    dotenvPath = main / "venv/.env"

    # Load .env File
    load_dotenv(dotenvPath)

    # Get Database-related Environment Variables
    try:
        host = os.getenv("HOST")
        port = os.getenv("PORT")
        dbname = os.getenv("DBNAME")
        user = os.getenv("USER")
        password = os.getenv("PASSWORD")
    except:
        console.print("Missing Database Information", style="warning")

    # Initialize Database Object
    return Database(dbname, user, password, host, port), user


# Basic Table Class
class BasicTable:
    # Protected Fields
    _tableName = None
    _items = None
    _c = None

    # Constructor
    def __init__(self, tableName: str, database: Database):
        # Assign Table Name
        self._tableName = tableName

        # Get Cursor
        self._c = database.getCursor()

    # Returns Get Query
    def __getQuery(self, field: str, value):
        return sql.SQL("SELECT * FROM {tableName} WHERE {field} = {value}").format(
            tableName=sql.Identifier(self._tableName),
            field=sql.Identifier(field),
            value=str(value),
        )

    # Returns Get Query with One And Condition
    def __getAndQuery(self, field1: str, field2: str, value1: str, value2: str):
        return sql.SQL(
            "SELECT * FROM {tableName} WHERE {field1} = {value1} AND {field2} = {value2}"
        ).format(
            tableName=sql.Identifier(self._tableName),
            field1=sql.Identifier(field1),
            field2=sql.Identifier(field2),
            value1=str(value1),
            value2=str(value2),
        )

    # Order By Table
    def _orderBy(self, orderBy: str, desc: bool) -> None:
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
            return self._c.execute(query)
        except Exception as err:
            raise (err)

    # Modify Row from Table
    def _modify(self, idField: str, idValue: int, field: str, value) -> None:
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
            self._c.execute(query, [value, idValue])
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
        query = self.__getQuery(field, value)

        # Execute Query
        try:
            self._items = self._c.execute(query).fetchall()
        except Exception as err:
            raise err

        return len(self._items) > 0

    # Filter Items from Table with Multiple WHERE Conditions
    def _getMult(self, field: list[str], value: list) -> bool:
        # Lists MUST have the Same Length
        length = len(field)

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
            query = self.__getAndQuery(field[0], field[1], value[0], value[1])

        # Execute Query
        try:
            self._items = self._c.execute(query).fetchall()
        except Exception as err:
            raise err

        return len(self._items) > 0

    # Get All Items from Table
    def _all(self, orderBy: str, desc: bool) -> None:
        # Fetch Items
        try:
            self._items = self._orderBy(orderBy, desc).fetchall()
        except Exception as err:
            raise err

    # Remove Row from Table
    def _remove(self, idField: str, idValue: int) -> None:
        # Get Query
        query = sql.SQL("DELETE FROM {tablename} WHERE {id} = (%s)").format(
            tablename=sql.Identifier(self._tableName), id=sql.Identifier(idField)
        )

        try:
            self._c.execute(query, [idValue])
            console.print(
                f"Row with '{idField}' '{idValue}' Successfully Removed from {self._tableName} Table",
                style="success",
            )
        except Exception as err:
            raise err
