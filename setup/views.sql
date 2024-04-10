--1
CREATE VIEW Connections.Warehouses AS
SELECT countries.country_id,countries.country_name, regions.region_id,regions.region_name, cities.city_id, cities.city_name, buildings.gps_latitude,buildings.gps_longitude,buildings.building_name,warehouses.warehouse_id
FROM Locations.Countries AS countries INNER JOIN Locations.Regions AS regions ON countries.country_id = regions.country_id
INNER JOIN Locations.Cities AS cities ON regions.region_id = cities.region_id
INNER JOIN Locations.Buildings AS buildings ON cities.city_id = buildings.city_id
INNER JOIN Locations.Warehouses AS warehouses ON buildings.building_id = warehouses.warehouse_id;

--2
CREATE VIEW Connections.Warehouse_Receivers AS
SELECT warehouses.*, warehouse_conns.connection_id, warehouse_conns.connection_type  FROM Connections.Warehouses AS warehouses INNER JOIN Connections.Warehouse_Connections AS warehouse_conns ON warehouses.warehouse_id =warehouse_conns.warehouse_to_id;

--3
CREATE VIEW Connections.Warehouse_Senders AS
SELECT warehouses.*, warehouse_conns.connection_id, warehouse_conns.connection_type  FROM Connections.Warehouses AS warehouses INNER JOIN Connections.Warehouse_Connections AS warehouse_conns ON warehouses.warehouse_id =warehouse_conns.warehouse_from_id;

--4
CREATE VIEW Connections.Region_Main_Warehouses AS
SELECT warehouses.* FROM Connections.Warehouses AS warehouses INNER JOIN Locations.Regions AS regions ON regions.main_warehouse = warehouses.warehouse_id;

--5
CREATE VIEW Connections.City_Main_Warehouses AS
SELECT warehouses.* FROM Connections.Warehouses AS warehouses INNER JOIN Locations.Cities AS cities ON cities.main_warehouse = warehouses.warehouse_id;


