from psycopg import sql

from .classes import Country, Province, Region, City, CityArea
from .constants import *
from .database import Database, console
from .database_tables import (
    BasicTable,
    noCoincidenceFetched,
    insertedRow,
    getTable,
)


# Country Table Class
class CountryTable(BasicTable):
    # Constructor
    def __init__(self, database: Database):
        # Initialize Basic Table Class
        super().__init__(COUNTRY_TABLENAME, COUNTRY_ID, database)

    # Print Items
    def __print(self) -> None:
        c = None

        # Number of Items
        nItems = len(self._items)

        # Initialize Rich Table
        table = getTable("Country", nItems)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Phone Prefix", justify="left", max_width=PHONE_PREFIX_NCHAR)

        # Loop Over Items
        for item in self._items:
            # Intialize Country from Item Fetched
            c = Country.fromItemFetched(item)

            # Add Row to Rich Table
            table.add_row(str(c.countryId), c.name, str(c.phonePrefix))

        # Print Table
        console.print(table)

    # Returns Country Insert Query
    def __insertQuery(self):
        return sql.SQL("INSERT INTO {tableName} ({fields}) VALUES (%s, %s)").format(
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [sql.Identifier(COUNTRY_NAME), sql.Identifier(COUNTRY_PHONE_PREFIX)]
            ),
        )

    # Insert Country to Table
    def add(self, c: Country) -> None:
        # Get Query
        query = self.__insertQuery()

        # Execute Query
        try:
            self._c.execute(query, [c.name, c.phonePrefix])

            console.print(
                insertedRow(c.name, self._tableName),
                style="success",
            )

        except Exception as err:
            raise err

    # Filter Items from Country Table
    def get(self, field: str, value, printItems: bool = True) -> bool:
        if not BasicTable._get(self, field, value):
            if printItems:
                noCoincidenceFetched()
            return False

        # Print Items
        if printItems:
            self.__print()
        return True

    # Find Country from Country Table
    def find(self, field: str, value) -> Country | None:
        """
        Returns Country Object if it was Found. Otherwise, False

        NOTE: All Columns from this Table Contain Unique Values
        """

        # Get Country
        if not self.get(field, value, False):
            return None

        # Get Country Object from Item Fetched
        return Country.fromItemFetched(self._items[0])

    # Get All Items from Country Table
    def all(self, orderBy: str, desc: bool) -> None:
        BasicTable._all(self, orderBy, desc)

        # Print Items
        self.__print()

    # Modify Row from Country Table
    def modify(self, countryId: int, field: str, value) -> None:
        BasicTable._modify(self, countryId, field, value)

    # Remove Row from Country Table
    def remove(self, countryId: int) -> None:
        BasicTable._remove(self, countryId)


# Province Table Class
class ProvinceTable(BasicTable):
    # Constructor
    def __init__(self, database: Database):
        # Initialize Basic Table Class
        super().__init__(PROVINCE_TABLENAME, PROVINCE_ID, database)

    # Print Items
    def __print(self) -> None:
        p = None

        # Number of Items
        nItems = len(self._items)

        # Initialize Rich Table
        table = getTable("Province", nItems)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Country ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Air Forwarder ID", justify="left", max_width=FORWARDER_NCHAR)
        table.add_column(
            "Ocean Forwarder ID", justify="left", max_width=FORWARDER_NCHAR
        )

        # Loop Over Items
        for item in self._items:
            # Intialize Province from Item Fetched
            p = Province.fromItemFetched(item)

            # Add Row to Rich Table
            table.add_row(
                str(p.provinceId),
                p.name,
                str(p.countryId),
                str(p.airForwarderId),
                str(p.oceanForwarderId),
            )

        # Print Table
        console.print(table)

    # Returns Province Insert Query
    def __insertQuery(self):
        return sql.SQL("INSERT INTO {tableName} ({fields}) VALUES (%s, %s)").format(
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [sql.Identifier(PROVINCE_FK_COUNTRY), sql.Identifier(PROVINCE_NAME)]
            ),
        )

    # Insert Province to Table
    def add(self, p: Province) -> None:
        # Get Query
        query = self.__insertQuery()

        # Execute Query
        try:
            self._c.execute(query, [p.countryId, p.name])

            console.print(
                insertedRow(p.name, self._tableName),
                style="success",
            )

        except Exception as err:
            raise err

    # Filter Items from Province Table
    def get(self, field: str, value, printItems: bool = True) -> bool:
        if not BasicTable._get(self, field, value):
            if printItems:
                noCoincidenceFetched()
            return False

        # Print Items
        if printItems:
            self.__print()
        return True

    # Filter Items with Multiple Conditions from Province Table
    def getMult(self, fields: list[str], values: list, printItems: bool = True) -> bool:
        if not BasicTable._getMult(self, fields, values):
            if printItems:
                noCoincidenceFetched()
            return False

        # Print Items
        if printItems:
            self.__print()
        return True

    # Find Province from Province Table
    def find(self, countryId: int, provinceName: str) -> Province | None:
        """
        Returns Province Object if it was Found. Otherwise, False
        """

        # Get Province
        if not self.getMult(
            [PROVINCE_FK_COUNTRY, PROVINCE_NAME], [countryId, provinceName], False
        ):
            return None

        # Get Province Object from Item Fetched
        return Province.fromItemFetched(self._items[0])

    # Get All Items from Province Table
    def all(self, orderBy: str, desc: bool) -> None:
        BasicTable._all(self, orderBy, desc)

        # Print Items
        self.__print()

    # Modify Row from Province Table
    def modify(self, provinceId: int, field: str, value) -> None:
        BasicTable._modify(self, provinceId, field, value)

    # Remove Row from Province Table
    def remove(self, provinceId: int) -> None:
        BasicTable._remove(self, provinceId)


