import os
from email_validator import validate_email, EmailNotValidError

from .constants import *
from .exceptions import FieldValueError, PlaceError, GoToMenu


def clear() -> None:
    """
    Function to Clear the Terminal

    :return: Nothing
    :rtype: NoneType
    """

    # For Windows
    if os.name == "nt":
        os.system("cls")

    # For Posix
    else:
        os.system("clear")


def stringValidator(
    inputStr: str,
    nullable: bool,
    canAlpha: bool = True,
    canDigit: bool = True,
    canWhitespace: bool = False,
    canEnDash: bool = False,
    canDot: bool = False,
) -> bool:
    """
    Function that Validates String Input by the User for SQL-related Operations

    :param str inputStr: User Input String
    :param bool nullable: Specificies whether the String can be Empty (of Length 0)
    :param bool canAlpha: ... can Contain Alphabetic Characters
    :param bool canDigit: ... can Contain Numeric Characters
    :param bool canWhitespace: ... can Contain Whitespace Characters
    :param bool canEnDash: ... can Contain En Dash Characters
    :param bool canDot: ... can Contain Dot Characters
    :return: ``True`` if the User Input String is Valid. Otherwise, ``False``
    :rtype: bool
    """

    # Nothing to Check
    if canAlpha and canDigit and canWhitespace and canEnDash and canDot:
        return True

    # Check String Length
    if not nullable and len(inputStr) == 0:
        return False

    for i in inputStr:
        # Check if the Given Character is an Alphabetic Character
        if canAlpha and i.isalpha():
            continue

        # Check if the Given Character is a Numeric Character
        if canDigit and i.isdigit():
            continue

        # Check if the Given Character is a Whitespace
        if canWhitespace and i.isspace():
            continue

        # Check if the Given Character is an En Dash
        if canEnDash and i == "-":
            continue

        # Check if the Given Character is a Dot
        if canDot and i == ".":
            continue

        return False

    return True


def digitValidator(inputStr: str) -> bool:
    """
    Function that Validates 'Digit' String Input by the User for SQL-related Operations

    :param str inputStr: User Input String
    :return: ``True`` if the User Input String is Valid. Otherwise, ``False``
    :rtype: bool
    """

    return stringValidator(inputStr, False, False, True, False, False, False)


def alphaValidator(inputStr: str) -> bool:
    """
    Function that Validates 'Alphabetic' String Input by the User for SQL-related Operations

    :param str inputStr: User Input String
    :return: ``True`` if the User Input String is Valid. Otherwise, ``False``
    :rtype: bool
    """

    return stringValidator(inputStr, False, True, False, False, False, False)


def addressValidator(inputStr: str, canDigits: bool, nullable: bool) -> bool:
    """
    Function that Validates 'Address' String Input by the User for SQL-related Operations

    :param str inputStr: User Input String
    :return: ``True`` if the User Input String is Valid. Otherwise, ``False``
    :rtype: bool
    """

    return stringValidator(inputStr, nullable, True, canDigits, True, False, False)


def territoryAddressValidator(inputStr: str) -> bool:
    """
    Function that Validates a Territory 'Address' String Input by the User for SQL-related Operations

    :param str inputStr: User Input String
    :return: ``True`` if the User Input String is Valid. Otherwise, ``False``
    :rtype: bool
    """

    return addressValidator(inputStr, False, True)


def buildingAddressValidator(inputStr: str) -> bool:
    """
    Function that Validates a Building 'Address' String Input by the User for SQL-related Operations

    :param str inputStr: User Input String
    :return: ``True`` if the User Input String is Valid. Otherwise, ``False``
    :rtype: bool
    """

    return addressValidator(inputStr, True, False)


def isEmailValid(email: str) -> str:
    """
    Function to Check the Email Input by the User, and Returns its Normalized Form if It's Valid

    :param str email: Email String that was Input by the User
    :return: Email Normalized Form
    :rtype: str
    :raises EmailNotValidError: Raised if the Email Contain Illegal Characters
    :raises GoToMenu: Raised when the User wants to Go Back to the Program Main Menu
    """

    # Check if the User wants to Exit
    if email == EXIT:
        raise GoToMenu

    try:
        # Validating Email
        validatedEmail = validate_email(email)

        # Get Email Normalized Form
        return validatedEmail.email

    except EmailNotValidError as err:
        raise err


def isAddressValid(tableName: str, field: str, address: str) -> None:
    """
    Function to Check the Address Input by the User for a Given Table

    :param str tableName: Table Name where the Address is Pretended to be Inserted
    :param str field: Address Field Name
    :param str address: Address String that was Input by the User
    :return: Nothing
    :rtype: NoneType
    :raises FieldValueError: Raised if the Address Contain Illegal Characters for the Given Table
    :raises GoToMenu: Raised when the User wants to Go Back to the Program Main Menu
    """

    # Check if the User wants to Exit
    if address == EXIT:
        raise GoToMenu

    if tableName == WAREHOUSE_TABLE_NAME or tableName == BRANCH_TABLE_NAME:
        if not buildingAddressValidator(address):
            raise FieldValueError(tableName, field, address)

    elif not territoryAddressValidator(address):
        raise FieldValueError(tableName, field, address)

    return


def isPlaceNameValid(name: str):
    """
    Function to Check the Place Name Input by the User

    :param str name: Place Name String that was Input by the User
    :return: Nothing
    :rtype: NoneType
    :raises PlacedError: Raised if the Place Name Contain Illegal Characters
    :raises GoToMenu: Raised when the User wants to Go Back to the Program Main Menu
    """

    # Check if the User wants to Exit
    if name == EXIT:
        raise GoToMenu

    if not addressValidator(name, True, False):
        raise PlaceError(name)
