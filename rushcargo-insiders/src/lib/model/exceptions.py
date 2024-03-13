class ValueError(Exception):
    """
    Exception Raised for Invalid Values Used as Columns Data for a Given Table
    """

    def __init__(self, tableName: str, field: str, value: str):
        super().__init__(
            f"Invalid '{value}' at Column '{field}' for '{tableName}' Table\n"
        )
