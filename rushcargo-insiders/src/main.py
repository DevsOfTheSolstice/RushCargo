import argparse
import asyncio
import os
import sys
import textwrap
import logging

from lib.controller.events import EventHandler
from lib.controller.events import END_MSG

from lib.graph.constants import DATA_DIR

from lib.io.constants import *
from lib.io.arguments import getEventHandlerArguments

from lib.model.database import initAsyncPool, console

from lib.terminal.constants import TITLE_MSG, PROG_MSG
from lib.terminal.clear import clear


# Initialize argParse Parser and Get Parser Arguments
def getParserArguments() -> dict:
    """
    Function to Initialize Argument Parser from ``argparse`` Standard Library and Get the User Commands

    :return: Dictionary that Contains All the Commands and its Arguments
    :rtype: dict
    """

    # Intialize Parser
    parser = argparse.ArgumentParser(
        prog=PROG_MSG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(TITLE_MSG),
        exit_on_error=False,
    )

    # Get a Subparser for the Different Command Types
    subparsers = parser.add_subparsers(help="Command Types", dest=CMD_TYPE)

    # Database-related Actions Commands Parser
    dbParser = subparsers.add_parser(DB, help="Database-related Commands")

    # Graph-related Actions Commands Parser
    graphParser = subparsers.add_parser(GRAPH, help="Graph-related Commands")

    # Database Action Argument
    dbParser.add_argument(
        DB_ACTION,
        help="Table-related Action Commands",
        choices=DB_ACTION_CMDS,
        type=str,
    )

    # Database Table Argument
    dbParser.add_argument(
        DB_TABLE, help="Insert to Table", choices=DB_TABLE_CMDS, type=str
    )

    # Graph Type Argument
    graphParser.add_argument(
        GRAPH_TYPE, help="Graph Type", choices=GRAPH_TYPE_CMDS, type=str
    )

    # Graph Level Argument
    graphParser.add_argument(
        GRAPH_LEVEL, help="Graph Level", choices=GRAPH_LEVEL_CMDS, type=str
    )

    # Get Arguments
    args = parser.parse_args()

    argsDict = {}

    # Get the Main Command
    argsDict[CMD_TYPE] = args.cmdType

    # Get the Database-related Commands
    if argsDict[CMD_TYPE] == DB:
        # Get the Action and Table Commands
        argsDict[DB_ACTION] = args.action
        argsDict[DB_TABLE] = args.table

        # Get the Scheme
        if argsDict[DB_TABLE] in DB_LOCATIONS_SCHEME_TABLE_CMDS:
            argsDict[DB_SCHEME] = DB_LOCATIONS_SCHEME_CMD

    # Get the Graph-related Commands
    elif argsDict[CMD_TYPE] == GRAPH:
        # Get the Graph Type and Level Commands
        argsDict[GRAPH_TYPE] = args.type
        argsDict[GRAPH_LEVEL] = args.level

    return argsDict


if __name__ == "__main__":
    # Change Directory to 'rushcargo-insiders/data'
    try:
        os.chdir(DATA_DIR)

    except FileNotFoundError:
        # Create 'rushcargo-insiders/data' Directory
        cwd = os.getcwd()
        path = os.path.join(cwd, DATA_DIR)
        os.mkdir(path)

        # Change Current Working Directory
        os.chdir(DATA_DIR)

    except Exception as err:
        print(err)
        os._exit(0)

    try:
        # Arguments Dictionary
        argsDict = None

        # Get Arguments
        if len(sys.argv) > 1:
            argsDict = getParserArguments()

        else:
            # Clear Terminal
            clear()

            argsDict = getEventHandlerArguments()

            # Check Arguments
            if argsDict == None:
                os._exit(0)

        # Initialize Remote Database Asynchronous Connection Pool
        apool, user, ORSApiKey = initAsyncPool()

        # Open Remote Database Connection Pool
        asyncio.run(apool.openPool())

        # Initialize Event Handler
        e = EventHandler(apool, user, ORSApiKey)

        # Disable Loggers (there's a Logger inside the 'putconn' Method from the AsyncConnectionPool Class)
        logging.disable(logging.CRITICAL)

        # Call Main Event Handler
        e.handler(argsDict)

        # Close Remote Database Asynchronous Connection Pool
        # asyncio.run(apool.closePool())

    # End Program
    except KeyboardInterrupt:
        console.print(END_MSG, style="warning")
