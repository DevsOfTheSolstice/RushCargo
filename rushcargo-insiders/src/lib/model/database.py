import asyncio
import os
from pathlib import Path
import time

from dotenv import load_dotenv

from psycopg_pool import AsyncConnectionPool

from rich.console import Console

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

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class AsyncPool:
    """
    Class that Handles the Remote Database Asynchronous Connection Pool
    """

    # Private Fields
    __host = None
    __dbname = None
    __user = None
    __password = None
    __port = None
    __apool = None

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
        Remote Database Asynchronous Connection Pool Class Constructor

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

        try:
            # Get and Open Asynchronous Connection Pool
            self.__apool = AsyncConnectionPool(
                conninfo=f"host={self.__host} dbname={self.__dbname} user={self.__user} password={self.__password} port={self.__port} sslmode={'require'}",
                open=False,
            )

        except Exception as err:
            return err

    async def openPool(self):
        """
        Method to Open the Asynchronous Connection Pool
        """

        await asyncio.gather(self.__apool.open())

    async def closePool(self):
        """
        Method to Close the Asynchronous Connection Pool
        """

        await asyncio.gather(self.__apool.close())

    def connection(self):
        """
        Method to Get a Pool Connection Context Manager

        :return: Asynchronous Pool Connection Context Manager
        """

        return self.__apool.connection()

    async def getConnection(self):
        """
        Asynchronous Method to Get a Pool Connection

        :return: Asynchronous Pool Connection
        """

        conn = await asyncio.gather(self.__apool.getconn())

        return conn

    async def putConnection(self, conn):
        """
        Asynchronous Method to Put a Pool Connection

        :param conn: Asynchronous Pool Connection
        """

        await asyncio.gather(self.__apool.putconn(conn))


# Initialize Asynchronous Connection Pool
def initAsyncPool() -> tuple[AsyncPool, str, str]:
    """
    Function that Initialize Remote Database Asynchronous Connection Pool and Returns Some Environment Variables

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

    # Initialize Remote Database Asynchronous Connection Pool Object
    apool = AsyncPool(dbname, user, password, host, port)

    return apool, user, ORSApiKey
