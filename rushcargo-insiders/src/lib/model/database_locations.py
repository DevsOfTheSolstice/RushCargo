from .database import *


# Country Table Class
class CountryTable(BasicTable):
    # Constructor
    def __init__(self, database: Database):
        # Initialize Basic Table Class
        super().__init__(COUNTRY_TABLENAME, database)

    # Print Items
    def __print(self) -> None:
        c = None

        # Number of Items
        nItems = len(self._items)

        # No Results
        if nItems == 0:
            noCoincidenceFetched()
            return

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

        # Print New Line
        console.print("\n")

        # Print Table
        console.print(table)

    # Get Insert Query
    def __getInsertQuery(self):
        return sql.SQL("INSERT INTO {tableName} ({fields}) VALUES (%s, %s)").format(
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [sql.Identifier(COUNTRY_NAME), sql.Identifier(COUNTRY_PHONE_PREFIX)]
            ),
        )

    # Insert Country to Table
    def add(self, c: Country) -> None:
        # Get Query
        query = self.__getInsertQuery()

        # Execute Query
        try:
            self.c.execute(query, [c.name, c.phonePrefix])
            console.print(
                f"{c.name} Successfully Inserted to {self._tableName} Table",
                style="success",
            )
        except Exception as err:
            raise err

    # Insert Multiple Countries to Table
    def addMany(self, countries: list[Country]) -> None:
        # Get Query
        query = self.__getInsertQuery()

        countriesTuple = []
        countriesName = []

        # Create Tuples List from Countries List, and Countries Name List
        for c in countries:
            countriesTuple.append([c.name, c.phonePrefix])
            countriesName.append(c.name)

        # Execute Query
        try:
            extras.execute_values(
                self.c, query.as_string(self.c), countriesTuple, page_size=100
            )
            console.print(
                f"{' '.join(countriesName)} Successfully Inserted to {self._tableName} Table",
                style="success",
            )
        except Exception as err:
            raise err

    # Filter Items from Country Table
    def get(self, field: str, value, printItems: bool = True) -> bool:
        if not BasicTable._get(self, field, value):
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
        if not self._get(field, value):
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
        BasicTable._modify(self, COUNTRY_ID, countryId, field, value)

    # Remove Row from Country Table
    def remove(self, countryId: int) -> None:
        BasicTable._remove(self, COUNTRY_ID, countryId)


