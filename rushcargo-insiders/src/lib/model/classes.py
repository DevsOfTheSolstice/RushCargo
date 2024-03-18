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
        countryId, name, phonePrefix = item

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
        regionId, countryId, name, airForwarder, oceanForwarder = item

        return cls(name, countryId, regionId, airForwarder, oceanForwarder)


# Subregion Class
class Subregion:
    # Public Fields
    name: str = None
    regionId: int = None
    subregionId: int = None
    warehouseId: int = None

    # Constructor
    def __init__(
        self,
        name: str,
        regionId: int,
        subregionId: int = None,
        warehouseId: int = None,
    ):
        self.name = name
        self.regionId = regionId
        self.subregionId = subregionId
        self.warehouseId = warehouseId

    @classmethod
    def fromItemFetched(cls, item: tuple):
        """
        Initialize Subregion from Query Item Fetched
        """
        subregionId, regionId, name, warehouse = item

        return cls(name, regionId, subregionId, warehouse)


# City Class
class City:
    # Public Fields
    name: str = None
    subregionId: int = None
    cityId: int = None
    warehouseId: int = None

    # Constructor
    def __init__(
        self,
        name: str,
        subregionId: int,
        cityId: int = None
                ):
        self.name = name
        self.subregionId = subregionId
        self.cityId = cityId

    @classmethod
    def fromItemFetched(cls, item: tuple):
        """
        Initialize City from Query Item Fetched
        """
        cityId, subregionId, name = item

        return cls(name, subregionId, cityId)


# City Area Class
class CityArea:
    # Public Fields
    areaName: str = None
    areaDescription: str = None
    cityId: int = None
    areaId: int = None

    # Constructor
    def __init__(
        self,
        areaName: str,
        areaDescription: str,
        cityId: int,
        areaId: int = None,
    ):
        self.areaName = areaName
        self.areaDescription = areaDescription
        self.cityId = cityId
        self.areaId = areaId

    @classmethod
    def fromItemFetched(cls, item: tuple):
        """
        Initialize City Area from Query Item Fetched
        """
        areaId, cityId, areaName, areaDescription = item

        return cls(areaName, areaDescription, cityId, areaId)
