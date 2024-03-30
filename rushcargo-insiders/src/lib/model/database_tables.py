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
    _c = None
    _items = None

    # Scheme, Table, Table PK and Scheme + Table Name
    _schemeName = None
    _tableName = None
    _tablePKName = None
    _fullTableName = None  # (schemeName.tableName)

    def __init__(
        self, tableName: str, tablePKName: str, remoteCursor, schemeName: str = None
    ):
        """
        Base Remote Table Class Constructor

        :param str tableName: Table Name to Initialize
        :param str tablePKName: Table Primary Key Field Name
        :param str schemeName: Scheme Name where the Table is Located. Default is ```None``
        :param Cursor remoteCursor: Remote Database Connection Cursor
        """

        # Store Scheme (if It inside One), Table and Primary Key Column Names
        self._schemeName = schemeName
        self._tableName = tableName
        self._tablePKName = tablePKName

        # Set Full Table Name
        if schemeName == None:
            self._fullTableName = sql.Identifier(self._tableName)

        else:
            self._fullTableName = sql.SQL(".").join(
                [sql.Identifier(self._schemeName), sql.Identifier(self._tableName)]
            )

        # Store Database Connection Cursor
        self._c = remoteCursor

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
            return sql.SQL("SELECT * FROM {fullTableName} WHERE {field} = (%s)").format(
                fullTableName=self._fullTableName,
                field=sql.Identifier(field),
            )

        return sql.SQL(
            "SELECT * FROM {fullTableName} WHERE {field} = (%s) ORDER BY {orderBy}"
        ).format(
            fullTableName=self._fullTableName,
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
                "SELECT * FROM {fullTableName} WHERE {field1} = (%s) AND {field2} = (%s)"
            ).format(
                fullTableName=self._fullTableName,
                field1=sql.Identifier(field1),
                field2=sql.Identifier(field2),
            )

        return sql.SQL(
            "SELECT * FROM {fullTableName} WHERE {field1} = (%s) AND {field2} = (%s) ORDER BY {orderBy}"
        ).format(
            fullTableName=self._fullTableName,
            field1=sql.Identifier(field1),
            field2=sql.Identifier(field2),
            orderBy=sql.Identifier(orderBy),
        )

    def __orderByQuery(self, orderBy: str, desc: bool):
        """
        Method to Get the Query to Sort the Table Rows in Asceding/Descending Order for a Given Field

        :param str orderBy: Table Field to Sort
        :param bool desc: Specifies wheter to Sort the Rows in Ascending or Descending Order
        :return: SQL Query
        :rtype: Composed
        """

        # Get Query to Sort the Rows in Ascending Order
        if not desc:
            return sql.SQL("SELECT * FROM {fullTableName} ORDER BY {order}").format(
                fullTableName=self._fullTableName,
                order=sql.Identifier(orderBy),
            )

        # Get Query to Sort the Rows in Descending Order
        return sql.SQL("SELECT * FROM {fullTableName} ORDER BY {order} DESC").format(
            fullTableName=sql.Identifier(self._fullTableName),
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
            "UPDATE {fullTableName} SET {modField} = (%s) WHERE {compareField} = (%s)"
        ).format(
            fullTableName=self._fullTableName,
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

        return sql.SQL("DELETE FROM {tableName} WHERE {field} = (%s)").format(
            tableName=sql.Identifier(self._tableName), field=sql.Identifier(field)
        )

    def _modify(self, idValue: int, field: str, value) -> None:
        """
        Method to Modify a Row Field Value with a Given Unique Identifier

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
        try:
            self._c.execute(query, [value, idValue])
            modifiedRow(field, value, idField, idValue, self._tableName)

        except Exception as err:
            raise err

    def _get(self, field: str, value, orderBy: str = None) -> bool:
        """
        Method to Check wheter the Table Contains at least One Row with a Given Field-Value Pair

        :param str field: Field to be Compared
        :param value: Value to be Compared
        :param str orderBy: Table Field that will be Used to Sort it. Default is ```None``
        :return: Returns ``True`` if One or More Items were Fetched. Otherwise, ``False``
        :rtype: bool
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        query = self.__getQuery(field, orderBy)

        # Execute the Query and Fetch the Items
        try:
            self._items = self._c.execute(query, [value]).fetchall()

        except Exception as err:
            raise err

        return len(self._items) > 0

    def _getMult(self, fields: list[str], values: list, orderBy: str = None) -> bool:
        """
        Method to Check wheter the Table Contains at least One Row with Some Given Field-Value Pairs

        :param list fields: Fields to be Compared
        :param list values: Values to be Compared
        :param str orderBy: Table Field that will be Used to Sort it. Default is ``None``
        :return: Returns ``True`` if One or More Items were Fetched. Otherwise, ``False``
        :rtype: bool
        :raises LenError: Raised if ```fields`` and ``values`` have Different Lists Length
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Lists MUST have the Same Length
        length = len(fields)

        if length != len(values):
            raise LenError()

        try:
            # Check the Number of WHERE Conditions
            if length > 2:
                console.print("Query hasn't been Implemented", style="warning")
                return

            # Get Query for Two Conditions and Execute it
            elif length == 2:
                twoCondQuery = self.__getAndQuery(fields[0], fields[1], orderBy)
                self._items = self._c.execute(twoCondQuery, [values[0], values[1]])

            # Query for One Condition. Method Implemented
            elif length == 1:
                return self._get(fields[0], values[0], orderBy)

            # Fetch the Items
            self._items = self._items.fetchall()

        except Exception as err:
            raise err

        return len(self._items) > 0

    def _all(self, orderBy: str, desc: bool) -> None:
        """
        Method to Print the Table Rows Sorted in Asceding/Descending Order for a Given Field

        :param str orderBy: Table Field to Sort
        :param bool desc: Specifies wheter to Sort the Rows in Ascending or Descending Order
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Query To Sort the Table Rows
        query = self.__orderByQuery(orderBy, desc)

        # Execute the Query and Fetch the Items
        try:
            self._items = self._c.execute(query).fetchall()

        except Exception as err:
            raise (err)

    def _remove(self, idValue: int) -> None:
        """
        Method to Remove a Row with a Given Unique Identifier

        :param int idValue: Row Unique Identifier
        :return:Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        idField = self._tablePKName

        # Get Query to Remove the Given Row
        query = self.__removeQuery(idField)

        # Execute the Query and Print a Success Message
        try:
            self._c.execute(query, [idValue])
            removeRow(self._tableName, idField, idValue)

        except Exception as err:
            raise err


class SpecializationTable:
    """
    Specialization Remote Table Class
    """

    # Database Connection
    _c = None
    _items = None

    # Specialization and Specialization's Parent Scheme, Table, Table PK and Scheme + Table Name
    _tableName = None
    _parentTableName = None
    _tablePKFKName = None
    _parentTablePKName = None
    _schemeName = None
    _parentSchemeName = None
    _fullTableName = None  # (schemeName.tableName)
    _fullParentTableName = None  # (parentSchemeName.parentTableName)

    # Constructor
    def __init__(
        self,
        tableName: str,
        parentTableName: str,
        tablePKFKName: str,
        parentTablePKName: str,
        remoteCursor,
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

        # Set Full Table Name
        if schemeName == None:
            self._fullTableName = sql.Identifier(self._tableName)

        else:
            self._fullTableName = sql.SQL(".").join(
                [sql.Identifier(self._schemeName), sql.Identifier(self._tableName)]
            )

        # Set Full Parent Table Name
        if parentSchemeName == None:
            self._fullParentTableName = sql.Identifier(self._parentTableName)

        else:
            self._fullParentTableName = sql.SQL(".").join(
                [
                    sql.Identifier(self._parentSchemeName),
                    sql.Identifier(self._parentTableName),
                ]
            )

        # Store Database Connection Cursor
        self._c = remoteCursor

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
                "SELECT * FROM {fullTableName} AS child INNER JOIN {fullParentTableName} AS parent ON child.{tablePKFKName} = parent.{parentTablePKName} WHERE {field} = (%s)"
            ).format(
                fullTableName=self._fullTableName,
                fullParentTableName=self._fullParentTableName,
                tablePKFKName=sql.Identifier(self._tablePKFKName),
                parentTablePKName=sql.Identifier(self._parentTablePKName),
                field=sql.Identifier(field),
            )

        return sql.SQL(
            "SELECT * FROM {fullTableName} AS child INNER JOIN {fullParentTableName} AS parent ON child.{tablePKFKName} = parent.{parentTablePKName} WHERE {field} = (%s) ORDER BY {orderBy}"
        ).format(
            fullTableName=self._fullTableName,
            fullParentTableName=self._fullParentTableName,
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
                "SELECT * FROM {fullParentTableName} WHERE {field} = (%s)"
            ).format(
                fullParentTableName=self._parentTableName,
                field=sql.Identifier(field),
            )

        return sql.SQL(
            "SELECT * FROM {fullParentTableName} WHERE {field} = (%s) ORDER BY {orderBy}"
        ).format(
            fullParentTableName=self._parentTableName,
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
                "SELECT * FROM {fullTableName} AS child INNER JOIN {fullParentTableName} AS parent ON child.{tablePKFKName} = parent.{parentTablePKName} WHERE {field1} = (%s) AND {field2} = (%s)"
            ).format(
                fullTableName=self._fullTableName,
                fullParentTableName=self._fullParentTableName,
                tablePKFKName=sql.Identifier(self._tablePKFKName),
                parentTablePKName=sql.Identifier(self._parentTablePKName),
                field1=sql.Identifier(field1),
                field2=sql.Identifier(field2),
            )

        return sql.SQL(
            "SELECT * FROM {fullTableName} AS child INNER JOIN {fullParentTableName} AS parent ON child.{tablePKFKName} = parent.{parentTablePKName} WHERE {field1} = (%s) AND {field2} = (%s) ORDER BY {orderBy}"
        ).format(
            fullTableName=self._fullTableName,
            fullParentTableName=self._fullParentTableName,
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
                "SELECT * FROM {fullParentTableName} WHERE {field1} = (%s) AND {field2} = (%s)"
            ).format(
                fullParentTableName=self._fullParentTableName,
                field1=sql.Identifier(field1),
                field2=sql.Identifier(field2),
            )

        return sql.SQL(
            "SELECT * FROM {fullParentTableName} WHERE {field1} = (%s) AND {field2} = (%s) ORDER BY {orderBy}"
        ).format(
            fullParentTableName=self._fullParentTableName,
            field1=sql.Identifier(field1),
            field2=sql.Identifier(field2),
            orderBy=sql.Identifier(orderBy),
        )

    def __orderByQuery(self, orderBy: str, desc: bool):
        """
        Method to Get the Query to Sort the Table Rows in Asceding/Descending Order for a Given Field

        :param str orderBy: Table Field to Sort
        :param bool desc: Specifies wheter to Sort the Rows in Ascending or Descending Order
        :return: SQL Query
        :rtype: Composed
        """

        # Get Query to Sort the Rows in Ascending Order
        if not desc:
            return sql.SQL(
                "SELECT * FROM {fullTableName} AS child INNER JOIN {fullParentTableName} AS parent ON child.{tablePKFKName} = parent.{parentTablePKName} ORDER BY {order}"
            ).format(
                fullTableName=self._fullTableName,
                fullParentTableName=self._fullParentTableName,
                tablePKFKName=sql.Identifier(self._tablePKFKName),
                parentTablePKName=sql.Identifier(self._parentTablePKName),
                order=sql.Identifier(orderBy),
            )

        # Get Query to Sort the Rows in Descending Order
        return sql.SQL(
            "SELECT * FROM {fullTableName} AS child INNER JOIN {fullParentTableName} AS parent ON child.{tablePKFKName} =parent.{parentTablePKName} ORDER BY {order} DESC"
        ).format(
            fullTableName=self._fullTableName,
            fullParentTableName=self._fullParentTableName,
            tablePKFKName=sql.Identifier(self._tablePKFKName),
            parentTablePKName=sql.Identifier(self._parentTablePKName),
            order=sql.Identifier(orderBy),
        )

    def __modifyQuery(self, fullTableName, compareField: str, modField: str):
        """
        Method to Modify a Row Field Value with a Given Unique Identifier at a Given Table

        :param fullTableName: SQL Identifier or Composed Table Name to Modify
        :param str compareField: Field to be Compared
        :param str modField: Field to Modify
        :return: SQL Query
        :rtype: Composed
        """

        return sql.SQL(
            "UPDATE {fullTableName} SET {modField} = (%s) WHERE {compareField} = (%s)"
        ).format(
            fullTableName=fullTableName,
            modField=sql.Identifier(modField),
            compareField=sql.Identifier(compareField),
        )

    def __removeQuery(self, fullTableName, field: str):
        """
        Method to Get the Query to Remove a Row with a Given Value at a Given Field and Table

        :param fullTableName: SQL Identifier or Composed Table that Contains the Row/s to be Removed
        :param str field: Field to be Compared
        :return: SQL Query
        :rtype: Composed
        """

        return sql.SQL("DELETE FROM {fullTableName} WHERE {field} = (%s)").format(
            fullTableName=fullTableName, field=sql.Identifier(field)
        )

    def __modify(self, parentTable: bool, idValue: int, field: str, value) -> None:
        """
        Method to Modify a Row Field Value with a Given Unique Identifier at a Given Table

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
        fullTableName = None

        # Check if the User wants to Modify the Row from the Parent Table
        if parentTable:
            idField = self._parentTablePKName
            tableName = self._parentTableName
            fullTableName = self._fullParentTableName

        else:
            idField = self._tablePKFKName
            tableName = self._tableName
            fullTableName = self._fullTableName

        # Get Query to Modify the Given Row
        query = self.__modifyQuery(fullTableName, idField, field)

        # Execute the Query and Print a Success Message
        try:
            self._c.execute(query, [value, idValue])
            modifiedRow(field, value, idField, idValue, tableName)

        except Exception as err:
            raise err

    def _modifyTable(self, idValue: int, field: str, value) -> None:
        """
        Method to Modify a Row Field Value with a Given Unique Identifier from the Specialization Table

        :param int idValue: Row Unique Identifier
        :param str field: Field to be Modified
        :param value: Value to be Assigned
        :return:Nothing
        :rtype: NoneType
        """

        return self.__modify(False, idValue, field, value)

    def _modifyParentTable(self, idValue: int, field: str, value) -> None:
        """
        Method to Modify a Row Field Value with a Given Unique Identifier from the Specialization's Parent Table

        :param int idValue: Row Unique Identifier
        :param str field: Field to be Modified
        :param value: Value to be Assigned
        :return:Nothing
        :rtype: NoneType
        """

        return self.__modify(True, idValue, field, value)

    def __get(self, parentTable: bool, field: str, value, orderBy: str = None) -> bool:
        """
        Method to Check wheter the Table Contains at least One Row with a Given Field-Value Pair at a Given Table

        :param bool parentTable: ``False`` if the User wants to Compare the Specialization Table. Otherwise,``True``
        :param str field: Field to be Compared
        :param value: Value to be Compared
        :param str orderBy: Table Field that will be Used to Sort it. Default is ``None``
        :return: Returns ``True`` if One or More Items were Fetched. Otherwise, ``False``
        :rtype: bool
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        try:
            # Check if the User wants to Get the Row from the Parent Table and Execute the Query
            if parentTable:
                getParentQuery = self.__getParentTableQuery(field, orderBy)
                self._items = self._c.execute(getParentQuery, [value])

            else:
                getSpecQuery = self.__getTableQuery(field, orderBy)
                self._items = self._c.execute(getSpecQuery, [value])

            # Fetch the Items
            self._items = self._items.fetchall()

        except Exception as err:
            raise err

        return len(self._items) > 0

    def _getTable(self, field: str, value, orderBy: str = None) -> bool:
        """
        Method to Check wheter the Table Contains at least One Row with a Given Field-Value Pair at the Specialization Table

        :param str field: Field to be Compared
        :param value: Value to be Compared
        :param str orderBy: Table Field that will be Used to Sort it. Default is ``None``
        :return: Returns ``True`` if One or More Items were Fetched. Otherwise, ``False``
        :rtype: bool
        """

        return self.__get(False, field, value, orderBy)

    def _getParentTable(self, field: str, value, orderBy=None) -> bool:
        """
        Method to Check wheter the Table Contains at least One Row with a Given Field-Value Pair at the Specialization's Parent Table

        :param str field: Field to be Compared
        :param value: Value to be Compared
        :param str orderBy: Table Field that will be Used to Sort it. Default is ``None``
        :return: Returns ``True`` if One or More Items were Fetched. Otherwise, ``False``
        :rtype: bool
        """

        return self.__get(True, field, value)

    def __getMult(
        self, parentTable: bool, fields: list[str], values: list, orderBy: str = None
    ) -> bool:
        """
        Method to Check wheter the Table Contains at least One Row with Some Given Field-Value Pairs

        :param bool parentTable: ``False`` if the User wants to Compare the Specialization Table. Otherwise,``True``
        :param list fields: Fields to be Compared
        :param list values: Values to be Compared
        :param str orderBy: Table Field that will be Used to Sort it. Default is ``None``
        :return: Returns ``True`` if One or More Items were Fetched. Otherwise, ``False``
        :rtype: bool
        :raises LenError: Raised if ```fields`` and ``values`` have Different Lists Length
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Lists MUST have the Same Length
        length = len(fields)

        if length != len(values):
            raise LenError()

        try:
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
                    self._items = self._c.execute(twoCondQuery, [values[0], values[1]])

                # Query for One Condition. Method Implemented
                elif length == 1:
                    return self._getParentTable(fields[0], values[0], orderBy)

            else:
                # Get Query for Specialization Table with Two Conditions and Execute it
                if length == 2:
                    twoCondQuery = self.__getTableAndQuery(
                        fields[0], fields[1], orderBy
                    )
                    self._items = self._c.execute(twoCondQuery, [values[0], values[1]])

                # Query for One Condition. Method Implemented
                elif length == 1:
                    return self._getTable(fields[0], values[0], orderBy)

            # Fetch the Items
            self._items = self._items.fetchall()

        except Exception as err:
            raise err

        return len(self._items) > 0

    def _getMultTable(
        self, fields: list[str], values: list, orderBy: str = None
    ) -> bool:
        """
        Method to Check wheter the Table Contains at least One Row with Some Given Field-Value Pairs at the Specialization Table

        :param list fields: Fields to be Compared
        :param list values: Values to be Compared
        :param str orderBy: Table Field that will be Used to Sort it. Default is ``None``
        :return: Returns ``True`` if One or More Items were Fetched. Otherwise, ``False``
        :rtype: bool
        """

        return self.__getMult(False, fields, values, orderBy)

    def _getMultParentTable(
        self, fields: list[str], values: list, orderBy: str = None
    ) -> bool:
        """
        Method to Check wheter the Table Contains at least One Row with Some Given Field-Value Pairs at the Specialization's Parent Table

        :param list fields: Fields to be Compared
        :param list values: Values to be Compared
        :param str orderBy: Table Field that will be Used to Sort it. Default is ``None``
        :return: Returns ``True`` if One or More Items were Fetched. Otherwise, ``False``
        :rtype: bool
        """

        return self.__getMult(True, fields, values, orderBy)

    def _all(self, orderBy: str, desc: bool) -> None:
        """
        Method to Print the Table Rows Sorted in Asceding/Descending Order for a Given Field at the Specialization Table

        :param str orderBy: Table Field to Sort
        :param bool desc: Specifies wheter to Sort the Rows in Ascending or Descending Order
        :return: Nothing
        :rtype: NoneType
        :raises Exception: Raised when Something Occurs at Query Execution or Items Fetching
        """

        # Get Query to Sort Items from the Specialization Table
        query = self.__orderByQuery(orderBy, desc)

        # Execute the Query and Fecth Items
        try:
            self._items = self._c.execute(query).fetchall()

        except Exception as err:
            raise (err)

    def _remove(self, idValue: int) -> None:
        """
        Method to Remove a Row with a Given Unique Identifier from the Specialization and its Parent Table

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
        tableQuery = self.__removeQuery(self._fullTableName, idField)

        # Get Query to Remove Row from the Specialization's Parent Table
        parentTableQuery = self.__removeQuery(self._fullParentTableName, parentIdField)

        try:
            # Remove Row from Specialization Table
            self._c.execute(tableQuery, [idValue])
            removeRow(tableName, idField, idValue)

            # Remove Row from Specialization's Parent Table
            self._c.execute(parentTableQuery, [idValue])
            removeRow(parentTableName, parentIdField, idValue)

        except Exception as err:
            raise err
