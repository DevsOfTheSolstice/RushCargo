class FieldError(Exception):
  """
  Exception Raised for Invalid Fields Used as Columns for a Given Table
  """

  def __init__(self, field: str, tableName: str):
    super().__init__(f"Invalid Column '{field}' for '{tableName}' Table\n")

class ValueError(Exception):
  """
  Exception Raised for Invalid Values Used as Columns Data for a Given Table
  """

  def __init__(self, value: str, field: str, tableName: str):
    super().__init__(f"Invalid '{value}' at Column '{field}' for '{tableName}' Table\n")