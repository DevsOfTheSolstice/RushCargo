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

# Database Connection Fields
db = None
user = None
ORSApiKey = None


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
        try:
            self._conn = connect(
                f"host={host} dbname={dbname} user={user} password={password} port={port} sslmode={'require'}"
            )
            self._c = self.getCursor()

        except Exception as err:
            return err

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
def initDb() -> tuple[Database, str, str, str]:
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
    return Database(dbname, user, password, host, port), user, ORSApiKey
