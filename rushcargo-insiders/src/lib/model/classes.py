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
        regionId, countryId, name, airForwarderId, oceanForwarderId = item

        return cls(name, countryId, regionId, airForwarderId, oceanForwarderId)


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
        subregionId, regionId, name, warehouseId = item

        return cls(name, regionId, subregionId, warehouseId)


# City Class
class City:
    # Public Fields
    name: str = None
    subregionId: int = None
    cityId: int = None

    # Constructor
    def __init__(self, name: str, subregionId: int, cityId: int = None):
        self.name = name
        self.subregionId = subregionId
        self.cityId = cityId

    @classmethod
    def fromItemFetched(cls, item: tuple):
        """
        Initialize City from Query Item Fetched
        """
        cityId, name, subregionId = item

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
        areaId, areaName, areaDescription, cityId = item

        return cls(areaName, areaDescription, cityId, areaId)


# Building Class
class Building:
    # Public Fields
    buildingId: int = None
    buildingName: str = None
    areaId: int = None
    phone: int = None
    email: str = None
    addressDescription: str = None
    gpsLatitude: int = None
    gpsLongitude: int = None
    address: str = None

    # Constructor
    def __init__(
        self,
        addressDescription: str,
        buildingName: str,
        email: str,
        gpsLatitude: int,
        gpsLongitude: int,
        phone: int,
        areaId: int,
        buildingId: int = None,
    ):
        self.addressDescription = addressDescription
        self.buildingName = buildingName
        self.email = email
        self.gpsLatitude = gpsLatitude
        self.gpsLongitude = gpsLongitude
        self.phone = phone
        self.areaId = areaId
        self.buildingId = buildingId

    @classmethod
    def fromItemFetched(cls, item: tuple):
        """
        Initialize Building from Query Item Fetched
        """
        (
            addressDescription,
            buildingName,
            email,
            gpsLatitude,
            gpsLongitude,
            phone,
            areaId,
            buildingId,
        ) = item

        return cls(
            addressDescription,
            buildingName,
            email,
            gpsLatitude,
            gpsLongitude,
            phone,
            areaId,
            buildingId,
        )


# Warehouse Class
class Warehouse:
    # Public Fields
    warehouseId: int = None

    # Constructor
    def __init__(
        self,
        warehouseId: int,
    ):
        self.warehouseId = warehouseId

    @classmethod
    def fromItemFetched(cls, item: tuple):
        """
        Initialize Warehouse from Query Item Fetched
        """
        warehouseId = item

        return cls(warehouseId)


# Branch Class
class Branch:
    # Public Fields
    branchId: int = None
    warehouseConnection: int = None
    ruteDistance: float = None

    # Constructor
    def __init__(
        self,
        ruteDistance: float,
        branchId: int,
        warehouseConnection: int,
    ):
        self.ruteDistance = ruteDistance
        self.branchId = branchId
        self.warehouseConnection = warehouseConnection

    @classmethod
    def fromItemFetched(cls, item: tuple):
        """
        Initialize Branch from Query Item Fetched
        """
        ruteDistance, branchId, warehouseConnection = item

        return cls(ruteDistance, branchId, warehouseConnection)
