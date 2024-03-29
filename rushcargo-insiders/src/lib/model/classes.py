class Country:
    """
    Country Class that Represents a Row from its Remote Table
    """

    # Public Fields
    name: str = None
    phonePrefix: int = None
    countryId: int = None

    def __init__(self, name: str, phonePrefix: int, countryId: int = None):
        """
        Country Class Construtor

        :param str name: Country Name
        :param int phonePrefix: Country Phone Prefix
        :param int countryId: Country ID at its Remote Table. Default is ``None``
        """

        self.name = name
        self.phonePrefix = phonePrefix
        self.countryId = countryId

    @classmethod
    def fromFetchedItem(cls, item: tuple):
        """
        Country Classmethod to Initialize a Country Object from the Fetched Item at a Given Query

        :param tuple item: Fetched Row from Country Remote Table
        :return: Country Object
        :rtype: Self@Country
        """

        countryId, name, phonePrefix = item

        return cls(name, phonePrefix, countryId)


class Province:
    """
    Province Class that Represents a Row from its Remote Table
    """

    # Public Fields
    name: str = None
    countryId: int = None
    provinceId: int = None
    airForwarderId: int = None
    oceanForwarderId: int = None
    warehouseId: int = None

    def __init__(
        self,
        name: str,
        countryId: int,
        provinceId: int = None,
        airForwarderId: int = None,
        oceanForwarderId: int = None,
        warehouseId: int = None,
    ):
        """
        Province Class Construtor

        :param str name: Province Name
        :param int countryId: Country ID at Remote Table where the Province is Located
        :param int provinceId: Province ID at its Remote Table. Default is ``None``
        :param int airForwarderId: Province Main Air Forwarder Office ID at its Remote Table. Default is ``None``
        :param int oceanForwarderId: Province Main Ocean Forwarder Office ID at its Remote Table. Default is ``None``
        :param int warehouseId: Province Main Warehouse ID at its Remote Table. Default is ``None``
        """

        self.name = name
        self.countryId = countryId
        self.provinceId = provinceId
        self.airForwarderId = airForwarderId
        self.oceanForwarderId = oceanForwarderId
        self.warehouseId = warehouseId

    @classmethod
    def fromFetchedItem(cls, item: tuple):
        """
        Province Classmethod to Initialize a Province Object from the Fetched Item at a Given Query

        :param tuple item: Fetched Row from Province Remote Table
        :return: Province Object
        :rtype: Self@Province
        """

        provinceId, countryId, name, airForwarderId, oceanForwarderId, warehouseId = (
            item
        )

        return cls(
            name, countryId, provinceId, airForwarderId, oceanForwarderId, warehouseId
        )


class Region:
    """
    Region Class that Represents a Row from its Remote Table
    """

    # Public Fields
    name: str = None
    provinceId: int = None
    regionId: int = None
    warehouseId: int = None

    def __init__(
        self,
        name: str,
        provinceId: int,
        regionId: int = None,
        warehouseId: int = None,
    ):
        """
        Region Class Construtor

        :param str name: Region Name
        :param int provinceId: Province ID at Remote Table where the Region is Located
        :param int regionId: Region ID at its Remote Table. Default is ``None``
        :param int warehouseId: Region Main Warehouse ID at its Remote Table. Default is ``None``
        """

        self.name = name
        self.provinceId = provinceId
        self.regionId = regionId
        self.warehouseId = warehouseId

    @classmethod
    def fromFetchedItem(cls, item: tuple):
        """
        Region Classmethod to Initialize a Region Object from the Fetched Item at a Given Query

        :param tuple item: Fetched Row from Region Remote Table
        :return: Region Object
        :rtype: Self@Region
        """

        regionId, provinceId, name, warehouseId = item

        return cls(name, provinceId, regionId, warehouseId)


class City:
    """
    City Class that Represents a Row from its Remote Table
    """

    # Public Fields
    name: str = None
    regionId: int = None
    cityId: int = None
    warehouseId: int = None

    def __init__(
        self,
        name: str,
        regionId: int,
        cityId: int = None,
        warehouseId: int = None,
    ):
        """
        City Class Construtor

        :param str name: City Name
        :param int regionId: Region ID at Remote Table where the City is Located
        :param int cityId: City ID at its Remote Table. Default is ``None``
        :param int warehouseId: City Main Warehouse ID at its Remote Table. Default is ``None``
        """

        self.name = name
        self.regionId = regionId
        self.cityId = cityId
        self.warehouseId = warehouseId

    @classmethod
    def fromFetchedItem(cls, item: tuple):
        """
        City Classmethod to Initialize a City Object from the Fetched Item at a Given Query

        :param tuple item: Fetched Row from City Remote Table
        :return: City Object
        :rtype: Self@City
        """

        cityId, name, regionId, warehouseId = item

        return cls(name, regionId, cityId, warehouseId)


