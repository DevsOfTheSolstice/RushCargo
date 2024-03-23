-- Warehouse Buildings
INSERT INTO building (building_id, area_id, gps_latitude, gps_longitude, address_description, building_name)
VALUES (0, 0, 10.5, 20.5, 'Warehouse addr desc 0', 'Osaka North Warehouse');

INSERT INTO building (building_id, area_id, gps_latitude, gps_longitude, address_description, building_name)
VALUES (1, 2, 10.8, 20.8, 'Warehouse addr desc 1', 'Osaka East Warehouse');

INSERT INTO building (building_id, area_id, gps_latitude, gps_longitude, address_description, building_name)
VALUES (2, 3, 20.3, 30.3, 'Warehouse addr desc 2', 'Tokyo West Warehouse');

INSERT INTO building (building_id, area_id, gps_latitude, gps_longitude, address_description, building_name)
VALUES(3, 1, 20.8, 30.8, 'Warehouse addr desc 3', 'Tokyo North Warehouse');

-- Branch Buildings
INSERT INTO building (building_id, area_id, gps_latitude, gps_longitude, address_description, building_name)
VALUES (4, 0, 10.4, 20.4, 'Branch addr desc 0', 'RushCargo Osaka North');

INSERT INTO building (building_id, area_id, gps_latitude, gps_longitude, address_description, building_name)
VALUES (5, 1, 20.7, 30.7, 'Branch addr desc 1', 'RushCargo Tokyo North');

-- Warehouses
INSERT INTO warehouse (warehouse_id) VALUES (0);
INSERT INTO warehouse (warehouse_id) VALUES (1);
INSERT INTO warehouse (warehouse_id) VALUES (2);
INSERT INTO warehouse (warehouse_id) VALUES (3);

-- Branches
INSERT INTO branch (branch_id, warehouse_connection, rute_distance) VALUES (4, 0, 10.0);
INSERT INTO branch (branch_id, warehouse_connection, rute_distance) VALUES (5, 3, 20.0);