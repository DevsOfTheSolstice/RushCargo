from psycopg import sql
from rich.table import Table

from .database import Database, console

from .constants import BOX_STYLE
from .exceptions import LenError


# Message Printed when there was Nothing Fetched from Query
def noCoincidenceFetched() -> None:
    console.print("No Results Fetched", style="warning")


# Message Printed when the User tries to Insert a Row which has Unique Fields that Contains Values
# that have been already Inserted
def uniqueInserted(tableName: str, field: str, value) -> None:
    console.print(
        f"Unique '{value}' Already Inserted at '{field}' on {tableName}",
        style="warning",
    )


# Message Printed when the User tries to Insert a Row that Contains Values which Violate
# Unique Constraint of Multiple Columns
def uniqueInsertedMult(tableName: str, field: list[str], value: list) -> None:
    fieldStr = ",".join(f for f in field)
    valueStr = ",".join(str(v) for v in value)

    console.print(
        f"({valueStr}) at ({fieldStr}) Violates Unique Constraint on {tableName}",
        style="warning",
    )


# Message Printed when a New Row has been Successfully Inserted to a Table
def insertedRow(name: str, tableName: str) -> str:
    return f"{name} Successfully Inserted to {tableName} Table"


# Message Print when a Row has been Successfully Removed from a Table
def removeRow(tableName: str, idField: int, idValue: int) -> str:
    return (
        f"Row with '{idField}' '{idValue}' Successfully Removed from {tableName} Table"
    )


# Get Table with Default values
def getTable(tableName: str, nItems: int) -> Table:
    # Initialize Rich Table
    return Table(
        title=f"{tableName} Table Query",
        title_style="title",
        header_style="header",
        caption=f"{nItems} Results Fetched",
        caption_style="caption",
        border_style="border",
        box=BOX_STYLE,
        row_styles=["text", "textAlt"],
    )


