import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

from psycopg_pool import AsyncConnectionPool

from rich.console import Console

from .constants import (
    APOOL_MIN_SIZE,
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


def cancelTasks(tasks: list):
    """
    Cancel All Asynchronous Tasks from ``asyncio`` Library if there was an Error

    :param list tasks: List of Asynchronous Task from ``asyncio`` Library
    """

    for task in tasks:
        try:
            task.cancel()
        except:
            pass


# Change the Current Event Loop Policy to Work with the Asynchronous Connection Pool Class. For Windows
if os.name == "nt":
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
                min_size=APOOL_MIN_SIZE,
            )

        except Exception as err:
            return err

    async def openPool(self):
        """
        Method to Open the Asynchronous Connection Pool

        :raises Exception: Raised if Something Occurs when the Pool is Opening
        """

        # Wait for the Requested Connections
        await asyncio.gather(self.__apool.open(wait=True))

    async def closePool(self):
        """
        Method to Close the Asynchronous Connection Pool

        :raises Exception: Raised if Something Occurs when the Pool is Closing
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
        :raises Exception: Raised if Something Occurs when Getting a Connection from the Pool
        """

        aconnTask = asyncio.create_task(self.__apool.getconn())
        await asyncio.gather(aconnTask)

        return aconnTask.result()

    async def getConnections(self, number: int) -> list:
        """
        Asynchronous Method to Get Some Pool Connections

        :param int number: Number of Connections to Get
        :return: List of Asynchronous Pool Connections
        :rtype: list
        :raises Exception: Raised if Something Occurs when Getting a Connection from the Pool
        """

        # Get the Connections
        tasks = []
        for _ in range(number):
            tasks.append(asyncio.create_task(self.getConnection()))

        try:
            await asyncio.gather(*tasks)

        except Exception as err:
            cancelTasks(tasks)
            raise err

        aconns = []
        for t in tasks:
            aconns.append(t.result())

        return aconns

    async def putConnection(self, aconn):
        """
        Asynchronous Method to Put a Pool Connection

        :param aconn: Asynchronous Pool Connection
        :raises Exception: Raised if Something Occurs when Putting Back a Connection to the Pool
        """

        await asyncio.gather(self.__apool.putconn(aconn))

    async def putConnections(self, aconns: list) -> None:
        """
        Asynchronous Method to Put Some Pool Connections

        :param int aconns: List of Asynchronous Pool Connections
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised if Something Occurs when Putting Back a Connection to the Pool
        """

        # Put the Connections
        tasks = []
        for aconn in aconns:
            tasks.append(asyncio.create_task(self.putConnection(aconn)))

        try:
            await asyncio.gather(*tasks)

        except Exception as err:
            cancelTasks(tasks)
            raise err


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
