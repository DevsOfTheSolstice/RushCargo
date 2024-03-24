from rich.prompt import Prompt, IntPrompt, Confirm

from .constants import *
from .exceptions import BuildingFound, WarehouseNotFound, InvalidWarehouse
from .territoryEvents import territoryEventHandler

from ..geocoding.geopy import (
    NOMINATIM_LATITUDE,
    NOMINATIM_LONGITUDE,
)
from ..geocoding.routingpy import routingPyGeocoder

from ..io.constants import (
    ADD,
    RM,
    ALL,
    GET,
    MOD,
)
from ..io.validator import *

from ..model.database import db
from ..model.database_tables import uniqueInsertedMult
from ..model.database_building import *

# Building Event Handler
buildingEventHandler = None


# Building Table-related Event Handler
class BuildingEventHandler:
    # Table Classes
    _warehouseTable = None
    _branchTable = None

    # Get Location Messages
    _getBuildingMsg = "\nEnter Building Name"

    # Constructor
    def __init__(self, db: Database):
        # Initialize Table Classes
        self._warehouseTable = WarehouseTable(db)
        self._branchTable = BranchTable(db)

    # Check if Building Exists
    def __buildingExists(self, areaId: str, buildingName: str) -> bool:
        buildingFields = [BUILDING_FK_CITY_AREA, BUILDING_NAME]
        buildingValues = [areaId, buildingName]

        # Check if Building Name has already been Inserted for the City Area
        if self._warehouseTable._getMultParentTable(buildingFields, buildingValues):
            uniqueInsertedMult(buildingValues, buildingFields, buildingValues)
            return

    # Returns Building Type Corresponding for the Given Table
    def __buildingType(self, tableName: str) -> str:
        if tableName == WAREHOUSE_TABLENAME:
            return "Warehouse"

        elif tableName == BRANCH_TABLENAME:
            return "Branch"

    # Ask for Building Common Fields
    def __askBuildingFields(
        self,
        tableName: str,
        buildingType: str,
        areaId: int,
    ) -> None | tuple[str, int, str, str]:
        # Get Building Name
        buildingName = Prompt.ask(f"Enter {buildingType} Name")

        # Check Building Name
        isAddressValid(tableName, BUILDING_NAME, buildingName)

        # Get Building Complete Name
        buildingName = self.__buildingName(buildingType, buildingName)

        # Check if Building Name for the Given City Area Already Exists
        if self.__buildingExists(areaId, buildingName):
            console.print(
                f"There's a Building Named as '{buildingName}' in '{areaId}'",
                style="warning",
            )
            raise BuildingFound(buildingName, areaId)

        # Get New Building Fields
        buildingPhone = Prompt.ask(f"Enter {buildingType} Phone Number")
        buildingEmail = Prompt.ask(f"Enter {buildingType} Email")
        addressDescription = Prompt.ask(f"Enter {buildingType} Address Description")

        # Check Building Warehouse Name, Phone, Email and Description
        isPhoneValid(tableName, BUILDING_PHONE, buildingPhone)
        isEmailValid(buildingEmail)
        isAddressValid(tableName, BUILDING_ADDRESS_DESCRIPTION, addressDescription)

        return buildingName, buildingPhone, buildingEmail, addressDescription

    # Ask for Building Common Values
    def __askBuildingValue(self, buildingType: str, field: str):
        if field == BUILDING_PHONE:
            value = str(IntPrompt.ask(MOD_VALUE_MSG))

        elif field == BUILDING_EMAIL:
            value = Prompt.ask(MOD_VALUE_MSG)

            # Check Building Email and Get its Normalized Form
            value = isEmailValid(value)

        elif field == BUILDING_NAME:
            value = Prompt.ask(MOD_VALUE_MSG)

            # Check Building Name
            isAddressValid(BUILDING_TABLENAME, field, value)

            # Get Building Complete Name
            value = self.__buildingName(buildingType, value)

        # Not a Building Table Column
        else:
            return None

        return value

    # Returns Complete Building Name
    def __buildingName(self, buildingType: str, buildingName: str) -> str:
        return f"{buildingType} {buildingName}"

    # Returns Warehouse Connection ID and Route Distance
    def __getWarehouseConnection(
        self, areaId: int, coords: dict
    ) -> None | tuple[int, int]:
        # Clear Terminal
        clear()

        # Initialize Warehouse Coordinates Dictionary
        warehouseCoords = {}

        # Print Warehouses at the Given City Area
        if not self._warehouseTable.get(BUILDING_FK_CITY_AREA, areaId):
            raise WarehouseNotFound(areaId)

        while True:
            try:
                # Select Branch Warehouse Connection for the Given City Area
                warehouseId = IntPrompt.ask("Select the Warehouse Connection")

                # Get Warehouse Object
                warehouse = self._warehouseTable.find(warehouseId)

                # Check if Warehouse ID Exists and is in the Given City Area
                if warehouse == None or warehouse.areaId != areaId:
                    raise InvalidWarehouse(areaId)

                # Get Warehouse Coordinates
                warehouseCoords[NOMINATIM_LATITUDE] = warehouse.gpsLatitude
                warehouseCoords[NOMINATIM_LONGITUDE] = warehouse.gpsLongitude

                break

            except Exception as err:
                console.print(err, style="warning")
                continue

        # Calculate Route Distance
        routeDistance = routingPyGeocoder.getRouteDistance(warehouseCoords, coords)

        return warehouseId, routeDistance

    # Get All Table Handler
    def _allHandler(self, tableName: str) -> None:
        sortBy = None

        # Asks if the User wants to Print it in Descending Order
        desc = Confirm.ask(ALL_DESC_MSG)

        if tableName == WAREHOUSE_TABLENAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                ALL_SORT_BY_MSG,
                choices=[WAREHOUSE_ID, BUILDING_NAME, BUILDING_FK_CITY_AREA],
            )

            # Clear Terminal
            clear()

            # Print Table
            self._warehouseTable.all(sortBy, desc)

        elif tableName == BRANCH_TABLENAME:
            # Ask the Sort Order
            sortBy = Prompt.ask(
                ALL_SORT_BY_MSG,
                choices=[
                    BRANCH_ID,
                    BRANCH_FK_WAREHOUSE_CONNECTION,
                    BRANCH_ROUTE_DISTANCE,
                    BUILDING_NAME,
                    BUILDING_FK_CITY_AREA,
                ],
            )

            # Clear Terminal
            clear()

            # Print Table
            self._branchTable.all(sortBy, desc)

    # Get Table Handler
    def _getHandler(self, tableName: str) -> None:
        field = value = None

        if tableName == WAREHOUSE_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                GET_FIELD_MSG,
                choices=[
                    WAREHOUSE_ID,
                    BUILDING_NAME,
                    BUILDING_PHONE,
                    BUILDING_FK_CITY_AREA,
                ],
            )

            # Prompt to Ask the Value to be Compared
            if field == BUILDING_NAME:
                value = Prompt.ask(GET_VALUE_MSG)

                # Check Value
                isAddressValid(tableName, field, value)

            else:
                value = str(IntPrompt.ask(GET_VALUE_MSG))

            # Clear Terminal
            clear()

            # Print Table Coincidences
            self._warehouseTable.get(field, value)

        elif tableName == BRANCH_TABLENAME:
            # Asks for Field to Compare
            field = Prompt.ask(
                GET_FIELD_MSG,
                choices=[
                    BRANCH_ID,
                    BRANCH_FK_WAREHOUSE_CONNECTION,
                    BUILDING_NAME,
                    BUILDING_PHONE,
                    BUILDING_FK_CITY_AREA,
                ],
            )

            # Prompt to Ask the Value to be Compared
            if field == BUILDING_NAME:
                value = Prompt.ask(GET_VALUE_MSG)

                # Check Value
                isAddressValid(tableName, field, value)

            else:
                value = str(IntPrompt.ask(GET_VALUE_MSG))

            # Clear Terminal
            clear()

            # Print Table Coincidences
            self._branchTable.get(field, value)

    # Modify Row from Table Handler
    def _modHandler(self, tableName: str) -> None:
        field = value = None
        warehouseId = None

        # Get Building Type
        buildingType = self.__buildingType(tableName)

        if tableName == WAREHOUSE_TABLENAME:
            # Ask for Warehouse ID to Modify
            warehouseId = IntPrompt.ask("\nEnter Warehouse ID to Modify")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._warehouseTable.get(WAREHOUSE_ID, warehouseId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(MOD_CONFIRM_MSG):
                return

            # Ask for Field to Modify
            field = Prompt.ask(
                MOD_FIELD_MSG,
                choices=[BUILDING_NAME, BUILDING_PHONE, BUILDING_EMAIL],
            )

            # Prompt to Ask the New Value
            value = self.__askBuildingValue(buildingType, field)

            # Modify Warehouse
            self._warehouseTable.modify(warehouseId, field, value)

        elif tableName == BRANCH_TABLENAME:
            # Ask for Branch ID to Modify
            branchId = IntPrompt.ask("\nEnter Branch ID to Modify")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._branchTable.get(BRANCH_ID, branchId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(MOD_CONFIRM_MSG):
                return

            # Ask for Field to Modify
            field = Prompt.ask(
                MOD_FIELD_MSG,
                choices=[
                    BRANCH_FK_WAREHOUSE_CONNECTION,
                    BUILDING_NAME,
                    BUILDING_PHONE,
                    BUILDING_EMAIL,
                ],
            )

            # Prompt to Ask the New Value
            if field != BRANCH_FK_WAREHOUSE_CONNECTION:
                value = self.__askBuildingValue(buildingType, field)

                # Modify Branch
                self._branchTable.modify(branchId, field, value)

            else:
                # Get Branch Object
                branch = self._branchTable.find(branchId)

                # Get City Area ID where the Branch is Located
                areaId = branch.areaId

                # Get Branch Coordinate
                coords = {
                    NOMINATIM_LATITUDE: branch.gpsLatitude,
                    NOMINATIM_LONGITUDE: branch.gpsLongitude,
                }

                # Get New Warehouse Connection ID and Route Distance
                warehouseId, routeDistance = self.__getWarehouseConnection(
                    areaId, coords
                )

                # Modify Branch
                self._branchTable.modify(
                    branchId, BRANCH_FK_WAREHOUSE_CONNECTION, warehouseId
                )
                self._branchTable.modify(branchId, BRANCH_ROUTE_DISTANCE, routeDistance)

    # Add Row to Table Handler
    def _addHandler(self, tableName: str) -> None:
        # Coordinates Dictionary
        coords = None

        # Get Building Type
        buildingType = self.__buildingType(tableName)

        while True:
            # Asks for Building Fields
            if coords == None:
                coords = territoryEventHandler.getPlaceCoordinates(
                    f"Enter Place Name Near to {buildingType}"
                )

            # Get City Area ID and Coordinates
            areaId = coords[DICT_CITY_AREA_ID]

            # Get Building Fields
            buildingFields = self.__askBuildingFields(tableName, buildingType, areaId)

            buildingName, buildingPhone, buildingEmail, addressDescription = (
                buildingFields
            )

            if tableName == WAREHOUSE_TABLENAME:
                # Insert Warehouse
                self._warehouseTable.add(
                    Warehouse(
                        buildingName,
                        coords[NOMINATIM_LATITUDE],
                        coords[NOMINATIM_LONGITUDE],
                        buildingEmail,
                        buildingPhone,
                        areaId,
                        addressDescription,
                    )
                )

            elif tableName == BRANCH_TABLENAME:
                # Get New Warehouse Connection ID and Route Distance
                warehouseId, routeDistance = self.__getWarehouseConnection(
                    areaId, coords
                )

                # Insert Branch
                self._branchTable.add(
                    Branch(
                        buildingName,
                        coords[NOMINATIM_LATITUDE],
                        coords[NOMINATIM_LONGITUDE],
                        buildingEmail,
                        buildingPhone,
                        areaId,
                        addressDescription,
                        warehouseId,
                        routeDistance,
                    )
                )

            # Ask to Add More
            if not Confirm.ask(ADD_MORE_MSG):
                break

    # Remove Row from Table Handler
    def _rmHandler(self, tableName: str) -> None:
        if tableName == WAREHOUSE_TABLENAME:
            # Ask for Warehouse ID to Remove
            warehouseId = IntPrompt.ask("\nEnter Warehouse ID to Remove")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._warehouseTable.get(WAREHOUSE_ID, warehouseId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            self._warehouseTable.remove(warehouseId)

        elif tableName == BRANCH_TABLENAME:
            # Ask for Branch ID to Remove
            branchId = IntPrompt.ask("\nEnter Branch ID to Remove")

            # Clear Terminal
            clear()

            # Print Fetched Results
            if not self._branchTable.get(BRANCH_ID, branchId):
                noCoincidenceFetched()
                return

            # Ask for Confirmation
            if not Confirm.ask(RM_CONFIRM_MSG):
                return

            self._branchTable.remove(branchId)

    # Building Event Handler
    def handler(self, action: str, tableName: str) -> None:
        # Clear Terminal
        clear()

        if action == ALL:
            self._allHandler(tableName)

        elif action == GET:
            self._getHandler(tableName)

        elif action == MOD:
            self._modHandler(tableName)

        elif action == ADD:
            self._addHandler(tableName)

        elif action == RM:
            self._rmHandler(tableName)


# Initialize Building Event Handler
buildingEventHandler = BuildingEventHandler(db)
