import os


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
