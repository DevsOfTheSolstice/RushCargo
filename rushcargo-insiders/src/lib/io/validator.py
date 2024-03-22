from ..model.constants import *
import os


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
    isAlpha: bool = True,
    isDigit: bool = True,
    isWhitespace: bool = False,
    isEnDash: bool = False,
    isSpecial: bool = False,
) -> bool:
    # Nothing to Check
    if isAlpha and isDigit and isWhitespace and isSpecial:
        return True

    # Check String Length
    if not nullable and len(inputStr) == 0:
        return False

    for i in inputStr:
        # Check if the Given Character is an Alphabetical Character
        if isAlpha and i.isalpha():
            continue

        # Check if the Given Character is a Digit
        if isDigit and i.isdigit():
            continue

        # Check if the Given Character is a Whitespace
        if isWhitespace and i == " ":
            continue

        # Check if the Given Character is an En Dash
        if isEnDash and i == "-":
            continue

        if isSpecial:
            continue

        return False

    return True


# String Input Validator that Only Accepts Digits
def onlyDigits(inputStr: str) -> bool:
    return checkString(inputStr, False, False, True, False, False, False)


# String Input Validator that Only Accepts Alphabetic Characters
def onlyAlpha(inputStr: str) -> bool:
    return checkString(inputStr, False, True, False, False, False, False)


# String Input Validator for Territories Name
def territoryValidator(inputStr: str, nullable: bool = False) -> bool:
    return checkString(inputStr, nullable, True, False, True, True, False)


# Check Table Value for the Given Field
def checkTableValue(table: str, field: str, value) -> bool:
    """
    Returns True for Valid Values. Otherwise, False
    """

    # Check Field for Country Table
    if table == COUNTRY_TABLENAME:
        # Check if Country Name only Contains Characters or Whitespaces
        if field == COUNTRY_NAME:
            return territoryValidator(value)

        # Check Value Given for Numeric Data Types
        else:
            return onlyDigits(value)

    # Check Field for Province Table
    elif table == PROVINCE_TABLENAME:
        # Check if Province Name only Contains Characters or Whitespaces
        if field == PROVINCE_NAME:
            return territoryValidator(value)

        # Check Value Given for Numeric Data Types
        else:
            return onlyDigits(value)

    # Check Field for Region Table
    elif table == REGION_TABLENAME:
        # Check if Region Name only Contains Characters or Whitespaces
        if field == REGION_NAME:
            return territoryValidator(value)

        # Check Value Given for Numeric Data Types
        else:
            return onlyDigits(value)

    # Check Field for City Table
    elif table == CITY_TABLENAME:
        # Check if City Name only Contains Characters or Whitespaces
        if field == CITY_NAME:
            return territoryValidator(value)

        # Check Value Given for Numeric Data Types
        else:
            return onlyDigits(value)

    elif table == CITY_AREA_TABLENAME:
        # Check if City Name only Contains Characters or Whitespaces
        if field == CITY_AREA_NAME:
            return territoryValidator(value)

        # Check if City Description only Contains Characters or Whitespaces, or it's Empty
        elif field == CITY_AREA_DESCRIPTION:
            return territoryValidator(value, True)

        # Check Value Given for Numeric Data Types
        else:
            return onlyDigits(value)

    return False


def isValueValid(table: str, field: str, value):
    if not checkTableValue(table, field, value):
        raise ValueError(table, field, value)
