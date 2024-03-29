from rich.prompt import Prompt

from .constants import *

from ..model.database import console

from ..terminal.constants import TITLE_MSG, WELCOME_MSG, TABLE_MSG


def getEventHandlerArguments() -> tuple[str, str, str] | None:
    """
    Method to Get Main Event Handler Command Arguemnts

    :return: Tuple of 'action', 'tableGroup' and 'tableName' Commands. If there's No Input by the User, returns None
    :rtype: tuple, NoneType
    """

    # Print Rush Cargo Title and Welcome Message
    console.print(TITLE_MSG, justify="center", style="title")
    console.print(WELCOME_MSG, justify="center", style="caption")

    # Get Command
    action = Prompt.ask("\nWhat do you want to do?", choices=ACTION_CMDS)

    # Check if the User wants to Exit the Program
    if action == EXIT:
        return None

    # Ask for the Table Group to Work with
    tableGroup = Prompt.ask("At which Table Group?", choices=TABLE_GROUP_CMDS)
    table = None

    # Ask for the Table to Work with
    if tableGroup == TABLE_LOCATION_CMD:
        table = Prompt.ask(TABLE_MSG, choices=TABLE_LOCATION_CMDS)

    return action, tableGroup, table