# Region Table Class
class RegionTable(BasicTable):
    # Constructor
    def __init__(self, database: Database):
        # Initialize Basic Table Class
        super().__init__(REGION_TABLENAME, database)

    # Print Items
    def __print(self) -> None:
        r = None

        # Number of Items
        nItems = len(self._items)

        # No Results
        if nItems == 0:
            noCoincidenceFetched()
            return

        # Initialize Rich Table
        table = getTable("Region", nItems)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Country ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Air Forwarder ID", justify="left", max_width=FORWARDER_NCHAR)
        table.add_column(
            "Ocean Forwarder ID", justify="left", max_width=FORWARDER_NCHAR
        )

        # Loop Over Items
        for item in self._items:
            # Intialize Region from Item Fetched
            r = Region.fromItemFetched(item)

            # Add Row to Rich Table
            table.add_row(
                str(r.regionId),
                str(r.countryId),
                r.name,
                str(r.airForwarderId),
                str(r.oceanForwarderId),
            )

        # Print New Line
        console.print("\n")

        # Print Table
        console.print(table)

    # Get Insert Query
    def __getInsertQuery(self):
        return sql.SQL("INSERT INTO {tableName} ({fields}) VALUES (%s, %s)").format(
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [sql.Identifier(REGION_FK_COUNTRY), sql.Identifier(REGION_NAME)]
            ),
        )

    # Insert Region to Table
    def add(self, r: Region) -> None:
        # Get Query
        query = self.__getInsertQuery()

        # Execute Query
        try:
            self.c.execute(query, [r.countryId, r.name])
            console.print(
                f"{r.name} Successfully Inserted to {self._tableName} Table",
                style="success",
            )
        except Exception as err:
            raise err

    # Insert Multiple Regions to Table
    def addMany(self, regions: list[Region]) -> None:
        # Get Query
        query = self.__getInsertQuery()

        regionsTuple = []
        regionsName = []

        # Create Tuples List from Regions List, and Regions Name List
        for r in regions:
            regionsTuple.append([r.countryId, r.name])
            regionsName.append(r.name)

        # Execute Query
        try:
            extras.execute_values(
                self.c, query.as_string(self.c), regionsTuple, page_size=100
            )
            console.print(
                f"{' '.join(regionsName)} Successfully Inserted to {self._tableName} Table",
                style="success",
            )
        except Exception as err:
            raise err

    # Filter Items from Region Table
    def get(self, field: str, value, printItems: bool = True) -> bool:
        if not BasicTable._get(self, field, value):
            return False

        # Print Items
        if printItems:
            self.__print()
        return True

    # Filter Items with Multiple Conditions from Region Table
    def getMult(self, field: list[str], value: list, printItems: bool = True) -> bool:
        if not BasicTable._getMult(self, field, value):
            return False

        # Print Items
        if printItems:
            self.__print()
        return True

    # Find Region from Region Table
    def find(self, countryId: int, regionName: str) -> Region | None:
        """
        Returns Region Object if it was Found. Otherwise, False
        """

        # Get Region
        if not self.getMult(
            [REGION_FK_COUNTRY, REGION_NAME], [countryId, regionName], False
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
        BasicTable._modify(self, REGION_ID, regionId, field, value)

    # Remove Row from Region Table
    def remove(self, regionId: int) -> None:
        BasicTable._remove(self, REGION_ID, regionId)


# City Table Class
class CityTable(BasicTable):
    # Constructor
    def __init__(self, database: Database):
        # Initialize Basic Table Class
        super().__init__(CITY_TABLENAME, database)

    # Print Items
    def __print(self) -> None:
        c = None

        # Number of Items
        nItems = len(self._items)

        # No Results
        if nItems == 0:
            noCoincidenceFetched()
            return

        # Initialize Rich Table
        table = getTable("City", nItems)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Region ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Warehouse ID", justify="left", max_width=WAREHOUSE_NCHAR)

        # Loop Over Items
        for item in self._items:
            # Intialize Region from Item Fetched
            c = City.fromItemFetched(item)

            # Add Row to Rich Table
            table.add_row(str(c.cityId), str(c.regionId), c.name, str(c.warehouseId))

        # Print New Line
        console.print("\n")

        # Print Table
        console.print(table)

    # Get Insert Query
    def __getInsertQuery(self):
        return sql.SQL("INSERT INTO {tableName} ({fields}) VALUES (%s, %s)").format(
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [sql.Identifier(CITY_FK_REGION), sql.Identifier(CITY_NAME)]
            ),
        )

    # Insert City to Table
    def add(self, c: City) -> None:
        # Get Query
        query = self.__getInsertQuery()

        # Execute Query
        try:
            self.c.execute(query, [c.regionId, c.name])
            console.print(
                f"{c.name} Successfully Inserted to {self._tableName} Table",
                style="success",
            )
        except Exception as err:
            raise err

    # Insert Multiple Cities to Table
    def addMany(self, cities: list[City]) -> None:
        # Get Query
        query = self.__getInsertQuery()

        citiesTuple = []
        citiesName = []

        # Create Tuples List from Cities List, and Cities Name List
        for c in cities:
            citiesTuple.append([c.regionId, c.name])
            citiesName.append(c.name)

        # Execute Query
        try:
            extras.execute_values(
                self.c, query.as_string(self.c), citiesTuple, page_size=100
            )
            console.print(
                f"{' '.join(citiesName)} Successfully Inserted to {self._tableName} Table",
                style="success",
            )
        except Exception as err:
            raise err

    # Filter Items from City Table
    def get(self, field: str, value, printItems: bool = True) -> bool:
        if not BasicTable._get(self, field, value):
            return False

        # Print Items
        if printItems:
            self.__print()
        return True

    # Filter Items with Multiple Conditions from City Table
    def getMult(self, field: list[str], value: list, printItems: bool = True) -> bool:
        if not BasicTable._getMult(self, field, value):
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
        BasicTable._modify(self, CITY_ID, cityId, field, value)

    # Remove Row from City Table
    def remove(self, cityId: int) -> None:
        BasicTable._remove(self, CITY_ID, cityId)


