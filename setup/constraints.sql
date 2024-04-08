-- Make Unique Country Name
ALTER TABLE Locations.Countries
ADD CONSTRAINT uq_country_name UNIQUE(country_name);

-- Make Unique Region Name per Country
ALTER TABLE Locations.Regions
ADD CONSTRAINT uq_country_region_name UNIQUE (country_id, region_name);

-- Make Unique City Name per Region
ALTER TABLE Locations.Cities
ADD CONSTRAINT uq_region_city_name UNIQUE (region_id, city_name);

-- Make Unique Building Name per City
ALTER TABLE Locations.Buildings
ADD CONSTRAINT uq_city_building_name UNIQUE (city_id, building_name);

-- Make Unique the Warehouse Connections
ALTER TABLE Connections.Warehouse_Connections
ADD CONSTRAINT uq_warehouse_connection UNIQUE (warehouse_from_id, warehouse_to_id, connection_type);