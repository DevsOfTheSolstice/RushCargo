import os
from email_validator import validate_email, EmailNotValidError

from .constants import TABLE_TERRITORY_CMDS, TABLE_BUILDING_CMDS

from .exceptions import FieldValueError, PlaceError


# Clear Function
def clear():
    # For Windows
    if os.name == "nt":
        os.system("cls")

    # For Posix
    else:
        os.system("clear")


# String Input Validator
def checkString(
    inputStr: str,
    nullable: bool,
    canAlpha: bool = True,
    canDigit: bool = True,
    canWhitespace: bool = False,
    canEnDash: bool = False,
    canDot: bool = False,
) -> bool:
    # Nothing to Check
    if canAlpha and canDigit and canWhitespace and canEnDash and canDot:
        return True

    # Check String Length
    if not nullable and len(inputStr) == 0:
        return False

    for i in inputStr:
        # Check if the Given Character is an Alphabetical Character
        if canAlpha and i.isalpha():
            continue

        # Check if the Given Character is a Digit
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


# String Input Validator that Only Accepts Digit Charcters
def isDigitStr(inputStr: str) -> bool:
    return checkString(inputStr, False, False, True, False, False, False)


# String Input Validator that Only Accepts Alphabetic Characters
def isAlphaStr(inputStr: str) -> bool:
    return checkString(inputStr, False, True, False, False, False, False)


# String Input Validator that Checks if the Given String Corresponds to a Valid Address
def isAddressStr(inputStr: str, canDigits: bool, nullable: bool) -> bool:
    return checkString(inputStr, nullable, True, canDigits, True, False, False)


# String Input Validator for Territories Address
def territoryAddressValidator(inputStr: str) -> bool:
    return isAddressStr(inputStr, False, True)


# String Input Validator for Building Name
def buildingAddressValidator(inputStr: str) -> bool:
    return isAddressStr(inputStr, True, False)


# Table Email Validator that Returns its Normalized Form (if It's Valid)
def isEmailValid(email: str) -> str:
    try:
        # Validating Email
        validatedEmail = validate_email(email)

        # Get Email Normalized Form
        return validatedEmail.email

    except EmailNotValidError as err:
        raise err


# Table Phone Number Validator
def isPhoneValid(table: str, field: str, phone: str):
    if not isDigitStr(phone):
        raise FieldValueError(table, field, phone)


# Table Address Validator
def isAddressValid(table: str, field: str, address: str):
    if table in TABLE_TERRITORY_CMDS:
        if not territoryAddressValidator(address):
            raise FieldValueError(table, field, address)

        return

    elif table == TABLE_BUILDING_CMDS:
        if not buildingAddressValidator(address):
            raise FieldValueError(table, field, address)

        return


# Place Name Validator
def isPlaceNameValid(address: str):
    if not isAddressStr(address, True, False):
        raise PlaceError(address)
