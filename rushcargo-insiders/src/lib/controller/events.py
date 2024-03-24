from rich.prompt import Confirm
import logging
from rich.logging import RichHandler

from .territoryEvents import territoryEventHandler
from .buildingEvents import buildingEventHandler

from ..io.arguments import getEventHandlerArguments
from ..io.constants import (
    TABLE_TERRITORY_CMD,
    TABLE_BUILDING_CMD,
)
from ..io.validator import clear

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
    # Main Event Handler
    def handler(self, action: str, tableGroup: str, tableName: str) -> None:
        try:
            while True:
                try:
                    # Check if it's a Territory Table
                    if tableGroup == TABLE_TERRITORY_CMD:
                        # Call Territory Event Handler
                        territoryEventHandler.handler(action, tableName)

                    # Check if it's a Building Table
                    elif tableGroup == TABLE_BUILDING_CMD:
                        # Call Building Event Handler
                        buildingEventHandler.handler(action, tableName)

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
            console.print("\nExiting...", style="warning")
            return