# Basic Table Class
class BasicTable:
    # Protected Fields
    _tableName = None
    _tablePKName = None

    _items = None
    _c = None

    # Constructor
    def __init__(self, tableName: str, tablePKName: str, database: Database):
        # Assign Table Name
        self._tableName = tableName

        # Assign Table Columns Name
        self._tablePKName = tablePKName

        # Get Cursor
        self._c = database.getCursor()

    # Returns Get Query
    def __getQuery(self, field: str, value):
        return sql.SQL("SELECT * FROM {tableName} WHERE {field} = {value}").format(
            tableName=sql.Identifier(self._tableName),
            field=sql.Identifier(field),
            value=str(value),
        )

    # Returns Get Query with One AND Condition
    def __getAndQuery(self, field1: str, field2: str, value1: str, value2: str):
        return sql.SQL(
            "SELECT * FROM {tableName} WHERE {field1} = {value1} AND {field2} = {value2}"
        ).format(
            tableName=sql.Identifier(self._tableName),
            field1=sql.Identifier(field1),
            field2=sql.Identifier(field2),
            value1=str(value1),
            value2=str(value2),
        )

    # Returns Query to Sort Table Rows from a Given Table
    def __orderByQuery(self, orderBy: str, desc: bool) -> str:
        # Get Order By Query
        if not desc:
            return sql.SQL("SELECT * FROM {tableName} ORDER BY {order}").format(
                tableName=sql.Identifier(self._tableName),
                order=sql.Identifier(orderBy),
            )

        # Get Order By Query in Descending Order
        return sql.SQL("SELECT * FROM {tableName} ORDER BY {order} DESC").format(
            tableName=sql.Identifier(self._tableName),
            order=sql.Identifier(orderBy),
        )

    # Returns Query to Modify a Row from a Given Table
    def __modifyQuery(self, idField: str, field: str) -> str:
        return sql.SQL(
            "UPDATE {tableName} SET {field} = (%s) WHERE {idField} = (%s)"
        ).format(
            tableName=sql.Identifier(self._tableName),
            field=sql.Identifier(field),
            idField=sql.Identifier(idField),
        )

    # Returns Query to Remove a Row from a Given Table
    def __removeQuery(self, idField: str) -> str:
        return sql.SQL("DELETE FROM {tablename} WHERE {idField} = (%s)").format(
            tablename=sql.Identifier(self._tableName), idField=sql.Identifier(idField)
        )

    # Modify Row from a Given Table
    def _modify(self, idValue: int, field: str, value) -> None:
        idField = self._tablePKName

        # Get Query to Modify the Given Row
        query = self.__modifyQuery(idField, field)

        # Execute Query
        try:
            self._c.execute(query, [value, idValue])
            console.print(
                f"Data '{value}' Successfully Assigned to '{field}' at '{idField}' '{idValue}' in {self._tableName} Table",
                style="success",
            )

        except Exception as err:
            raise err

    # Filter Items from a Given Table
    def _get(self, field: str, value) -> bool:
        """
        Returns True if One or More Items were Fetched. Otherwise, False
        """

        # Get Query
        query = self.__getQuery(field, value)

        # Execute Query and Fetch Items
        try:
            self._items = self._c.execute(query).fetchall()

        except Exception as err:
            raise err

        return len(self._items) > 0

    # Filter Items from a Given Table with Multiple WHERE Conditions
    def _getMult(self, fields: list[str], values: list) -> bool:
        """
        Returns True if One or More Items were Fetched. Otherwise, False
        """

        # Lists MUST have the Same Length
        length = len(fields)

        if length != len(values):
            raise LenError()

        query = None

        # Check Number of WHERE Conditions
        if length > 2:
            console.print("Query hasn't been Implemented", style="warning")
            return

        # Get Query for Two Conditions
        elif length == 2:
            query = self.__getAndQuery(fields[0], fields[1], values[0], values[1])

        # Method Implemented
        elif length == 1:
            return self._get(fields[0], values[0])

        # Execute Query and Fetch Items
        try:
            self._items = self._c.execute(query).fetchall()

        except Exception as err:
            raise err

        return len(self._items) > 0

    # Get All Items from a Given Table
    def _all(self, orderBy: str, desc: bool) -> None:
        # Get Query To Sort Items from a Given Table
        query = self.__orderByQuery(orderBy, desc)

        # Execute Query and Fetch Items
        try:
            self._items = self._c.execute(query).fetchall()

        except Exception as err:
            raise (err)

    # Remove Row from a Given Table
    def _remove(self, idValue: int) -> None:
        idField = self._tablePKName

        # Get Query to Remove the Given Row
        query = self.__removeQuery(idField)

        # Execute Query
        try:
            self._c.execute(query, [idValue])

            console.print(
                removeRow(self._tableName, idField, idValue),
                style="success",
            )

        except Exception as err:
            raise err


