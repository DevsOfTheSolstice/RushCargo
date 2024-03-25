from rich.prompt import Confirm
import logging
from rich.logging import RichHandler

from .constants import END_MSG
from .locationEvents import LocationEventHandler

from ..io.arguments import getEventHandlerArguments
from ..io.constants import TABLE_LOCATION_CMD
from ..io.validator import clear

from ..model.database import Database
from ..model.database_tables import console


# Get Rich Logger
logging.basicConfig(
    level="NOTSET",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
log = logging.getLogger("rich")


# Event Handler Class
class EventHandler:
    # Event Handlers
    __locationEventHandler = None

    # Initialize Event Handler
    def __init__(self, db: Database, user: str, ORSApiKey: str):
        # Initialize Location Event Handler
        self.__locationEventHandler = LocationEventHandler(db, user, ORSApiKey)

    # Main Event Handler
    def handler(self, action: str, tableGroup: str, tableName: str) -> None:
        try:
            while True:
                try:
                    # Check if it's a Location Table
                    if tableGroup == TABLE_LOCATION_CMD:
                        # Call Location Event Handler
                        self.__locationEventHandler.handler(action, tableName)

                except Exception as err:
                    console.print(err, style="warning")

                # Ask to Change Action
                if Confirm.ask("\nDo you want to Continue with this Command?"):
                    # Clear Terminal
                    clear()
                    continue

                # Clear Terminal
                clear()

                # Get Event Handler Arguments
                arguments = getEventHandlerArguments()

                # Check if the User wants to Exit the Program
                if arguments == None:
                    break

                # Get Arguments
                action, tableGroup, tableName = arguments

        except KeyboardInterrupt:
            # End Program
            console.print(END_MSG, style="warning")
            return
