from rich.prompt import Prompt

from .constants import *

from ..model.database import console

from ..terminal.constants import (
    TITLE_MSG,
    WELCOME_MSG,
    CMD_TYPE_MSG,
    DB_ACTION_MSG,
    DB_SCHEME_MSG,
    DB_TABLE_MSG,
    GRAPH_TYPE_MSG,
    GRAPH_LEVEL_MSG,
)


def getEventHandlerArguments() -> dict | None:
    """
    Method to Get Main Event Handler Command Arguemnts

    :return: Dictionary that Contains All the Commands and its Arguments. If there's No Input by the User, returns None
    :rtype: dict, NoneType
    """

    # Arguments Dictionary
    argsDict = {}

    # Print Rush Cargo Title and Welcome Message
    console.print(TITLE_MSG, justify="center", style="mainTitle")
    console.print(WELCOME_MSG, justify="center", style="caption")

    # Get Action Type Command
    argsDict[CMD_TYPE] = Prompt.ask(CMD_TYPE_MSG, choices=CMD_TYPE_CMDS)

    # Check if the User wants to Exit the Program
    if argsDict[CMD_TYPE] == EXIT:
        return None

    # Get Database-related Commands
    if argsDict[CMD_TYPE] == DB:
        # Ask for the Action Command
        argsDict[DB_ACTION] = Prompt.ask(DB_ACTION_MSG, choices=DB_ACTION_CMDS)

        if argsDict[DB_ACTION] == EXIT:
            return None

        # Ask for the Scheme to Work with
        argsDict[DB_SCHEME] = Prompt.ask(DB_SCHEME_MSG, choices=DB_SCHEME_CMDS)

        if argsDict[DB_SCHEME] == EXIT:
            return None

        # Ask for the Table to Work with
        if argsDict[DB_SCHEME] == DB_LOCATIONS_SCHEME_CMD:
            argsDict[DB_TABLE] = Prompt.ask(
                DB_TABLE_MSG, choices=DB_LOCATIONS_SCHEME_TABLE_CMDS
            )

        if argsDict[DB_TABLE] == EXIT:
            return None

    # Get Graph-related Commands
    elif argsDict[CMD_TYPE] == GRAPH:
        # Ask for the Graph Type Command
        argsDict[GRAPH_TYPE] = Prompt.ask(GRAPH_TYPE_MSG, choices=GRAPH_TYPE_CMDS)

        if argsDict[GRAPH_TYPE] == EXIT:
            return None

        # Ask for the Level Command
        argsDict[GRAPH_LEVEL] = Prompt.ask(GRAPH_LEVEL_MSG, choices=GRAPH_LEVEL_CMDS)

        if argsDict[GRAPH_LEVEL] == EXIT:
            return None

    return argsDict
