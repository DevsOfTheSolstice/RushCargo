class LenError(Exception):
    """
    Exception Raised when Two Lists MUST have the Same Length, but don't
    """

    def __init__(self):
        super().__init__(f"Lists don't have the Same Length\n")
