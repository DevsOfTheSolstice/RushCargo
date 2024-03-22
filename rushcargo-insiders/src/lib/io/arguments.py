from rich.prompt import Prompt
from rich.console import Console

from .constants import *

from ..model.constants import THEME

from ..terminal.constants import TITLE_MSG, WELCOME_MSG

# Get Console
console = Console(theme=THEME)


# Function to Get Arguments for the Main Event Handler
def getEventHandlerArguments() -> None | tuple[str, str, str]:
    # Print Rush Cargo Title Message
    console.print(TITLE_MSG, justify="center", style="title")

    # Print New Line
    console.print("\n")

    # Print Rush Cargo Welcome Messasge
    console.print(WELCOME_MSG, justify="center", style="caption")

    tableMsg = "At which Table?"

    # Ask Next Action
    action = Prompt.ask("\nWhat do you want to do?", choices=ACTION_CMDS)

    # Check if the User wants to Exit the Program
    if action == EXIT:
        return None

    # Ask for Table Group to Work with
    tableGroup = Prompt.ask("At which Table Group?", choices=TABLE_GROUP_CMDS)
    table = None

    # Ask for Table to Work with
    if tableGroup == TABLE_TERRITORY_CMD:
        table = Prompt.ask(tableMsg, choices=TABLE_TERRITORY_CMDS)

    elif tableGroup == TABLE_BUILDING_CMD:
        table = Prompt.ask(tableMsg, choices=TABLE_BUILDING_CMDS)

    return action, tableGroup, table
