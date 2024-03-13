# Country Class
class Country:
    # Public Fields
    name = ""
    phonePrefix = ""

    # Constructor
    def __init__(self, name: str, phonePrefix: int):
        self.name = name
        self.phonePrefix = phonePrefix


# Region Class
class Region:
    # Public Fields
    name = ""
    countryId = ""
    airForwarderId = ""
    oceanForwarderId = ""

    # Constructor
    def __init__(
        self, name: str, countryId: int, airForwarderId: int, oceanForwarderId: int
    ):
        self.name = name
        self.countryId = countryId
        self.airForwarderId = airForwarderId
        self.oceanForwarderId = oceanForwarderId