# City Area Table Class
class CityAreaTable(BasicTable):
    # Constructor
    def __init__(self, database: Database):
        # Initialize Basic Table Class
        super().__init__(CITY_AREA_TABLENAME, database)

    # Print Items
    def __print(self) -> None:
        a = None

        # Number of Items
        nItems = len(self._items)

        # No Results
        if nItems == 0:
            noCoincidenceFetched()
            return

        # Initialize Rich Table
        table = getTable("City", nItems)

        # Add Table Columns
        table.add_column("ID", justify="left", max_width=ID_NCHAR)
        table.add_column("City ID", justify="left", max_width=ID_NCHAR)
        table.add_column("Name", justify="left", max_width=LOCATION_NAME_NCHAR)
        table.add_column("Description", justify="left", max_width=DESCRIPTION_NCHAR)

        # Loop Over Items
        for item in self._items:
            # Intialize Region from Item Fetched
            a = CityArea.fromItemFetched(item)

            # Add Row to Rich Table
            table.add_row(str(a.areaId), str(a.cityId), a.areaName, a.areaDescription)

        # Print New Line
        console.print("\n")

        # Print Table
        console.print(table)

    # Get Insert Query
    def __getInsertQuery(self):
        return sql.SQL("INSERT INTO {tableName} ({fields}) VALUES (%s, %s)").format(
            tableName=sql.Identifier(self._tableName),
            fields=sql.SQL(",").join(
                [sql.Identifier(CITY_AREA_FK_CITY), sql.Identifier(CITY_AREA_NAME)]
            ),
        )

    # Insert City Area to Table
    def add(self, a: CityArea) -> None:
        # Get Query
        query = self.__getInsertQuery()

        # Execute Query
        try:
            self.c.execute(query, [a.cityId, a.areaName])
            console.print(
                f"{a.areaName} Successfully Inserted to {self._tableName} Table",
                style="success",
            )
        except Exception as err:
            raise err

    # Insert Multiple City Areas to Table
    def addMany(self, areas: list[City]) -> None:
        # Get Query
        query = self.__getInsertQuery()

        areasTuple = []
        areasName = []

        # Create Tuples List from City Areas List, and City Areas Name List
        for a in areas:
            areasTuple.append([a.regionId, a.name])
            areasName.append(a.name)

        # Execute Query
        try:
            extras.execute_values(
                self.c, query.as_string(self.c), areasTuple, page_size=100
            )
            console.print(
                f"{' '.join(areasName)} Successfully Inserted to {self._tableName} Table",
                style="success",
            )
        except Exception as err:
            raise err

    # Filter Items from City Areas Table
    def get(self, field: str, value, printItems: bool = True) -> bool:
        if not BasicTable._get(self, field, value):
            return False

        # Print Items
        if printItems:
            self.__print()
        return True

    # Filter Items with Multiple Conditions from City Areas Table
    def getMult(self, field: list[str], value: list, printItems: bool = True) -> bool:
        if not BasicTable._getMult(self, field, value):
            return False

        # Print Items
        if printItems:
            self.__print()
        return True

    # Get All Items from City Area Table
    def all(self, orderBy: str, desc: bool) -> None:
        BasicTable._all(self, orderBy, desc)

        # Print Items
        self.__print()

    # Modify Row from City Area Table
    def modify(self, areaId: int, field: str, value) -> None:
        BasicTable._modify(self, CITY_AREA_ID, areaId, field, value)

    # Remove Row from City Area Table
    def remove(self, areaId: int) -> None:
        BasicTable._remove(self, CITY_AREA_ID, areaId)