# Specialization Table Class
class SpecializationTable:
    # Protected Fields
    _tableName = None
    _parentTableName = None
    _tablePKFKName = None
    _parentTablePKName = None

    _items = None
    _c = None

    # Constructor
    def __init__(
        self,
        tableName: str,
        parentTableName: str,
        tablePKFKName: str,
        parentTablePKName: str,
        database: Database,
    ):
        # Assign Table Names
        self._tableName = tableName
        self._parentTableName = parentTableName

        # Assign Table Columns Name
        self._tablePKFKName = tablePKFKName
        self._parentTablePKName = parentTablePKName

        # Get Cursor
        self._c = database.getCursor()

    # Returns Get Query from Specialization Table
    def __getTableQuery(self, field: str, value):
        return sql.SQL(
            "SELECT * FROM {tableName} AS child INNER JOIN {parentTableName} AS parent ON child.{tablePKFKName} = parent.{parentTablePKName} WHERE {field} = {value}"
        ).format(
            tableName=sql.Identifier(self._tableName),
            parentTableName=sql.Identifier(self._parentTableName),
            tablePKFKName=sql.Identifier(self._tablePKFKName),
            parentTablePKName=sql.Identifier(self._parentTablePKName),
            field=sql.Identifier(field),
            value=str(value),
        )

    # Returns Get Query from Specialization's Parent Table
    def __getParentTableQuery(self, field: str, value):
        return sql.SQL(
            "SELECT * FROM {parentTableName} WHERE {field} = {value}"
        ).format(
            tableName=sql.Identifier(self._parentTableName),
            field=sql.Identifier(field),
            value=str(value),
        )

    # Returns Get Query with One AND Condition from Specialization Table
    def __getTableAndQuery(self, field1: str, field2: str, value1: str, value2: str):
        return sql.SQL(
            "SELECT * FROM {tableName} AS child INNER JOIN {parentTableName} AS parent ON child.{tablePKFKName} = parent.{parentTablePKName} WHERE {field1} = {value1} AND {field2} = {value2}"
        ).format(
            tableName=sql.Identifier(self._tableName),
            parentTableName=sql.Identifier(self._parentTableName),
            tablePKFKName=sql.Identifier(self._tablePKFKName),
            parentTablePKName=sql.Identifier(self._parentTablePKName),
            field1=sql.Identifier(field1),
            field2=sql.Identifier(field2),
            value1=str(value1),
            value2=str(value2),
        )

    # Returns Get Query with One AND Condition from Specialization's Parent Table
    def __getParentTableAndQuery(
        self, field1: str, field2: str, value1: str, value2: str
    ):
        return sql.SQL(
            "SELECT * FROM {parentTableName} WHERE {field1} = {value1} AND {field2} = {value2}"
        ).format(
            parentTableName=sql.Identifier(self._parentTableName),
            field1=sql.Identifier(field1),
            field2=sql.Identifier(field2),
            value1=str(value1),
            value2=str(value2),
        )

    # Returns Query to Sort Table Rows from a Given Table
    def __orderByQuery(self, orderBy: str, desc: bool) -> str:
        # Get Sort By Query
        if not desc:
            return sql.SQL(
                "SELECT * FROM {tableName} AS child INNER JOIN {parentTableName} AS parent ON child.{tablePKFKName} = parent.{parentTablePKName} ORDER BY {order}"
            ).format(
                tableName=sql.Identifier(self._tableName),
                parentTableName=sql.Identifier(self._parentTableName),
                tablePKFKName=sql.Identifier(self._tablePKFKName),
                parentTablePKName=sql.Identifier(self._parentTablePKName),
                order=sql.Identifier(orderBy),
            )

        # Get Sort By Query in Descending Order
        return sql.SQL(
            "SELECT * FROM {tableName} AS child INNER JOIN {parentTableName} AS parent ON child.{tablePKFKName} =parent.{parentTablePKName} ORDER BY {order} DESC"
        ).format(
            tableName=sql.Identifier(self._tableName),
            parentTableName=sql.Identifier(self._parentTableName),
            tablePKFKName=sql.Identifier(self._tablePKFKName),
            parentTablePKName=sql.Identifier(self._parentTablePKName),
            order=sql.Identifier(orderBy),
        )

    # Returns Query to Modify a Row from a Given Table
    def __modifyQuery(self, tableName: str, idField: str, field: str) -> str:
        return sql.SQL(
            "UPDATE {tableName} SET {field} = (%s) WHERE {idField} = (%s)"
        ).format(
            tableName=sql.Identifier(tableName),
            field=sql.Identifier(field),
            idField=sql.Identifier(idField),
        )

    # Returns Query to Remove a Row from a Given Table
    def __removeQuery(self, tableName: str, idField: str) -> str:
        return sql.SQL("DELETE FROM {tableName} WHERE {idField} = (%s)").format(
            tableName=sql.Identifier(tableName), idField=sql.Identifier(idField)
        )

    # Modify Row
    def __modify(self, parentTable: bool, idValue: int, field: str, value) -> None:
        idField = None
        tableName = None

        # Check if the User wants to Modify the Row from the Parent Table
        if parentTable:
            idField = self._parentTablePKName
            tableName = self._parentTableName
        else:
            idField = self._tablePKFKName
            tableName = self._tableName

        # Get Query to Modify a Row from a Given Table
        query = self.__modifyQuery(tableName, idField, field)

        # Execute Query
        try:
            self._c.execute(query, [value, idValue])
            console.print(
                f"Data '{value}' Successfully Assigned to '{field}' at '{idField}' '{idValue}' in {tableName} Table",
                style="success",
            )

        except Exception as err:
            raise err

    # Modify Row from Specialization Table
    def _modifyTable(self, idValue: int, field: str, value) -> None:
        return self.__modify(False, idValue, field, value)

    # Modify Row from Specialization's Parent Table
    def _modifyParentTable(self, idValue: int, field: str, value) -> None:
        return self.__modify(True, idValue, field, value)

    # Filter Items from a Given Table
    def __get(self, parentTable: bool, field: str, value) -> bool:
        """
        Returns True if One or More Items were Fetched. Otherwise, False
        """

        query = None

        # Check if the User wants to Get the Row from the Parent Table
        if parentTable:
            query = self.__getParentTableQuery(field, value)
        else:
            query = self.__getTableQuery(field, value)

        # Execute Query and Fetch Items
        try:
            self._items = self._c.execute(query).fetchall()

        except Exception as err:
            raise err

        return len(self._items) > 0

    # Filter Items from Specialization Table
    def _getTable(self, field: str, value) -> bool:
        return self.__get(False, field, value)

    # Filter Items from Specialization's Parent Table
    def _getParentTable(self, field: str, value) -> bool:
        return self.__get(True, field, value)

    # Filter Items from a Given Table with Multiple WHERE Conditions
    def __getMult(self, parentTable: bool, fields: list[str], values: list) -> bool:
        """
        Returns True if One or More Items were Fetched. Otherwise, False
        """

        # Lists MUST have the Same Length
        length = len(fields)

        if length != len(values):
            raise LenError()

        query = None

        # Check Number of WHERE Conditions
        if length > 2:
            console.print("Query hasn't been Implemented", style="warning")
            return

        # Get Query
        if parentTable:
            # Get Query for Specialization's Parent Table with Two Conditions
            if length == 2:
                query = self.__getParentTableAndQuery(
                    fields[0], fields[1], values[0], values[1]
                )

            # Method Already Implemented
            elif length == 1:
                return self._getParentTable(fields[0], values[0])

        else:
            # Get Query for Specialization Table with Two Conditions
            if length == 2:
                query = self.__getTableAndQuery(
                    fields[0], fields[1], values[0], values[1]
                )

            # Method Already Implemented
            elif length == 1:
                return self._getTable(fields[0], values[0])

        # Execute Query and Fetch Items
        try:
            self._items = self._c.execute(query).fetchall()

        except Exception as err:
            raise err

        return len(self._items) > 0

    # Filter Items from Specialization Table with Multiple WHERE Conditions
    def _getMultTable(self, fields: list[str], values: list) -> bool:
        return self.__getMult(False, fields, values)

    # Filter Items from Specialization's Panret Table with Multiple WHERE Conditions
    def _getMultParentTable(self, fields: list[str], values: list) -> bool:
        return self.__getMult(True, fields, values)

    # Get All Items from a Given Table
    def _all(self, orderBy: str, desc: bool) -> None:
        # Get Query to Sort Items from a Given Table
        query = self.__orderByQuery(orderBy, desc)

        # Execute Query and Fecth Items
        try:
            self._items = self._c.execute(query).fetchall()
            
        except Exception as err:
            raise (err)

    # Remove Row from a Given Table and its Parent Table
    def _remove(self, idValue: int) -> None:
        # Get Specialization and Specialization's Parent Table Name and ID Field
        parentIdField = self._parentTablePKName
        parentTableName = self._parentTableName
        idField = self._tablePKFKName
        tableName = self._tableName

        # Get Query to Remove Row from a Given Table
        tableQuery = self.__removeQuery(tableName, idField)

        # Get Query to Remove Row from its Parent Table
        parentTableQuery = self.__removeQuery(parentTableName, parentIdField)

        try:
            # Remove Row from Specialization Table
            self._c.execute(tableQuery, [idValue])
            console.print(
                removeRow(tableName, idField, idValue),
                style="success",
            )

            # Remove Row from Specialization's Parent Table
            self._c.execute(parentTableQuery, [idValue])
            console.print(
                removeRow(parentTableName, parentIdField, idValue),
                style="success",
            )

        except Exception as err:
            raise err
