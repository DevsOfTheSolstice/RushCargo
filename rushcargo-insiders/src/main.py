import argparse
import textwrap
import sys

from lib.controller.events import EventHandler
from lib.controller.events import END_MSG

from lib.io.constants import *
from lib.io.arguments import getEventHandlerArguments
from lib.io.validator import clear

from lib.model.database import initdb, console

from lib.terminal.constants import TITLE_MSG, WELCOME_MSG


# Initialize argParse Parser and Get Parser Arguments
def getParserArguments() -> tuple[str, str, str]:
    """
    Function to Initialize Argument Parser from ``argparse`` Standard Library and Get the User Commands

    :return: ``action``, ``scheme`` and ``table`` Commands
    :rtype: tuple
    """

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

    # Get Action and Table Command
    action = args.action
    table = args.table

    # Get Scheme
    if table in LOCATIONS_SCHEME_TABLE_CMDS:
        scheme = LOCATIONS_SCHEME_CMD

    return action, scheme, table


if __name__ == "__main__":
    if len(sys.argv) == 3:
        # Get argParser Arguments
        action, scheme, table = getParserArguments()

        # Initialize Database Connection
        db, user, ORSApiKey = initdb()

        # Initialize Event Handler
        e = EventHandler(db, user, ORSApiKey)

        # Call Main Event Handler
        e.handler(action, scheme, table)

    else:
        # Clear Terminal
        clear()

        try:
            # Get Event Handler Arguments
            arguments = getEventHandlerArguments()

            # Check Arguments
            if arguments != None:
                action, scheme, table = arguments

                # Initialize Database Connection
                db, user, ORSApiKey = initdb()

                # Initialize Event Handler
                e = EventHandler(db, user, ORSApiKey)

                # Call Main Event Handler
                e.handler(action, scheme, table)

        # End Program
        except KeyboardInterrupt:
            console.print(END_MSG, style="warning")