class Building:
    """
    Building Class that Represents a Row from its Remote Table
    """

    # Public Fields
    buildingId: int = None
    buildingName: str = None
    cityId: int = None
    addressDescription: str = None
    gpsLatitude: float = None
    gpsLongitude: float = None
    phone: int = None
    email: str = None

    def __init__(
        self,
        buildingName: str,
        gpsLatitude: float,
        gpsLongitude: float,
        addressDescription: str,
        phone: int,
        email: str,
        cityId: int,
        buildingId: int = None,
    ):
        """
        Building Class Construtor

        :param str name: Building Name
        :param float gpsLatitude: Building GPS Latitude Obtained throguh the Nominatim API
        :param float gpsLongitude: Building GPS Longitude Obtained throguh the Nominatim API
        :param str addressDescription: Building Address Description at the Given City
        :param int phone: Building Main Phone Number
        :param str email: Building Main Email
        :param int cityId: City ID at its Remote Table where the Building is Located
        :param int buildingId: Building ID at its Remote Table. Default is ``None``
        """

        self.buildingName = buildingName
        self.gpsLatitude = gpsLatitude
        self.gpsLongitude = gpsLongitude
        self.addressDescription = addressDescription
        self.phone = phone
        self.email = email
        self.cityId = cityId
        self.buildingId = buildingId

    @classmethod
    def fromFetchedItem(cls, item: tuple):
        """
        Building Classmethod to Initialize a Building Object from the Fetched Item at a Given Query

        :param tuple item: Fetched Row from Building Remote Table
        :return: Building Object
        :rtype: Self@Building
        """

        (
            buildingId,
            email,
            phone,
            gpsLatitude,
            gpsLongitude,
            addressDescription,
            buildingName,
            cityId,
        ) = item

        return cls(
            buildingName,
            gpsLatitude,
            gpsLongitude,
            addressDescription,
            phone,
            email,
            cityId,
            buildingId,
        )


class Warehouse(Building):
    """
    Warehouse Class that Represents a Row from its Remote Table
    """

    def __init__(
        self,
        buildingName: str,
        gpsLatitude: float,
        gpsLongitude: float,
        email: str,
        phone: int,
        cityId: int,
        addressDescription: str,
        buildingId: int = None,
    ):
        """
        Warehouse Class Construtor

        :param str name: Warehouse Building Name
        :param float gpsLatitude: Warehouse GPS Latitude Obtained throguh the Nominatim API
        :param float gpsLongitude: Warehouse GPS Longitude Obtained throguh the Nominatim API
        :param str email: Warehouse Main Email
        :param int phone: Warehouse Main Phone Number
        :param int cityId: City ID at its Remote Table where the Warehouse is Located
        :param str addressDescription: Warehouse Address Description at the Given City
        :param int buildingId: Warehouse ID at its Remote Table. Default is ``None``
        """

        # Initialize Building Class
        super().__init__(
            buildingName,
            gpsLatitude,
            gpsLongitude,
            addressDescription,
            phone,
            email,
            cityId,
            buildingId,
        )

    @classmethod
    def fromFetchedItem(cls, item: tuple):
        """
        Warehouse Classmethod to Initialize a Warehouse Object from the Fetched Item at a Given Query

        :param tuple item: Fetched Row from Warehouse Remote Table
        :return: Warehouse Object
        :rtype: Self@Warehouse
        """

        (
            _,  # Warehouse ID, Same as Building ID
            buildingId,
            email,
            phone,
            gpsLatitude,
            gpsLongitude,
            addressDescription,
            buildingName,
            cityId,
        ) = item

        return cls(
            buildingName,
            gpsLatitude,
            gpsLongitude,
            email,
            phone,
            cityId,
            addressDescription,
            buildingId,
        )


class Branch(Building):
    """
    Branch Class that Represents a Row from its Remote Table
    """

    # Public Fields
    branchId: int = None
    warehouseConnection: int = None
    routeDistance: float = None

    def __init__(
        self,
        buildingName: str,
        gpsLatitude: float,
        gpsLongitude: float,
        email: str,
        phone: int,
        cityId: int,
        addressDescription: str,
        warehouseConnection: int,
        routeDistance: int,
        buildingId: int = None,
    ):
        """
        Branch Class Construtor

        :param str name: Branch Building Name
        :param float gpsLatitude: Branch GPS Latitude Obtained throguh the Nominatim API
        :param float gpsLongitude: Branch GPS Longitude Obtained throguh the Nominatim API
        :param str email: Branch Main Email
        :param int phone: Branch Main Phone Number
        :param int cityId: City ID at its Remote Table where the Branch is Located
        :param str addressDescription: Branch Address Description at the Given City
        :param int warehouseConnection: Warehouse ID that's Connected with the Given Branch
        :param int routeDistance: Driving Distance between the Branch and its Warehouse Connections (in meters)
        :param int buildingId: Branch ID at its Remote Table. Default is ``None``
        """

        # Initialize Building Class
        super().__init__(
            buildingName,
            gpsLatitude,
            gpsLongitude,
            addressDescription,
            phone,
            email,
            cityId,
            buildingId,
        )

        # Set Own Branch Fields
        self.warehouseConnection = warehouseConnection
        self.routeDistance = routeDistance

    @classmethod
    def fromFetchedItem(cls, item: tuple):
        """
        Branch Classmethod to Initialize a Branch Object from the Fetched Item at a Given Query

        :param tuple item: Fetched Row from Branch Remote Table
        :return: Branch Object
        :rtype: Self@Branch
        """

        (
            _,  # Branch ID, Same as Building ID
            warehouseConnection,
            routeDistance,
            buildingId,
            email,
            phone,
            gpsLatitude,
            gpsLongitude,
            addressDescription,
            buildingName,
            cityId,
        ) = item

        return cls(
            buildingName,
            gpsLatitude,
            gpsLongitude,
            email,
            phone,
            cityId,
            addressDescription,
            warehouseConnection,
            routeDistance,
            buildingId,
        )
