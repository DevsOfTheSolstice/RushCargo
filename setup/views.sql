--1
CREATE VIEW Warehouses AS
SELECT country.country_id, province.province_id, region.region_id, city.city_id, building.gps_latitude,building.gps_longitude,warehouse.warehouse_id
FROM Country AS country INNER JOIN PROVINCE AS province ON country.country_id = province.country_id
INNER JOIN Region AS region ON province.province_id = region.province_id
INNER JOIN City AS city ON region.region_id = city.region_id
INNER JOIN Building AS building ON city.city_id = building.city_id
INNER JOIN Warehouse AS warehouse ON building.building_id = warehouse.warehouse_id;

--2
CREATE VIEW Warehouse_Receivers AS
SELECT warehouses.*, warehouse_conn.connection_id, warehouse_conn.connection_type  FROM Warehouses AS warehouses INNER JOIN Warehouse_Connection AS warehouse_conn ON warehouses.warehouse_id =warehouse_conn.warehouse_to_id;

--3
CREATE VIEW Warehouse_Senders AS
SELECT warehouses.*, warehouse_conn.connection_id, warehouse_conn.connection_type  FROM Warehouses AS warehouses INNER JOIN Warehouse_Connection AS warehouse_conn ON warehouses.warehouse_id =warehouse_conn.warehouse_from_id;

--4
CREATE VIEW Province_Main_Warehouses AS
SELECT warehouses.* FROM Warehouses AS warehouses INNER JOIN Province AS province ON province.main_warehouse = warehouses.warehouse_id;

--5
CREATE VIEW Region_Main_Warehouses AS
SELECT warehouses.* FROM Warehouses AS warehouses INNER JOIN Region AS region ON region.main_warehouse = warehouses.warehouse_id;

--6
CREATE VIEW City_Main_Warehouses AS
SELECT warehouses.* FROM Warehouses AS warehouses INNER JOIN City AS city ON city.main_warehouse = warehouses.warehouse_id;



