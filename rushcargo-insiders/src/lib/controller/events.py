import asyncio
import logging

from rich.prompt import Prompt
from rich.logging import RichHandler

from .constants import RICH_LOGGER_DEBUG_MODE
from .locationsEvents import LocationsEventHandler

from ..io.arguments import getEventHandlerArguments
from ..io.constants import *

from ..model.database import AsyncPool
from ..model.database_tables import console

from ..terminal.clear import clear
from ..terminal.constants import END_MSG, PRESS_ENTER

# Get Rich Logger
if RICH_LOGGER_DEBUG_MODE:
    logging.basicConfig(
        level="NOTSET",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    log = logging.getLogger("rich")


class EventHandler:
    """
    Class that Handles All the Events
    """

    # Remote Database Asynchronous Connection Pool
    __apool = None

    # Event Handlers
    __locationsEventHandler = None

    def __init__(self, apool: AsyncPool, user: str, ORSApiKey: str):
        """
        Event Handler Class Constructor

        :param AsyncPool apool: Object of the Asynchronous Connection Pool with the Remote Database
        :param str user: Remote Database Role Name
        :param str ORSApiKey: Open Routing Service API Key
        """

        # Store Remote Database Asynchronous Connection Pool
        self.__apool = apool

        # Initialize Location Event Handler
        self.__locationsEventHandler = LocationsEventHandler(user, ORSApiKey)

    async def handler(self, argsDict: dict) -> None:
        """
        Main Handler of ``add``, ``all``, ``get``, ``mod`` and ``rm`` Commands

        :param dict argsDict: Dictionary that Contains All the Commands and its Arguments. If there's No Input by the User, returns None
        :return: Nothing
        :rtype: NoneType
        """

        # Open Remote Database Connection Pool
        await self.__apool.openPool()

        while True:
            async with self.__apool.connection() as aconn:
                try:
                    # Clear Terminal
                    clear()

                    # Check if it's a Database-related Command
                    if argsDict[CMD_TYPE] == DB:
                        # Check if it's a Locations Scheme Table
                        if argsDict[DB_SCHEME] == DB_LOCATIONS_SCHEME_CMD:
                            # Call Location Database Event Handler
                            await self.__locationsEventHandler.dbHandler(
                                aconn, argsDict[DB_ACTION], argsDict[DB_TABLE]
                            )

                    # Check if it's a Graph-related Command
                    elif argsDict[CMD_TYPE] == GRAPH:
                        # Call Location Graph Event Handler
                        await asyncio.gather(
                            self.__locationsEventHandler.graphHandler(
                                aconn, argsDict[GRAPH_TYPE], argsDict[GRAPH_LEVEL]
                            )
                        )

                    # Clear Terminal
                    clear()

                    argsDict = getEventHandlerArguments()

                    # Check if the User wants to Exit the Program
                    if argsDict == None:
                        break

                # End Program
                except KeyboardInterrupt:
                    # Roll Back
                    rollbackTask = asyncio.create_task(aconn.rollback())

                    console.print(END_MSG, style="warning")
                    await rollbackTask
                    break

                except Exception as err:
                    # Roll Back
                    rollbackTask = asyncio.create_task(aconn.rollback())

                    try:
                        console.print(err, style="warning")

                        # Press ENTER to Continue
                        Prompt.ask(PRESS_ENTER)
                        await rollbackTask

                        # Clear Terminal
                        clear()

                        argsDict = getEventHandlerArguments()

                        # Check if the User wants to Exit the Program
                        if argsDict == None:
                            break

                        continue

                    # End Program
                    except KeyboardInterrupt:
                        console.print(END_MSG, style="warning")
                        break

        # Close Remote Database Asynchronous Connection Pool
        await self.__apool.closePool()
