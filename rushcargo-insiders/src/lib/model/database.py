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
    def __init__(self, dbname: str, user: str, password: str, host: str = "localhost", port: int = 5432):         
        # Save Connection Data to Protected Fields
        self._host = host
        self._dbname = dbname
        self._user = user
        self._password = password
        self._port = port
        
        # Connect to Database
        self.conn = connect(
            host = host,
            dbname = dbname,
            user = user,
            password = password,
            port = port,
            sslmode = 'require'
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
    __tableName = "country"
    __items = None
    
    # Public Fields
    c = None

    # Constructor
    def __init__(self, database: Database):         
      # Get Cursor
      self.c = database.getCursor()

   # Check if Column Used as Parameter is Valid
    def __checkField(self, field: str, isIdValid: bool = True) -> bool:
        if field == COUNTRY_NAME or field == COUNTRY_PHONE_PREFIX:
            return True
        if isIdValid and field == COUNTRY_ID:
            return True
        return False      

    # Delete Country from Table
    def delete(self, field: str, value):
        # Check Field Parameter
        if not self.__checkField(field):
          raise FieldError(field, self.__tableName)
        
        query = sql.SQL(
                "DELETE FROM {tablename} WHERE {field} = (%s)"
            ).format(
                tablename = sql.Identifier(self.__tableName),
                field = sql.Identifier(field))
        
        try:
            self.c.execute(query, [value])
            console.print(f"Deleted Coincidences which had: '{value}' in '{field}' Column\n", style="success")
        except Exception as err:
            console.print(err, style="warning")
            return

        # TO DEVELOP: Check Regions that Depended on this Country

    # Insert Country to Table
    def insert(self, c: Country): 
        # Get Query
        query = sql.SQL(
                "INSERT INTO {tableName} ({name}, {phone_prefix}) VALUES (%s, %s)"
            ).format(
                tableName = sql.Identifier(self.__tableName),
                name = sql.Identifier(COUNTRY_NAME),
                phone_prefix = sql.Identifier(COUNTRY_PHONE_PREFIX))

        # Execute Query
        try:
            self.c.execute(query, [c.name, c.phonePrefix])
            console.print(f"Country Successfully Inserted to {self.__tableName} Table\n", style="success")
        except Exception as err:
            console.print(err, style="warning")
        
    # Insert Multiple Countries to Table
    def insertMany(self, countries: list[Country]):
        # Get Query
        query = sql.SQL(
                "INSERT INTO {tableName} ({name}, {phone_prefix}) VALUES %s"
            ).format(
                tableName = sql.Identifier(self.__tableName),
                name = sql.Identifier(COUNTRY_NAME),
                phone_prefix = sql.Identifier(COUNTRY_PHONE_PREFIX))

        countriesTuple = []
        for c in countries:
            countriesTuple.append([c.name, c.phonePrefix])

        # Execute Query
        try:
            extras.execute_values(self.c, query.as_string(self.c), countriesTuple, page_size=100)
            console.print(f"Countries Successfully Inserted to {self.__tableName}\n", style="success")
        except Exception as err:
            console.print(err, style="warning")

    # Update Country by Row ID
    def update(self, id: int, field: str, value):
        # Check Field Parameter
        if not self.__checkField(field, False):
            raise FieldError(field, self.__tableName)
        
        # Get Query
        query = sql.SQL(
                "UPDATE {tableName} SET {field} = (%s) WHERE {rowid} = (%s)"
            ).format(
                tableName = sql.Identifier(self.__tableName),
                field = sql.Identifier(field),
                rowid = sql.Identifier(COUNTRY_ID))
        
        # Execute Query
        try:
            self.c.execute(query, [value, id])
            console.print(f"Country {id} Successfully Updated to {self.__tableName}\n", style="success")
        except Exception as err:
            console.print(err, style="warning")

    # Sort By Table
    def __orderBy(self, orderBy: str, desc: bool):
        if desc:
            orderBy = orderBy.concat(' DESC')

        # Get Query
        query = sql.SQL(
                    "SELECT * FROM {tableName} ORDER BY {order}"
                ).format(
                    tableName = sql.Identifier(self.__tableName),
                    order = sql.Identifier(orderBy))
        
        # Execute Query
        try:
            self.c.execute(query, [orderBy])
        except Exception as err:
            raise(err)
        
    # Return All Countries
    def __fetch(self, orderBy: str, desc: bool):
        try:
            self.__orderBy(orderBy, desc)
            self.__items = self.c.fetchall()
        except Exception as err:
            raise err
        
    # Filter Items from Country Table 
    def get(self, field: str, value):
        # Check Field Parameter
        if not self.__checkField(field):
            raise FieldError(field, self.__tableName)

         # Get Query
        query = sql.SQL(
                    "SELECT * FROM {tableName} WHERE {field} = (%s)"
                ).format(
                    tableName = sql.Identifier(self.__tableName),
                    field = sql.Identifier(field))
        
        # Execute Query
        try:
            self.c.execute(query, value)
        except Exception as err:
            console.print(err, style="warning")
            return

        # Print Items
        self.__print()            


    # Get All Items from Country Table
    def getAll(self, orderBy: str = COUNTRY_ID, desc: bool = False):
        # Check orderBy
        if not self.__checkField(orderBy, True):
           raise FieldError(orderBy, self.__tableName) 

        # Fetch Items
        try:
            self.__fetch(orderBy, desc)
        except Exception as err:
            console.print(err, style="warning")
            return
        
        # Print Items
        self.__print()            

    # Print Items
    def __print(self):
        # Number of Items
        nItems = len(self.__items)

        # Initialize Rich Table
        table = Table(title="Country Table Query",
                      title_style="title",
                      header_style="header",
                      caption=f"{nItems} Results Fetched",
                      caption_style="caption",
                      border_style="border",
                      box=BOX_STYLE,
                      row_styles=["text", "textAlt"])

        # Add Table Columns
        table.add_column("ID", 
                         justify="left",
                         max_width=ID_NCHAR)
        
        table.add_column("Name", 
                         justify="left",
                         max_width=COUNTRY_NAME_NCHAR)
        
        table.add_column("Phone Prefix", 
                         justify="left",
                         max_width=PHONE_PREFIX_NCHAR)
        
        # Check Items
        if self.__items is None:
            console.print("Error: No Items Fetched", style="warning")
            return

        # Loop Over Items
        for item in self.__items:
            table.add_row(str(item[0]), item[1], str(item[2]))

        console.print(table)