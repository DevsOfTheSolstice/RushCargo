from psycopg2 import connect, sql, extras
from io import StringIO

from lib.model.constants import *
from lib.model.exceptions import *

# Input Validator
def checkInput(input: str, isAlpha: bool = True, isDigit: bool = True, isSpecial: bool = False) -> bool:
    # Nothing to Check
    if isAlpha and isDigit and isSpecial:
      return True
    
    for i in input:
        # Check if the Given Character is an Alphabetical Character
        if isAlpha and i.isalpha():
            continue
        
        # Check if the Given Character is a Digit
        if isDigit and i.isdigit():
            continue
        
        if not isSpecial: 
          return False
            
    return True        

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
class Country:
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
            print(f"Deleted Coincidences which had: '{value}' in '{field}' Column\n")
        except Exception as err:
            print(err)

    # Insert Country to Table
    def insert(self, name: str, phonePrefix: int): 
        # Get Query
        query = sql.SQL(
                "INSERT INTO {tableName} ({name}, {phone_prefix}) VALUES (%s, %s)"
            ).format(
                tableName = sql.Identifier(self.__tableName),
                name = sql.Identifier(COUNTRY_NAME),
                phone_prefix = sql.Identifier(COUNTRY_PHONE_PREFIX))

        # Execute Query
        try:
            self.c.execute(query, [name, phonePrefix])
            print(f"Country Successfully Inserted to {self.__tableName} Table\n")
        except Exception as err:
            print(err)
        
    # Insert Multiple Countries to Table
    def insertMany(self, countries: list):
        # Get Query
        query = sql.SQL(
                "INSERT INTO {tableName} ({id}, {name}, {phone_prefix}) VALUES %s"
            ).format(
                tableName = sql.Identifier(self.__tableName),
                id = sql.Identifier(COUNTRY_ID),
                name = sql.Identifier(COUNTRY_NAME),
                phone_prefix = sql.Identifier(COUNTRY_PHONE_PREFIX))

        # Execute Query
        try:
            extras.execute_values(self.c, query.as_string(self.c), countries, page_size=100)
            print(f"Countries Successfully Inserted to {self.__tableName}\n")
        except Exception as err:
            print(err)

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
            print(f"Country {id} Successfully Updated to {self.__tableName}\n")
        except Exception as err:
            print(err)

    # Sort By Table
    def __orderBy(self, orderBy: str, desc: bool):
        if desc:
            orderBy = orderBy.concat(' DESC')

        # Get Query
        query = sql.SQL(
                    "SELECT * FROM {tableName} ORDER BY (%s)"
                ).format(
                    tableName = sql.Identifier(self.__tableName))
        
        # Execute Query
        try:
            self.c.execute(query, [orderBy])
        except Exception as err:
            print(err)
        
    # Return All Countries
    def __fetch(self, orderBy: str, desc: bool):
        try:
            self.__orderBy(orderBy, desc)
            self.__items = self.c.fetchall()
        except Exception as err:
            print(err)
            raise err

    # Print All Items from Main Table
    def printAll(self, orderBy: str = COUNTRY_ID, desc: bool = False):
        # Check orderBy
        if not self.__checkField(orderBy, True):
           raise FieldError(orderBy, self.__tableName) 

        # Fetch Items
        try:
            self.__fetch(orderBy, desc)
        except Exception as err:
            raise err
            
        msg = StringIO()

        # Print Header
        msg.write("ID".ljust(COUNTRY_NCHAR, ' ') + 
                "Name".ljust(COUNTRY_NCHAR, ' ') + 
                "Phone Prefix".ljust(COUNTRY_NCHAR, ' ') + 
                '\n')

        # Add Separator
        msg.write('-' * COUNTRY_NCHAR * 4)

        # Check Items
        if self.__items is None:
            print("Error: No Items Fetched")
            return

        # Loop Over Items
        for item in self.__items:
            msg.write('\n')

            # Append String to In-Memory Buffer with Left Alignment
            for value in item:
                try:
                    msg.write(value.ljust(COUNTRY_NCHAR, ' '))
                except:
                    msg.write(str(value).ljust(COUNTRY_NCHAR, ' '))
        msg.write('\n')

        print(msg.getvalue())