import asyncio

from psycopg import sql

from rich.table import Table

from .constants import BOX_STYLE
from .database import console
from .exceptions import LenError


def noCoincidence() -> None:
    """
    Function to Print a Message when there was Nothing Fetched from a Given Query

    :return: Nothing
    :rtype: NoneType
    """

    console.print("No Results Fetched\n", style="warning")


def uniqueInserted(tableName: str, field: str, value) -> None:
    """
    Function to Print a Message when the User tries to Insert a Row which has Unique Fields that Contains Values that have been already Inserted

    :param str tableName: Table Name where the Row is being Inserted
    :param str field: Table Field Name that Raised the Constraint Error
    :param value: Value that has Already being Inserted for the Given Field
    :return: Nothing
    :rtype: NoneType
    """

    console.print(
        f"Unique '{value}' Already Inserted at '{field}' on {tableName}\n",
        style="warning",
    )


def uniqueInsertedMult(tableName: str, field: list[str], value: list) -> None:
    """
    Function to Print a Message when the User tries to Insert a Row that Contains Values which Violate UniqueConstraint of Multiple Columns

    :param str tableName: Table Name where the Row is being Inserted
    :param list fields: Table Fields Name that Raised the Constraint Error
    :param values: Values that have Already being Inserted for the Given Fields
    :return: Nothing
    :rtype: NoneType
    """

    fieldStr = ",".join(f for f in field)
    valueStr = ",".join(str(v) for v in value)

    console.print(
        f"({valueStr}) at ({fieldStr}) Violates Unique Constraint on {tableName}\n",
        style="warning",
    )


def modifiedRow(field: str, value, idField: str, idValue: int, tableName: str) -> None:
    """
    Function to Print a Message when a Row has been Successfully Modified at a Given Table

    :param value: Value Assigned to the Modified Field
    :param str field: Field Modified
    :param str idField: Table Field Used to Identify the Rows
    :param int idValue: Unique Identifier for the Given Row that was Modified
    :return: Nothing
    :rtype: NoneType
    """

    console.print(
        f"Data '{value}' Successfully Assigned to '{field}' at '{idField}' '{idValue}' in {tableName} Table\n",
        style="success",
    )


def insertedRow(name: str, tableName: str) -> None:
    """
    Function to Print a Message when a Row has been Successfully Inserted to a Table

    :param str name: Value Inserted to the Given Table
    :param str tableName: Table Name where the Row is being Inserted
    :return: Nothing
    :rtype: NoneType
    """

    console.print(
        f"{name} Successfully Inserted to {tableName} Table\n", style="success"
    )


def removeRow(tableName: str, idField: str, idValue: int) -> None:
    """
    Function to Print a Message when a Row has been Successfully Removed from a Table

    :param str tableName: Table Name where the Row is being Removed
    :param str idField: Table Field Used to Identify the Rows
    :param int idValue: Unique Identifier for the Given Row that was Removed
    :return: Nothing
    :rtype: NoneType
    """

    console.print(
        f"Row with '{idField}' '{idValue}' Successfully Removed from {tableName} Table\n",
        style="success",
    )


def getTable(tableName: str, nRows: int) -> Table:
    """
    Function that Returns a Table, from the ``rich`` Library, with Some Theme Customizations with the Aim to Print Pretty SQL Tables
    :param str tableName: Table Name to Add to the Rich Table Header
    :param list nRows: Number of Rows Fetched from the Given Query
    :return: Rich Table
    :rtype: Table
    """

    # Initialize Rich Table
    return Table(
        title=f"{tableName} Table Query",
        title_style="title",
        header_style="header",
        caption=f"{nRows} Results Fetched",
        caption_style="caption",
        border_style="border",
        box=BOX_STYLE,
        row_styles=["text", "textAlt"],
    )


