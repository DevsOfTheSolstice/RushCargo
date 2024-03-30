from rich.prompt import Prompt

from .constants import *

from ..model.database import console

from ..terminal.constants import TITLE_MSG, WELCOME_MSG, ACTION_MSG, SCHEME_MSG, TABLE_MSG


def getEventHandlerArguments() -> tuple[str, str, str] | None:
    """
    Method to Get Main Event Handler Command Arguemnts

    :return: Tuple of ``action``, ``schemeName`` and ``tableName`` Commands. If there's No Input by the User, returns None
    :rtype: tuple, NoneType
    """

    # Print Rush Cargo Title and Welcome Message
    console.print(TITLE_MSG, justify="center", style="mainTitle")
    console.print(WELCOME_MSG, justify="center", style="caption")

    # Get Command
    action = Prompt.ask(ACTION_MSG, choices=ACTION_CMDS)

    # Check if the User wants to Exit the Program
    if action == EXIT:
        return None

    # Ask for the Scheme to Work with
    schemeName = Prompt.ask(SCHEME_MSG, choices=SCHEME_CMDS)
    table = None

    # Ask for the Table to Work with
    if schemeName == LOCATION_SCHEME_CMD:
        table = Prompt.ask(TABLE_MSG, choices=LOCATION_SCHEME_TABLE_CMDS)

    return action, schemeName, table
