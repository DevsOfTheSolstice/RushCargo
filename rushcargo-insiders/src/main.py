import argparse
import textwrap
import sys


from lib.controller.events import EventHandler

from lib.io.constants import *
from lib.io.arguments import getEventHandlerArguments
from lib.io.validator import clear

from lib.terminal.constants import TITLE_MSG, WELCOME_MSG


# Initialize argParse Parser and Get Parser Arguments
def getParserArguments() -> tuple[str, str, str]:
    # Intialize Parser
    parser = argparse.ArgumentParser(
        prog=TITLE_MSG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(WELCOME_MSG),
    )

    # Action Argument
    parser.add_argument(
        "action", help="Table-related Action Commands", choices=ACTION_CMDS, type=str
    )

    # Table Argument
    parser.add_argument(
        "table", help="Insert to Table", choices=TABLE_ARGPARSE_CMDS, type=str
    )

    # Get Arguments
    args = parser.parse_args()

    # Get Action and Table
    action = args.action
    table = args.table

    # Get Table Group
    if table in TABLE_TERRITORY_CMDS:
        tableGroup = TABLE_TERRITORY_CMD

    elif table in TABLE_BUILDING_CMDS:
        tableGroup = TABLE_BUILDING_CMD

    return action, tableGroup, table


if __name__ == "__main__":
    if len(sys.argv) == 3:
        # Get argParser Arguments
        action, tableGroup, table = getParserArguments()

        # Initialize Event Handler
        e = EventHandler()

        # Call Main Event Handler
        e.handler(action, tableGroup, table)
    else:
        # Clear Terminal
        clear()

        # Get Event Handler Arguments
        arguments = getEventHandlerArguments()

        if arguments != None:
            # Get Arguments
            action, tableGroup, table = arguments

            # Initialize Event Handler
            e = EventHandler()

            # Call Main Event Handler
            e.handler(action, tableGroup, table)
