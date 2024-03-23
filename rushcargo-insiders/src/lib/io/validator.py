import os
from email_validator import validate_email, EmailNotValidError

from ..model.constants import *


# Clear Function
def clear():
    # For Windows
    if os.name == "nt":
        os.system("cls")

    # For Posix
    else:
        os.system("clear")


# Email String Validator
def isEmailValid(email: str) -> str:
    try:
        # Validating Email
        validatedEmail = validate_email(email)

        # Get Email Normalized Form
        return validatedEmail.email
    except EmailNotValidError as err:
        raise err


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


# String Input Validator that Only Accepts Digit or Dot Characters
def isDotStr(inputStr: str) -> bool:
    return checkString(inputStr, False, False, True, False, False, True)


# String Input Validator that Only Accepts Alphabetic Characters
def isAlphaStr(inputStr: str) -> bool:
    return checkString(inputStr, False, True, False, False, False, False)


# String Input Validator that Only Accepts Alphabetic, Digit or Whitespace Characters
def isAddressStr(inputStr: str, nullable: bool = False) -> bool:
    return checkString(inputStr, nullable, True, True, True, False, False)


# String Input Validator for Territories Name
def territoryValidator(inputStr: str, nullable: bool = False) -> bool:
    return checkString(inputStr, nullable, True, False, True, True, False)


# String Input Validator for Building Name
def buildingValidator(inputStr: str, nullable: bool = False) -> bool:
    return checkString(inputStr, nullable, True, False, True, True, False)


# Check Table Value for the Given Field
def checkTableValue(table: str, field: str, value) -> bool:
    """
    Returns True for Valid Values. Otherwise, False
    """

    # Check Field for Country Table
    if table == COUNTRY_TABLENAME:
        # Check if Country Name only Contains Alphabetic, En Dash or Whitespace Characters
        if field == COUNTRY_NAME:
            return territoryValidator(value)

        # Check Value Given for Numeric Data Types
        else:
            return isDigitStr(value)

    # Check Field for Province Table
    elif table == PROVINCE_TABLENAME:
        # Check if Province Name only Contains Alphabetic, En Dash or Whitespace Characters
        if field == PROVINCE_NAME:
            return territoryValidator(value)

        # Check Value Given for Numeric Data Types
        else:
            return isDigitStr(value)

    # Check Field for Region Table
    elif table == REGION_TABLENAME:
        # Check if Region Name only Contains Alphabetic, En Dash or Whitespace Characters
        if field == REGION_NAME:
            return territoryValidator(value)

        # Check Value Given for Numeric Data Types
        else:
            return isDigitStr(value)

    # Check Field for City Table
    elif table == CITY_TABLENAME:
        # Check if City Name only Contains Alphabetic, En Dash or Whitespace Characters
        if field == CITY_NAME:
            return territoryValidator(value)

        # Check Value Given for Numeric Data Types
        else:
            return isDigitStr(value)

    elif table == CITY_AREA_TABLENAME:
        # Check if City Name only Contains Alphabetic, En Dash or Whitespace Characters
        if field == CITY_AREA_NAME:
            return territoryValidator(value)

        # Check if City Area Description only Contains Alphabetic, Digit or Whitespace Characters or it's Empty
        elif field == CITY_AREA_DESCRIPTION:
            return isAddressStr(value, True)

        # Check Value Given for Numeric Data Types
        else:
            return isDigitStr(value)

    elif table == BUILDING_TABLENAME or table == WAREHOUSE_TABLENAME:
        # Check if Building Name only Contains Alphabetic, En Dash or Whitespace Characters
        if field == BUILDING_NAME or field:
            return buildingValidator(value)

        # Check if Building Address Description only Contains Alphabetic, Digit or Whitespace Characters or it's Empty
        elif field == BUILDING_ADDRESS_DESCRIPTION:
            return isAddressStr(value, True)

        # Check if Building Coordinates only Contain Digit or Point Characters
        elif field == BUILDING_GPS_LATITUDE or field == BUILDING_GPS_LONGITUDE:
            return isDotStr(field)

        # Check Value Given for Numeric Data Types
        elif field != BUILDING_EMAIL:
            return isDigitStr(value)

    return False


# Table Field's Value Validator
def isValueValid(table: str, field: str, value):
    """
    NOTE: Emails are Validated through the 'isEmailValid' Function, not with this Function
    """

    if not checkTableValue(table, field, value):
        raise ValueError(table, field, value)