class BaseTable:
    """
    Base Remote Table Class
    """

    # Database Connection
    _items = None

    # Scheme, Table and Table PK Name
    _schemeName = None
    _tableName = None
    _tablePKName = None

    def __init__(self, tableName: str, tablePKName: str, schemeName: str = None):
        """
        Base Remote Table Class Constructor

        :param str tableName: Table Name to Initialize
        :param str tablePKName: Table Primary Key Field Name
        :param str schemeName: Scheme Name where the Table is Located. Default is ``None``
        """

        # Store Scheme (if It inside One), Table and Primary Key Column Names
        self._schemeName = schemeName
        self._tableName = tableName
        self._tablePKName = tablePKName

    def __getQuery(self, field: str, orderBy: str = None):
        """
        Method to Get the Query to Select Some Table Rows based on a Given Field-Value Pair to Compare

        :param str field: Table Field Name to be Compared
        :param str orderBy: Table Field that will be Used to Sort it. Default is ``None``
        :return: SQL Query
        :rtype: Composed
        """

        # Check if there's Some Sorting to be Applied
        if orderBy == None:
            return sql.SQL(
                "SELECT * FROM {schemeName}.{tableName} WHERE {field} = (%s)"
            ).format(
                schemeName=sql.Identifier(self._schemeName),
                tableName=sql.Identifier(self._tableName),
                field=sql.Identifier(field),
            )

        return sql.SQL(
            "SELECT * FROM {schemeName}.{tableName} WHERE {field} = (%s) ORDER BY {orderBy}"
        ).format(
            schemeName=sql.Identifier(self._schemeName),
            tableName=sql.Identifier(self._tableName),
            field=sql.Identifier(field),
            orderBy=sql.Identifier(orderBy),
        )

    def __getAndQuery(self, field1: str, field2: str, orderBy: str = None):
        """
        Method to Get the Query to Select Some Table Rows based on Two Given Field-Value Pair to Compare

        :param str field1: First Table Field Name to be Compared
        :param str field2: Second Table Field Name to be Compared
        :param str orderBy: Table Field that will be Used to Sort it. Default is ``None``
        :return: SQL Query
        :rtype: Composed
        """
        # Check if there's Some Sorting to be Applied
        if orderBy == None:
            return sql.SQL(
                "SELECT * FROM {schemeName}.{tableName} WHERE {field1} = (%s) AND {field2} = (%s)"
            ).format(
                schemeName=sql.Identifier(self._schemeName),
                tableName=sql.Identifier(self._tableName),
                field1=sql.Identifier(field1),
                field2=sql.Identifier(field2),
            )

        return sql.SQL(
            "SELECT * FROM {schemeName}.{tableName} WHERE {field1} = (%s) AND {field2} = (%s) ORDER BY {orderBy}"
        ).format(
            schemeName=sql.Identifier(self._schemeName),
            tableName=sql.Identifier(self._tableName),
            field1=sql.Identifier(field1),
            field2=sql.Identifier(field2),
            orderBy=sql.Identifier(orderBy),
        )

    def __orderByQuery(self, orderBy: str, desc: bool):
        """
        Method to Get the Query to Sort the Table Rows in Asceding/Descending Order for a Given Field

        :param str orderBy: Table Field to Sort
        :param bool desc: Specifies whether to Sort the Rows in Ascending or Descending Order
        :return: SQL Query
        :rtype: Composed
        """

        # Get Query to Sort the Rows in Ascending Order
        if not desc:
            return sql.SQL(
                "SELECT * FROM {schemeName}.{tableName} ORDER BY {order}"
            ).format(
                schemeName=sql.Identifier(self._schemeName),
                tableName=sql.Identifier(self._tableName),
                order=sql.Identifier(orderBy),
            )

        # Get Query to Sort the Rows in Descending Order
        return sql.SQL(
            "SELECT * FROM {schemeName}.{tableName} ORDER BY {order} DESC"
        ).format(
            schemeName=sql.Identifier(self._schemeName),
            tableName=sql.Identifier(self._tableName),
            order=sql.Identifier(orderBy),
        )

    def __modifyQuery(self, compareField: str, modField: str) -> str:
        """
        Method to Get the Query to Modify a Row with a Given Value at a Given Field

        :param str compareField: Field to be Compared
        :param str modField: Field to Modify
        :return: SQL Query
        :rtype: Composed
        """

        return sql.SQL(
            "UPDATE {schemeName}.{tableName} SET {modField} = (%s) WHERE {compareField} = (%s)"
        ).format(
            schemeName=sql.Identifier(self._schemeName),
            tableName=sql.Identifier(self._tableName),
            compareField=sql.Identifier(compareField),
            modField=sql.Identifier(modField),
        )

    def __removeQuery(self, field: str):
        """
        Method to Get the Query to Remove a Row with a Given Value at a Given Field

        :param str field: Field to be Compared
        :return: SQL Query
        :rtype: Composed
        """

        return sql.SQL(
            "DELETE FROM {schemeName}.{tableName} WHERE {field} = (%s)"
        ).format(
            schemeName=sql.Identifier(self._schemeName),
            tableName=sql.Identifier(self._tableName),
            field=sql.Identifier(field),
        )

    async def _modify(self, acursor, idValue: int, field: str, value) -> None:
        """
        Asynchronous Method to Modify a Row Field Value with a Given Unique Identifier

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param int idValue: Row Unique Identifier
        :param str field: Field to be Modified
        :param value: Value to be Assigned
        :return:Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        idField = self._tablePKName

        # Get Query to Modify the Given Row
        query = self.__modifyQuery(idField, field)

        # Execute the Query and Print a Success Message
        await asyncio.gather(acursor.execute(query, [value, idValue]))
        modifiedRow(field, value, idField, idValue, self._tableName)

    async def _get(self, acursor, field: str, value, orderBy: str = None) -> None:
        """
        Asynchronous Method to Check whether the Table Contains at least One Row with a Given Field-Value Pair

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param str field: Field to be Compared
        :param value: Value to be Compared
        :param str orderBy: Table Field that will be Used to Sort it. Default is ``None``
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        query = self.__getQuery(field, orderBy)

        # Execute the Query and Fetch the Items
        await asyncio.gather(acursor.execute(query, [value]))
        fetchTask = asyncio.create_task(acursor.fetchall())
        await asyncio.gather(fetchTask)
        self._items = fetchTask.result()

    async def _getMult(
        self, acursor, fields: list[str], values: list, orderBy: str = None
    ) -> None:
        """
        Method to Check whether the Table Contains at least One Row with Some Given Field-Value Pairs

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param list fields: Fields to be Compared
        :param list values: Values to be Compared
        :param str orderBy: Table Field that will be Used to Sort it. Default is ``None``
        :return: Nothing
        :rtype: NoneType
        :raises LenError: Raised if ``fields`` and ``values`` have Different Lists Length
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Lists MUST have the Same Length
        length = len(fields)

        if length != len(values):
            raise LenError()

        # Check the Number of WHERE Conditions
        if length > 2:
            console.print("Query hasn't been Implemented", style="warning")
            return

        # Get Query for Two Conditions and Execute it
        elif length == 2:
            twoCondQuery = self.__getAndQuery(fields[0], fields[1], orderBy)
            await asyncio.gather(acursor.execute(twoCondQuery, [values[0], values[1]]))

        # Query for One Condition. Method Implemented
        elif length == 1:
            await asyncio.gather(self._get(acursor, fields[0], values[0], orderBy))
            return

        # Fetch the Items
        fetchTask = asyncio.create_task(acursor.fetchall())
        await asyncio.gather(fetchTask)
        self._items = fetchTask.result()

    async def _all(self, acursor, orderBy: str, desc: bool) -> None:
        """
        Asynchronoues Method to Print the Table Rows Sorted in Asceding/Descending Order for a Given Field

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param str orderBy: Table Field to Sort
        :param bool desc: Specifies whether to Sort the Rows in Ascending or Descending Order
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Query To Sort the Table Rows
        query = self.__orderByQuery(orderBy, desc)

        # Execute the Query and Fetch the Items
        await asyncio.gather(acursor.execute(query))
        fetchTask = asyncio.create_task(acursor.fetchall())
        await asyncio.gather(fetchTask)
        self._items = fetchTask.result()

    async def _remove(self, acursor, idValue: int) -> None:
        """
        Method to Remove a Row with a Given Unique Identifier

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param int idValue: Row Unique Identifier
        :return:Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        idField = self._tablePKName

        # Get Query to Remove the Given Row
        query = self.__removeQuery(idField)

        # Execute the Query and Print a Success Message
        await asyncio.gather(acursor.execute(query, [idValue]))
        removeRow(self._tableName, idField, idValue)


class SpecializationTable:
    """
    Specialization Remote Table Class
    """

    # Database Connection
    _items = None

    # Specialization and Specialization's Parent Scheme, Table and Table PK Name
    _tableName = None
    _parentTableName = None
    _tablePKFKName = None
    _parentTablePKName = None
    _schemeName = None
    _parentSchemeName = None

    # Constructor
    def __init__(
        self,
        tableName: str,
        parentTableName: str,
        tablePKFKName: str,
        parentTablePKName: str,
        schemeName: str = None,
        parentSchemeName: str = None,
    ):
        """
        Specialization Table Remote Class Constructor

        :param str tableName: Table Name to Initialize
        :param str parentTableName: Parent Table Name to Initialize
        :param str tablePKFKName: Table Primary Key Foreign Key Field Name
        :param str parentTablePKName: Parent Table Primary Key Field Name
        :param str schemeName: Scheme Name where the Table is Located. Default is ``None``
        :param str parentSchemeName: Scheme Name where the Parent Table is Located. Default is ``None``
        :param Cursor remoteCursor: Remote Database Connection Cursor
        """

        # Store Scheme (if It inside One), Table and Primary Key Column Names
        self._tableName = tableName
        self._parentTableName = parentTableName
        self._tablePKFKName = tablePKFKName
        self._parentTablePKName = parentTablePKName
        self._schemeName = schemeName
        self._parentSchemeName = parentSchemeName

    def __getTableQuery(self, field: str, orderBy: str = None):
        """
        Method to Get the Query to Select Some Table Rows based on a Given Field-Value Pair to Compare at the Main Table

        :param str field: Table Field Name to be Compared
        :param str orderBy: Table Field that will be Used to Sort it. Default is ``None``
        :return: SQL Query
        :rtype: Composed
        """

        # Check if there's Some Sorting to be Applied
        if orderBy == None:
            return sql.SQL(
                "SELECT * FROM {schemeName}.{tableName} AS child INNER JOIN {schemeName}.{parentTableName} AS parent ON child.{tablePKFKName} = parent.{parentTablePKName} WHERE {field} = (%s)"
            ).format(
                schemeName=sql.Identifier(self._schemeName),
                tableName=sql.Identifier(self._tableName),
                parentTableName=sql.Identifier(self._parentTableName),
                tablePKFKName=sql.Identifier(self._tablePKFKName),
                parentTablePKName=sql.Identifier(self._parentTablePKName),
                field=sql.Identifier(field),
            )

        return sql.SQL(
            "SELECT * FROM {schemeName}.{tableName} AS child INNER JOIN {schemeName}.{parentTableName} AS parent ON child.{tablePKFKName} = parent.{parentTablePKName} WHERE {field} = (%s) ORDER BY {orderBy}"
        ).format(
            schemeName=sql.Identifier(self._schemeName),
            tableName=sql.Identifier(self._tableName),
            parentTableName=sql.Identifier(self._parentTableName),
            tablePKFKName=sql.Identifier(self._tablePKFKName),
            parentTablePKName=sql.Identifier(self._parentTablePKName),
            field=sql.Identifier(field),
            orderBy=sql.Identifier(orderBy),
        )

    def __getParentTableQuery(self, field: str, orderBy: str = None):
        """
        Method to Get the Query to Select Some Table Rows based on a Given Field-Value Pair to Compare at the Parent Table

        :param str field: Parent Table Field Name to be Compared
        :param str orderBy: Table Field that will be Used to Sort it. Default is ``None``
        :return: SQL Query
        :rtype: Composed
        """

        # Check if there's Some Sorting to be Applied
        if orderBy == None:
            return sql.SQL(
                "SELECT * FROM {schemeName}.{parentTableName} WHERE {field} = (%s)"
            ).format(
                schemeName=sql.Identifier(self._schemeName),
                parentTableName=sql.Identifier(self._parentTableName),
                field=sql.Identifier(field),
            )

        return sql.SQL(
            "SELECT * FROM {schemeName}.{parentTableName} WHERE {field} = (%s) ORDER BY {orderBy}"
        ).format(
            schemeName=sql.Identifier(self._schemeName),
            parentTableName=sql.Identifier(self._parentTableName),
            field=sql.Identifier(field),
            orderBy=sql.Identifier(orderBy),
        )

    def __getTableAndQuery(self, field1: str, field2: str, orderBy: str = None):
        """
        Method to Get the Query to Select Some Table Rows based on Two Given Field-Value Pair to Compare at the Main Table

        :param str field1: First Table Field Name to be Compared
        :param str field2: Second Table Field Name to be Compared
        :param str orderBy: Table Field that will be Used to Sort it. Default is ``None``
        :return: SQL Query
        :rtype: Composed
        """

        # Check if there's Some Sorting to be Applied
        if orderBy == None:
            return sql.SQL(
                "SELECT * FROM {schemeName}.{tableName} AS child INNER JOIN {schemeName}.{parentTableName} AS parent ON child.{tablePKFKName} = parent.{parentTablePKName} WHERE {field1} = (%s) AND {field2} = (%s)"
            ).format(
                schemeName=sql.Identifier(self._schemeName),
                tableName=sql.Identifier(self._tableName),
                parentTableName=sql.Identifier(self._parentTableName),
                tablePKFKName=sql.Identifier(self._tablePKFKName),
                parentTablePKName=sql.Identifier(self._parentTablePKName),
                field1=sql.Identifier(field1),
                field2=sql.Identifier(field2),
            )

        return sql.SQL(
            "SELECT * FROM {schemeName}.{tableName} AS child INNER JOIN {schemeName}.{parentTableName} AS parent ON child.{tablePKFKName} = parent.{parentTablePKName} WHERE {field1} = (%s) AND {field2} = (%s) ORDER BY {orderBy}"
        ).format(
            schemeName=sql.Identifier(self._schemeName),
            tableName=sql.Identifier(self._tableName),
            parentTableName=sql.Identifier(self._parentTableName),
            tablePKFKName=sql.Identifier(self._tablePKFKName),
            parentTablePKName=sql.Identifier(self._parentTablePKName),
            field1=sql.Identifier(field1),
            field2=sql.Identifier(field2),
            orderBy=sql.Identifier(orderBy),
        )

    def __getParentTableAndQuery(self, field1: str, field2: str, orderBy: str = None):
        """
        Method to Get the Query to Select Some Table Rows based on Two Given Field-Value Pair to Compare at the Parent Table

        :param str field1: First Parent Table Field Name to be Compared
        :param str field2: Second Parent Table Field Name to be Compared
        :param str orderBy: Table Field that will be Used to Sort it. Default is ``None``
        :return: SQL Query
        :rtype: Composed
        """

        # Check if there's Some Sorting to be Applied
        if orderBy == None:
            return sql.SQL(
                "SELECT * FROM {schemeName}.{parentTableName} WHERE {field1} = (%s) AND {field2} = (%s)"
            ).format(
                schemeName=sql.Identifier(self._schemeName),
                parentTableName=sql.Identifier(self._parentTableName),
                field1=sql.Identifier(field1),
                field2=sql.Identifier(field2),
            )

        return sql.SQL(
            "SELECT * FROM {schemeName}.{parentTableName} WHERE {field1} = (%s) AND {field2} = (%s) ORDER BY {orderBy}"
        ).format(
            schemeName=sql.Identifier(self._schemeName),
            parentTableName=sql.Identifier(self._parentTableName),
            field1=sql.Identifier(field1),
            field2=sql.Identifier(field2),
            orderBy=sql.Identifier(orderBy),
        )

    def __orderByQuery(self, orderBy: str, desc: bool):
        """
        Method to Get the Query to Sort the Table Rows in Asceding/Descending Order for a Given Field

        :param str orderBy: Table Field to Sort
        :param bool desc: Specifies whether to Sort the Rows in Ascending or Descending Order
        :return: SQL Query
        :rtype: Composed
        """

        # Get Query to Sort the Rows in Ascending Order
        if not desc:
            return sql.SQL(
                "SELECT * FROM {schemeName}.{tableName} AS child INNER JOIN {schemeName}.{parentTableName} AS parent ON child.{tablePKFKName} = parent.{parentTablePKName} ORDER BY {order}"
            ).format(
                schemeName=sql.Identifier(self._schemeName),
                tableName=sql.Identifier(self._tableName),
                parentTableName=sql.Identifier(self._parentTableName),
                tablePKFKName=sql.Identifier(self._tablePKFKName),
                parentTablePKName=sql.Identifier(self._parentTablePKName),
                order=sql.Identifier(orderBy),
            )

        # Get Query to Sort the Rows in Descending Order
        return sql.SQL(
            "SELECT * FROM {schemeName}.{tableName} AS child INNER JOIN {schemeName}.{parentTableName} AS parent ON child.{tablePKFKName} =parent.{parentTablePKName} ORDER BY {order} DESC"
        ).format(
            schemeName=sql.Identifier(self._schemeName),
            tableName=sql.Identifier(self._tableName),
            parentTableName=sql.Identifier(self._parentTableName),
            tablePKFKName=sql.Identifier(self._tablePKFKName),
            parentTablePKName=sql.Identifier(self._parentTablePKName),
            order=sql.Identifier(orderBy),
        )

    def __modifyQuery(self, tableName: str, compareField: str, modField: str):
        """
        Method to Modify a Row Field Value with a Given Unique Identifier at a Given Table

        :param str tableName: Table Name to Modify
        :param str compareField: Field to be Compared
        :param str modField: Field to Modify
        :return: SQL Query
        :rtype: Composed
        """

        return sql.SQL(
            "UPDATE {schemeName}.{tableName} SET {modField} = (%s) WHERE {compareField} = (%s)"
        ).format(
            schemeName=sql.Identifier(self._schemeName),
            tableName=sql.Identifier(tableName),
            modField=sql.Identifier(modField),
            compareField=sql.Identifier(compareField),
        )

    def __removeQuery(self, tableName: str, field: str):
        """
        Method to Get the Query to Remove a Row with a Given Value at a Given Field and Table

        :param str tableName: Table that Contains the Row/s to be Removed
        :param str field: Field to be Compared
        :return: SQL Query
        :rtype: Composed
        """

        return sql.SQL(
            "DELETE FROM {schemeName}.{tableName} WHERE {field} = (%s)"
        ).format(tableName=tableName, field=sql.Identifier(field))

    async def __modify(
        self, acursor, parentTable: bool, idValue: int, field: str, value
    ) -> None:
        """
        Asynchronous Method to Modify a Row Field Value with a Given Unique Identifier at a Given Table

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param bool parentTable: ``False`` if the User wants to Modify the Specialization Table. Otherwise, ``True``
        :param int idValue: Row Unique Identifier
        :param str field: Field to be Modified
        :param value: Value to be Assigned
        :return:Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        idField = None
        tableName = None

        # Check if the User wants to Modify the Row from the Parent Table
        if parentTable:
            idField = self._parentTablePKName
            tableName = self._parentTableName

        else:
            idField = self._tablePKFKName
            tableName = self._tableName

        # Get Query to Modify the Given Row
        query = self.__modifyQuery(tableName, idField, field)

        # Execute the Query and Print a Success Message
        await asyncio.gather(acursor.execute(query, [value, idValue]))
        modifiedRow(field, value, idField, idValue, tableName)

    async def _modifyTable(self, acursor, idValue: int, field: str, value) -> None:
        """
        Asynchrnous Method to Modify a Row Field Value with a Given Unique Identifier from the Specialization Table

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param int idValue: Row Unique Identifier
        :param str field: Field to be Modified
        :param value: Value to be Assigned
        :return:Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        await asyncio.gather(self.__modify(acursor, False, idValue, field, value))

    async def _modifyParentTable(
        self, acursor, idValue: int, field: str, value
    ) -> None:
        """
        Asynchronous Method to Modify a Row Field Value with a Given Unique Identifier from the Specialization's Parent Table

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param int idValue: Row Unique Identifier
        :param str field: Field to be Modified
        :param value: Value to be Assigned
        :return:Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        await asyncio.gather(self.__modify(acursor, True, idValue, field, value))

    async def __get(
        self, acursor, parentTable: bool, field: str, value, orderBy: str = None
    ) -> None:
        """
        Asynchronous Method to Check whether the Table Contains at least One Row with a Given Field-Value Pair at a Given Table

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param bool parentTable: ``False`` if the User wants to Compare the Specialization Table. Otherwise,``True``
        :param str field: Field to be Compared
        :param value: Value to be Compared
        :param str orderBy: Table Field that will be Used to Sort it. Default is ``None``
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Check if the User wants to Get the Row from the Parent Table and Execute the Query
        if parentTable:
            getParentQuery = self.__getParentTableQuery(field, orderBy)
            await asyncio.gather(acursor.execute(getParentQuery, [value]))

        else:
            getSpecQuery = self.__getTableQuery(field, orderBy)
            await asyncio.gather(acursor.execute(getSpecQuery, [value]))

        # Fetch the Items
        fetchTask = asyncio.create_task(acursor.fetchall())
        await asyncio.gather(fetchTask)
        self._items = fetchTask.result()

    async def _getTable(self, acursor, field: str, value, orderBy: str = None) -> None:
        """
        Asynchronous Method to Check whether the Table Contains at least One Row with a Given Field-Value Pair at the Specialization Table

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param str field: Field to be Compared
        :param value: Value to be Compared
        :param str orderBy: Table Field that will be Used to Sort it. Default is ``None``
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        await asyncio.gather(self.__get(acursor, False, field, value, orderBy))

    async def _getParentTable(self, acursor, field: str, value, orderBy=None) -> None:
        """
        Asynchronous Method to Check whether the Table Contains at least One Row with a Given Field-Value Pair at the Specialization's Parent Table

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param str field: Field to be Compared
        :param value: Value to be Compared
        :param str orderBy: Table Field that will be Used to Sort it. Default is ``None``
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        await asyncio.gather(self.__get(True, field, value))

    async def __getMult(
        self,
        acursor,
        parentTable: bool,
        fields: list[str],
        values: list,
        orderBy: str = None,
    ) -> None:
        """
        Asynchronous Method to Check whether the Table Contains at least One Row with Some Given Field-Value Pairs

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param bool parentTable: ``False`` if the User wants to Compare the Specialization Table. Otherwise,``True``
        :param list fields: Fields to be Compared
        :param list values: Values to be Compared
        :param str orderBy: Table Field that will be Used to Sort it. Default is ``None``
        :return: Nothing
        :rtype: NoneType
        :raises LenError: Raised if ``fields`` and ``values`` have Different Lists Length
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Lists MUST have the Same Length
        length = len(fields)

        if length != len(values):
            raise LenError()

        # Check the Number of WHERE Conditions
        if length > 2:
            console.print("Query hasn't been Implemented", style="warning")
            return

        # Check if the User wants to Compare the Specialization's Parent Table
        if parentTable:
            # Get Query for Specialization's Parent Table with Two Conditions and Execute it
            if length == 2:
                twoCondQuery = self.__getParentTableAndQuery(
                    fields[0], fields[1], orderBy
                )
                await asyncio.gather(
                    acursor.execute(twoCondQuery, [values[0], values[1]])
                )

            # Query for One Condition. Method Implemented
            elif length == 1:
                getTask = asyncio.create_task(
                    self._getParentTable(acursor, fields[0], values[0], orderBy)
                )
                await asyncio.gather(getTask)
                return getTask.result()

        else:
            # Get Query for Specialization Table with Two Conditions and Execute it
            if length == 2:
                twoCondQuery = self.__getTableAndQuery(fields[0], fields[1], orderBy)
                await asyncio.gather(
                    acursor.execute(twoCondQuery, [values[0], values[1]])
                )

            # Query for One Condition. Method Implemented
            elif length == 1:
                getTask = asyncio.create_task(
                    self._getTable(acursor, fields[0], values[0], orderBy)
                )
                await asyncio.gather(getTask)
                return getTask.result

        # Fetch the Items
        fetchTask = asyncio.create_task(acursor.fetchall())
        await asyncio.gather(fetchTask)
        self._items = fetchTask.result()

    async def _getMultTable(
        self, acursor, fields: list[str], values: list, orderBy: str = None
    ) -> None:
        """
        Asynchronous Method to Check whether the Table Contains at least One Row with Some Given Field-Value Pairs at the Specialization Table

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param list fields: Fields to be Compared
        :param list values: Values to be Compared
        :param str orderBy: Table Field that will be Used to Sort it. Default is ``None``
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        await asyncio.gather(self.__getMult(acursor, False, fields, values, orderBy))

    async def _getMultParentTable(
        self, acursor, fields: list[str], values: list, orderBy: str = None
    ) -> None:
        """
        Asynchronous Method to Check whether the Table Contains at least One Row with Some Given Field-Value Pairs at the Specialization's Parent Table

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param list fields: Fields to be Compared
        :param list values: Values to be Compared
        :param str orderBy: Table Field that will be Used to Sort it. Default is ``None``
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        await asyncio.gather(self.__getMult(acursor, True, fields, values, orderBy))

    async def _all(self, acursor, orderBy: str, desc: bool) -> None:
        """
        Asynchronous Method to Print the Table Rows Sorted in Asceding/Descending Order for a Given Field at the Specialization Table

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param str orderBy: Table Field to Sort
        :param bool desc: Specifies whether to Sort the Rows in Ascending or Descending Order
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Query to Sort Items from the Specialization Table
        query = self.__orderByQuery(orderBy, desc)

        # Execute the Query and Fecth Items
        await asyncio.gather(acursor.execute(query))
        getTask = asyncio.create_task(acursor.fetchall())
        await asyncio.gather(getTask)
        self._items = getTask.result()

    async def _remove(self, acursor, idValue: int) -> None:
        """
        Asynchronous Method to Remove a Row with a Given Unique Identifier from the Specialization and its Parent Table

        :param acursor: Cursor from the Asynchronous Pool Connection with the Remote Database
        :param int idValue: Row Unique Identifier
        :return:Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Specialization and Specialization's Parent Table Name and ID Field
        parentIdField = self._parentTablePKName
        parentTableName = self._parentTableName
        idField = self._tablePKFKName
        tableName = self._tableName

        # Get Query to Remove Row from the Specialization Table
        tableQuery = self.__removeQuery(self._tableName, idField)

        # Get Query to Remove Row from the Specialization's Parent Table
        parentTableQuery = self.__removeQuery(self._parentTableName, parentIdField)

        # Remove Row from Specialization Table
        await asyncio.gather(acursor.execute(tableQuery, [idValue]))
        removeRow(tableName, idField, idValue)

        # Remove Row from Specialization's Parent Table
        await asyncio.gather(acursor.execute(parentTableQuery, [idValue]))
        removeRow(parentTableName, parentIdField, idValue)
