class RowNotFound(Exception):
    """
    Exception Raised when a Query MUST Return at Least One Coincidence, but it doesn't
    """

    def __init__(self, tableName: str, field: str, value: str):
        super().__init__(
            f"'{value}' Not Found at Column '{field}' in '{tableName}' Table\n"
        )