# Region Table Class
class RegionTable(BasicTable):
    # Constructor
    def __init__(self, database: Database):
        # Initialize Basic Table Class
        super().__init__(REGION_TABLENAME, REGION_ID, database)

    # Print Items
    def __print(self) -> None:
        r = None

        # Number of Items
        nItems = len(self._items)

        # Initialize Rich Table
        table = getTable("Region", nItems)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Province ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Warehouse ID", justify="left", max_width=WAREHOUSE_NCHAR)

        # Loop Over Items
        for item in self._items:
            # Intialize Region from Item Fetched
            r = Region.fromItemFetched(item)

            # Add Row to Rich Table
            table.add_row(
                str(r.regionId), r.name, str(r.provinceId), str(r.warehouseId)
            )

        # Print Table
        console.print(table)

    # Returns Region Insert Query
    def __insertQuery(self):
        return sql.SQL("INSERT INTO {tableName} ({fields}) VALUES (%s, %s)").format(
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [sql.Identifier(REGION_FK_PROVINCE), sql.Identifier(REGION_NAME)]
            ),
        )

    # Insert Region to Table
    def add(self, r: Region) -> None:
        # Get Query
        query = self.__insertQuery()

        # Execute Query
        try:
            self._c.execute(query, [r.provinceId, r.name])
            console.print(
                insertedRow(r.name, self._tableName),
                style="success",
            )

        except Exception as err:
            raise err

    # Filter Items from Region Table
    def get(self, field: str, value, printItems: bool = True) -> bool:
        if not BasicTable._get(self, field, value):
            if printItems:
                noCoincidenceFetched()
            return False

        # Print Items
        if printItems:
            self.__print()
        return True

    # Filter Items with Multiple Conditions from Region Table
    def getMult(self, fields: list[str], values: list, printItems: bool = True) -> bool:
        if not BasicTable._getMult(self, fields, values):
            if printItems:
                noCoincidenceFetched()
            return False

        # Print Items
        if printItems:
            self.__print()
        return True

    # Find Region from Region Table
    def find(self, provinceId: int, regionName: str) -> Region | None:
        """
        Returns Region Object if it was Found. Otherwise, False
        """

        # Get Region
        if not self.getMult(
            [REGION_FK_PROVINCE, REGION_NAME], [provinceId, regionName], False
        ):
            return None

        # Get Region Object from Item Fetched
        return Region.fromItemFetched(self._items[0])

    # Get All Items from Region Table
    def all(self, orderBy: str, desc: bool) -> None:
        BasicTable._all(self, orderBy, desc)

        # Print Items
        self.__print()

    # Modify Row from Region Table
    def modify(self, regionId: int, field: str, value) -> None:
        BasicTable._modify(self, regionId, field, value)

    # Remove Row from Region Table
    def remove(self, regionId: int) -> None:
        BasicTable._remove(self, regionId)


