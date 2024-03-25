--1
CREATE VIEW Country_Warehouses AS
SELECT country.country_id, province.province_id, region.region_id, city.city_id, area.area_id, warehouse.warehouse_id
FROM Country AS country INNER JOIN PROVINCE AS province ON country.country_id = province.country_id
INNER JOIN Region AS region ON province.province_id = region.province_id
INNER JOIN City AS city ON region.region_id = city.region_id
INNER JOIN City_Area AS area ON city.city_id = area.city_id
INNER JOIN Building AS building ON area.area_id = building.area_id
INNER JOIN Warehouse AS warehouse ON building.building_id = warehouse.warehouse_id;

--2
CREATE VIEW Country_Warehouse_Receivers AS
SELECT warehouses.*, warehouse_conn.connection_id  FROM Country_Warehouses AS warehouses INNER JOIN Warehouse_Connection AS warehouse_conn ON warehouses.warehouse_id =warehouse_conn.warehouse_to_id;

--3
CREATE VIEW Country_Warehouse_Senders AS
SELECT warehouses.*, warehouse_conn.connection_id  FROM Country_Warehouses AS warehouses INNER JOIN Warehouse_Connection AS warehouse_conn ON warehouses.warehouse_id =warehouse_conn.warehouse_from_id;