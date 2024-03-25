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


# Province Class
class Province:
    # Public Fields
    name: str = None
    countryId: int = None
    provinceId: int = None
    airForwarderId: int = None
    oceanForwarderId: int = None
    warehouseId: int = None

    # Constructor
    def __init__(
        self,
        name: str,
        countryId: int,
        provinceId: int = None,
        airForwarderId: int = None,
        oceanForwarderId: int = None,
        warehouseId: int = None,
    ):
        self.name = name
        self.countryId = countryId
        self.provinceId = provinceId
        self.airForwarderId = airForwarderId
        self.oceanForwarderId = oceanForwarderId
        self.warehouseId = warehouseId

    @classmethod
    def fromItemFetched(cls, item: tuple):
        """
        Initialize Province from Query Item Fetched
        """
        provinceId, countryId, name, airForwarderId, oceanForwarderId, warehouseId = (
            item
        )

        return cls(
            name, countryId, provinceId, airForwarderId, oceanForwarderId, warehouseId
        )


# Region Class
class Region:
    # Public Fields
    name: str = None
    provinceId: int = None
    regionId: int = None
    warehouseId: int = None

    # Constructor
    def __init__(
        self,
        name: str,
        provinceId: int,
        regionId: int = None,
        warehouseId: int = None,
    ):
        self.name = name
        self.provinceId = provinceId
        self.regionId = regionId
        self.warehouseId = warehouseId

    @classmethod
    def fromItemFetched(cls, item: tuple):
        """
        Initialize Region from Query Item Fetched
        """
        regionId, provinceId, name, warehouseId = item

        return cls(name, provinceId, regionId, warehouseId)


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
        cityId, name, regionId, warehouseId = item

        return cls(name, regionId, cityId, warehouseId)


# City Area Class
class CityArea:
    # Public Fields
    areaName: str = None
    areaDescription: str = None
    cityId: int = None
    areaId: int = None
    warehouseId: int = None

    # Constructor
    def __init__(
        self,
        areaName: str,
        areaDescription: str,
        cityId: int,
        areaId: int = None,
        warehouseId: int = None,
    ):
        self.areaName = areaName
        self.areaDescription = areaDescription
        self.cityId = cityId
        self.areaId = areaId
        self.warehouseId = warehouseId

    @classmethod
    def fromItemFetched(cls, item: tuple):
        """
        Initialize City Area from Query Item Fetched
        """
        areaId, areaName, areaDescription, cityId, warehouseId = item

        return cls(areaName, areaDescription, cityId, areaId, warehouseId)


# Building Class
class Building:
    # Public Fields
    buildingId: int = None
    buildingName: str = None
    areaId: int = None
    addressDescription: str = None
    gpsLatitude: float = None
    gpsLongitude: float = None
    phone: int = None
    email: str = None

    # Constructor
    def __init__(
        self,
        buildingName: str,
        gpsLatitude: float,
        gpsLongitude: float,
        addressDescription: str,
        phone: int,
        email: str,
        areaId: int,
        buildingId: int = None,
    ):
        self.buildingName = buildingName
        self.gpsLatitude = gpsLatitude
        self.gpsLongitude = gpsLongitude
        self.addressDescription = addressDescription
        self.phone = phone
        self.email = email
        self.areaId = areaId
        self.buildingId = buildingId

    @classmethod
    def fromItemFetched(cls, item: tuple):
        """
        Initialize Building from Query Item Fetched
        """
        (
            buildingId,
            areaId,
            email,
            phone,
            gpsLatitude,
            gpsLongitude,
            addressDescription,
            buildingName,
        ) = item

        return cls(
            buildingName,
            gpsLatitude,
            gpsLongitude,
            addressDescription,
            phone,
            email,
            areaId,
            buildingId,
        )


# Warehouse Class
class Warehouse(Building):
    # Constructor
    def __init__(
        self,
        buildingName: str,
        gpsLatitude: float,
        gpsLongitude: float,
        email: str,
        phone: int,
        areaId: int,
        addressDescription: str,
        buildingId: int = None,
    ):
        # Initialize Building Class
        super().__init__(
            buildingName,
            gpsLatitude,
            gpsLongitude,
            addressDescription,
            phone,
            email,
            areaId,
            buildingId,
        )

    @classmethod
    def fromItemFetched(cls, item: tuple):
        """
        Initialize Warehouse from Query Item Fetched
        """

        (
            _,  # Warehouse ID, Same as Building ID
            buildingId,
            areaId,
            email,
            phone,
            gpsLatitude,
            gpsLongitude,
            addressDescription,
            buildingName,
        ) = item

        return cls(
            buildingName,
            gpsLatitude,
            gpsLongitude,
            email,
            phone,
            areaId,
            addressDescription,
            buildingId,
        )


# Warehouse Connection Class
class WarehouseConnection:
    # Public Fields
    warehouseConnId: int = None
    warehouseFromId: int = None
    warehouseToId: int = None
    routeDistance: int = None

    # Constructor
    def __init__(
        self,
        warehouseFromId: int,
        warehouseToId: int,
        routeDistance: int,
        warehouseConnId: int = None,
    ):
        self.warehouseFromId = warehouseFromId
        self.warehouseToId = warehouseToId
        self.routeDistance = routeDistance
        self.warehouseConnId = warehouseConnId

    @classmethod
    def fromItemFetched(cls, item: tuple):
        """
        Initialize Warehouse Connection from Query Item Fetched
        """
        warehouseFromId, warehouseToId, routeDistance, warehouseConnId = item

        return cls(warehouseFromId, warehouseToId, routeDistance, warehouseConnId)


# Branch Class
class Branch(Building):
    # Public Fields
    branchId: int = None
    warehouseConnection: int = None
    routeDistance: float = None

    # Constructor
    def __init__(
        self,
        buildingName: str,
        gpsLatitude: float,
        gpsLongitude: float,
        email: str,
        phone: int,
        areaId: int,
        addressDescription: str,
        warehouseConnection: int,
        routeDistance: int,
        buildingId: int = None,
    ):
        # Initialize Building Class
        super().__init__(
            buildingName,
            gpsLatitude,
            gpsLongitude,
            addressDescription,
            phone,
            email,
            areaId,
            buildingId,
        )
        self.warehouseConnection = warehouseConnection
        self.routeDistance = routeDistance

    @classmethod
    def fromItemFetched(cls, item: tuple):
        """
        Initialize Branch from Query Item Fetched
        """

        (
            _,  # Branch ID, Same as Building ID
            warehouseConnection,
            routeDistance,
            buildingId,
            areaId,
            email,
            phone,
            gpsLatitude,
            gpsLongitude,
            addressDescription,
            buildingName,
        ) = item

        return cls(
            buildingName,
            gpsLatitude,
            gpsLongitude,
            email,
            phone,
            areaId,
            addressDescription,
            warehouseConnection,
            routeDistance,
            buildingId,
        )
