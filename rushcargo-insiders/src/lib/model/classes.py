# Country Class
class Country:
    # Public Fields
    name: str = None
    phonePrefix: int = None
    countryId: int = None

    # Constructor
    def __init__(self, name: str, phonePrefix: int, countryId: int = None):
        self.name = name
        self.phonePrefix = phonePrefix
        self.countryId = countryId

    @classmethod
    def fromItemFetched(cls, item: tuple):
        """
        Initialize Country from Query Item Fetched
        """
        countryId = item[0]
        name = item[1]
        phonePrefix = item[2]

        return cls(name, phonePrefix, countryId)


# Region Class
class Region:
    # Public Fields
    name: str = None
    countryId: int = None
    regionId: int = None
    airForwarderId: int = None
    oceanForwarderId: int = None

    # Constructor
    def __init__(
        self,
        name: str,
        countryId: int,
        regionId: int = None,
        airForwarderId: int = None,
        oceanForwarderId: int = None,
    ):
        self.name = name
        self.countryId = countryId
        self.regionId = regionId
        self.airForwarderId = airForwarderId
        self.oceanForwarderId = oceanForwarderId

    @classmethod
    def fromItemFetched(cls, item: tuple):
        """
        Initialize Region from Query Item Fetched
        """
        regionId = item[0]
        countryId = item[1]
        name = item[2]
        airForwarder = item[3]
        oceanForwarder = item[4]

        return cls(name, countryId, regionId, airForwarder, oceanForwarder)


# City Class
class City:
    # Public Fields
    name: str = None
    regionId: int = None
    cityId: int = None
    warehouseId: int = None

    # Constructor
    def __init__(
        self,
        name: str,
        regionId: int,
        cityId: int = None,
        warehouseId: int = None,
    ):
        self.name = name
        self.regionId = regionId
        self.cityId = cityId
        self.warehouseId = warehouseId

    @classmethod
    def fromItemFetched(cls, item: tuple):
        """
        Initialize City from Query Item Fetched
        """
        cityId = item[0]
        regionId = item[1]
        name = item[2]
        warehouse = item[3]

        return cls( name, regionId,cityId, warehouse)
