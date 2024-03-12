# Country Class
class Country:
  # Public Fields
  name = ""
  phonePrefix = ""

  # Constructor
  def __init__(self, name: str, phonePrefix: int):         
    self.name = name
    self.phonePrefix = phonePrefix