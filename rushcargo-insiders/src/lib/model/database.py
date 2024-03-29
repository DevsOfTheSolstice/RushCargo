from psycopg import connect
from rich.console import Console
from pathlib import Path
import os
from dotenv import load_dotenv

from .constants import (
    THEME,
    ENV_HOST,
    ENV_PORT,
    ENV_DBNAME,
    ENV_USER,
    ENV_PASSWORD,
    ENV_ORS_API_KEY,
)

# Set Custom Theme
console = Console(theme=THEME)


class Database:
    """
    Class that Handles the Remote Database Connection
    """

    # Private Fields
    __host = None
    __dbname = None
    __user = None
    __password = None
    __port = None
    __conn = None
    __c = None

    # Constructor
    def __init__(
        self,
        dbname: str,
        user: str,
        password: str,
        host: str,
        port: int = 5432,
    ):
        """
        Remote Database Connection Class Constructor

        :param str dbname: Remote Database Name
        :param str user: Remote Database Role Name
        :param str password: Role Name Password
        :param str host: URL where the Database is being Hosted
        :param int port: Database Connection Port Number. Default is ``5432``
        """

        # Store Database Connection Information
        self.__host = host
        self.__dbname = dbname
        self.__user = user
        self.__password = password
        self.__port = port

        # Connect to the Remote Database
        try:
            self.__conn = connect(
                f"host={self.__host} dbname={self.__dbname} user={self.__user} password={self.__password} port={self.__port} sslmode={'require'}"
            )
            self.__c = self.getCursor()

        except Exception as err:
            return err

    def __del__(self):
        """
        Remote Database Connection Class Destructor
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


# Initialize Database Connection
def initdb() -> tuple[Database, str, str]:
    """
    Function that Initialize Remote Database Connection and Returns Some Environment Variables

    :return: Tuple of Database Object, and the ``ENV_USER`` and ``ENV_ORS_API_KEY`` Environment Varibles
    :rtype: tuple
    """

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
        host = os.getenv(ENV_HOST)
        port = os.getenv(ENV_PORT)
        dbname = os.getenv(ENV_DBNAME)
        user = os.getenv(ENV_USER)
        password = os.getenv(ENV_PASSWORD)
        ORSApiKey = os.getenv(ENV_ORS_API_KEY)

    except Exception as err:
        console.print(err, style="warning")

    # Initialize Database Object
    db = Database(dbname, user, password, host, port)

    return db, user, ORSApiKey
