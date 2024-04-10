-- Warehouse Buildings
INSERT INTO locations.buildings (building_id, city_id, gps_latitude, gps_longitude, address_description, building_name)
VALUES (0, 0, 10.5, 20.5, 'Warehouse addr desc 0', 'Osaka Warehouse');

INSERT INTO locations.buildings (building_id, city_id, gps_latitude, gps_longitude, address_description, building_name)
VALUES (1, 1, 10.8, 20.8, 'Warehouse addr desc 1', 'Tokyo Warehouse');

INSERT INTO locations.buildings (building_id, city_id, gps_latitude, gps_longitude, address_description, building_name)
VALUES (2, 2, 20.3, 30.3, 'Warehouse addr desc 2', 'Okinawa Warehouse');

INSERT INTO locations.buildings (building_id, city_id, gps_latitude, gps_longitude, address_description, building_name)
VALUES (3, 3, 20.3, 30.5, 'Warehouse addr desc 2', 'Fukuoka Warehouse');

-- Branch Buildings
INSERT INTO locations.buildings (building_id, city_id, gps_latitude, gps_longitude, address_description, building_name)
VALUES (4, 0, 10.4, 20.4, 'Branch addr desc 0', 'RushCargo Osaka');

INSERT INTO locations.buildings (building_id, city_id, gps_latitude, gps_longitude, address_description, building_name)
VALUES (5, 1, 20.7, 30.7, 'Branch addr desc 1', 'RushCargo Tokyo');

-- Warehouses
INSERT INTO locations.warehouses (warehouse_id) VALUES (0);
INSERT INTO locations.warehouses (warehouse_id) VALUES (1);
INSERT INTO locations.warehouses (warehouse_id) VALUES (2);
INSERT INTO locations.warehouses (warehouse_id) VALUES (3);

-- Branches
INSERT INTO locations.branches (branch_id, warehouse_id, route_distance) VALUES (4, 0, 10.0);
INSERT INTO locations.branches (branch_id, warehouse_id, route_distance) VALUES (5, 1, 20.0);