# City Table Class
class CityTable(BasicTable):
    # Constructor
    def __init__(self, database: Database):
        # Initialize Basic Table Class
        super().__init__(CITY_TABLENAME, CITY_ID, database)

    # Print Items
    def __print(self) -> None:
        c = None

        # Number of Items
        nItems = len(self._items)

        # Initialize Rich Table
        table = getTable("City", nItems)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Region ID", justify="left", max_width=ID_NCHAR)

        # Loop Over Items
        for item in self._items:
            # Intialize City from Item Fetched
            c = City.fromItemFetched(item)

            # Add Row to Rich Table
            table.add_row(str(c.cityId), c.name, str(c.regionId))

        # Print Table
        console.print(table)

    # Returns City Insert Query
    def __insertQuery(self):
        return sql.SQL("INSERT INTO {tableName} ({fields}) VALUES (%s, %s)").format(
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [sql.Identifier(CITY_FK_REGION), sql.Identifier(CITY_NAME)]
            ),
        )

    # Insert City to Table
    def add(self, c: City) -> None:
        # Get Query
        query = self.__insertQuery()

        # Execute Query
        try:
            self._c.execute(query, [c.regionId, c.name])
            console.print(
                insertedRow(c.name, self._tableName),
                style="success",
            )

        except Exception as err:
            raise err

    # Filter Items from City Table
    def get(self, field: str, value, printItems: bool = True) -> bool:
        if not BasicTable._get(self, field, value):
            if printItems:
                noCoincidenceFetched()
            return False

        # Print Items
        if printItems:
            self.__print()
        return True

    # Filter Items with Multiple Conditions from City Table
    def getMult(self, fields: list[str], values: list, printItems: bool = True) -> bool:
        if not BasicTable._getMult(self, fields, values):
            if printItems:
                noCoincidenceFetched()
            return False

        # Print Items
        if printItems:
            self.__print()
        return True

    # Find City from City Table
    def find(self, regionId: int, cityName: str) -> City | None:
        """
        Returns City Object if it was Found. Otherwise, False
        """

        # Get City
        if not self.getMult([CITY_FK_REGION, CITY_NAME], [regionId, cityName], False):
            return None

        # Get City Object from Item Fetched
        return City.fromItemFetched(self._items[0])

    # Get All Items from City Table
    def all(self, orderBy: str, desc: bool) -> None:
        BasicTable._all(self, orderBy, desc)

        # Print Items
        self.__print()

    # Modify Row from City Table
    def modify(self, cityId: int, field: str, value) -> None:
        BasicTable._modify(self, cityId, field, value)

    # Remove Row from City Table
    def remove(self, cityId: int) -> None:
        BasicTable._remove(self, cityId)


# City Area Table Class
class CityAreaTable(BasicTable):
    # Constructor
    def __init__(self, database: Database):
        # Initialize Basic Table Class
        super().__init__(CITY_AREA_TABLENAME, CITY_AREA_ID, database)

    # Print Items
    def __print(self) -> None:
        a = None

        # Number of Items
        nItems = len(self._items)

        # Initialize Rich Table
        table = getTable("City", nItems)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Description", justify="left", max_width=DESCRIPTION_NCHAR)
        table.add_column("City ID", justify="left", max_width=ID_NCHAR)

        # Loop Over Items
        for item in self._items:
            # Intialize City Area from Item Fetched
            a = CityArea.fromItemFetched(item)

            # Add Row to Rich Table
            table.add_row(str(a.areaId), a.areaName, a.areaDescription, str(a.cityId))

        # Print Table
        console.print(table)

    # Returns City Area Insert Query
    def __insertQuery(self):
        return sql.SQL("INSERT INTO {tableName} ({fields}) VALUES (%s, %s)").format(
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [sql.Identifier(CITY_AREA_FK_CITY), sql.Identifier(CITY_AREA_NAME)]
            ),
        )

    # Insert City Area to Table
    def add(self, a: CityArea) -> None:
        # Get Query
        query = self.__insertQuery()

        # Execute Query
        try:
            self._c.execute(query, [a.cityId, a.areaName])
            console.print(
                insertedRow(a.areaName, self._tableName),
                style="success",
            )

        except Exception as err:
            raise err

    # Filter Items from City Areas Table
    def get(self, field: str, value, printItems: bool = True) -> bool:
        if not BasicTable._get(self, field, value):
            if printItems:
                noCoincidenceFetched()
            return False

        # Print Items
        if printItems:
            self.__print()
        return True

    # Filter Items with Multiple Conditions from City Areas Table
    def getMult(self, fields: list[str], values: list, printItems: bool = True) -> bool:
        if not BasicTable._getMult(self, fields, values):
            if printItems:
                noCoincidenceFetched()
            return False

        # Print Items
        if printItems:
            self.__print()
        return True

    # Find City Area from City Area Table
    def find(self, cityId: int, areaName: str) -> City | None:
        """
        Returns City Area Object if it was Found. Otherwise, False
        """

        # Get City Area
        if not self.getMult(
            [CITY_AREA_FK_CITY, CITY_AREA_NAME], [cityId, areaName], False
        ):
            return None

        # Get City Area Object from Item Fetched
        return CityArea.fromItemFetched(self._items[0])

    # Get All Items from City Area Table
    def all(self, orderBy: str, desc: bool) -> None:
        BasicTable._all(self, orderBy, desc)

        # Print Items
        self.__print()

    # Modify Row from City Area Table
    def modify(self, areaId: int, field: str, value) -> None:
        BasicTable._modify(self, areaId, field, value)

    # Remove Row from City Area Table
    def remove(self, areaId: int) -> None:
        BasicTable._remove(self, areaId)
