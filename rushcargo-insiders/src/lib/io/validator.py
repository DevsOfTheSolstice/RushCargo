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
    input: str, isAlpha: bool = True, isDigit: bool = True, isSpecial: bool = False
) -> bool:
    # Nothing to Check
    if isAlpha and isDigit and isSpecial:
        return True

    for i in input:
        # Check if the Given Character is an Alphabetical Character
        if isAlpha and i.isalpha():
            continue

        # Check if the Given Character is a Digit
        if isDigit and i.isdigit():
            continue

        if isSpecial:
            continue

        return False

    return True


# String Input Validator that Only Accepts Digits
def onlyDigits(input: str) -> bool:
    return checkString(input, False, True, False)


# String Input Validator that Only Accepts Alphabetic Characters
def onlyAlpha(input: str) -> bool:
    return checkString(input, True, False, False)


# Check Table Field
def checkTableField(table: str, field: str, value) -> bool:
    """
    Returns True for Valid Values. Otherwise, False
    """

    # Check Field for Country Table
    if table == COUNTRY_TABLENAME:
        # Check if Country Name only Contains Characters
        if field == COUNTRY_NAME:
            return onlyAlpha(value)

        # Check Value Given for Numeric Data Types
        else:
            return onlyDigits(value)

    # Check Field for Region Table
    elif table == REGION_TABLENAME:
        # Check if Region Name only Contains Characters
        if field == REGION_NAME:
            return onlyAlpha(value)

        # Check Value Given for Numeric Data Types
        else:
            return onlyDigits(value)

    # Check Field for City Table
    elif table == CITY_TABLENAME:
        # Check if City Name only Contains Characters
        if field == CITY_NAME:
            return onlyAlpha(value)

        # Check Value Given for Numeric Data Types
        else:
            return onlyDigits(value)

    return False
