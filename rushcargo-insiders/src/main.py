import argparse
import textwrap

from lib.model.constants import *
from lib.controller.events import *


def main():
    # Intialize Parser
    parser = argparse.ArgumentParser(
        prog="Rush Cargo Insiders",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """\
            Rush Cargo Database Tool for Project Developers
            -----------------------------------------------
            Made by: DevsOfTheSolstice
            """
        ),
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
    tableGroup = None

    # Get Table Group
    if table in TABLE_TERRITORY_CMDS:
        tableGroup = TABLE_TERRITORY_CMD

    elif table in TABLE_BUILDING_CMDS:
        tableGroup = TABLE_BUILDING_CMD

    # Initialize Event Handler
    e = EventHandler()

    # Call Main Event Handler
    e.handler(action, tableGroup, table)

    # Program End
    console.print("\nExiting...", style="warning")


if __name__ == "__main__":
    main()
