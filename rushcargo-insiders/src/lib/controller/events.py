import logging

from rich.prompt import Prompt
from rich.logging import RichHandler

from .locationsEvents import LocationsEventHandler

from ..io.arguments import getEventHandlerArguments
from ..io.constants import LOCATIONS_SCHEME_CMD
from ..io.validator import clear

from ..model.database import Database
from ..model.database_tables import console

from ..terminal.constants import END_MSG, PRESS_ENTER

# Get Rich Logger
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

    # Database Connection
    __c = None

    # Event Handlers
    __locationsEventHandler = None

    def __init__(self, db: Database, user: str, ORSApiKey: str):
        """
        Event Handler Class Constructor

        :param Database db: Database Object of the Current Connection with the Remote Database
        :param str user: Remote Database Role Name
        :param str ORSApiKey: Open Routing Service API Key
        """

        # Store Database Connection Cursor
        self.__c = db.getCursor()

        # Initialize Location Event Handler
        self.__locationsEventHandler = LocationsEventHandler(self.__c, user, ORSApiKey)

    def handler(self, action: str, schemeName: str, tableName: str) -> None:
        """
        Main Handler of ``add``, ``all``, ``get``, ``mod`` and ``rm`` Commands

        :param str action: Command (``add``, ``all``, ``get``, ``mod`` or ``rm``)
        :param str schemeName: Scheme Name at Remote Database
        :param str tableName: Table Name at Remote Database
        :return: Nothing
        :rtype: NoneType
        """

        while True:
            try:
                # Clear Terminal
                clear()

                # Check if it's a Locations Scheme Table
                if schemeName == LOCATIONS_SCHEME_CMD:
                    # Call Location Event Handler
                    self.__locationsEventHandler.handler(action, tableName)

                # Clear Terminal
                clear()

                arguments = getEventHandlerArguments()

                # Check if the User wants to Exit the Program
                if arguments == None:
                    break

                # Get Arguments
                action, schemeName, tableName = arguments

            # End Program
            except KeyboardInterrupt:
                console.print(END_MSG, style="warning")
                return

            except Exception as err:
                try:
                    console.print(err, style="warning")

                    # Press ENTER to Continue
                    Prompt.ask(PRESS_ENTER)

                    continue

                # End Program
                except KeyboardInterrupt:
                    console.print(END_MSG, style="warning")
                    return
