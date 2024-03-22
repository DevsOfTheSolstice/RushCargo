-- Country 1
INSERT INTO country (country_id, country_name, phone_prefix) VALUES (0, 'Japan', '+81');

-- Region, Subr, City, City Area 1
INSERT INTO region (region_id, country_id, region_name) VALUES (0, 0, 'Kansai');
INSERT INTO subregion (subregion_id, region_id, subregion_name) VALUES (0, 0, 'Kansai_Subr');
INSERT INTO city (city_id, subregion_id, city_name) VALUES (0, 0, 'Osaka');
INSERT INTO city_area (area_id, city_id, area_name) VALUES (0, 0, 'Osaka North');

-- Region, Subr, City, City Area 2
INSERT INTO region (region_id, country_id, region_name) VALUES (1, 0, 'Kanto');
INSERT INTO subregion (subregion_id, region_id, subregion_name) VALUES (1, 1, 'Kanto_Subr');
INSERT INTO city (city_id, subregion_id, city_name) VALUES (1, 1, 'Tokyo');
INSERT INTO city_area (area_id, city_id, area_name) VALUES (1, 1, 'Tokyo North');

-- City Area 3
INSERT INTO city_area (area_id, city_id, area_name) VALUES (2, 0, 'Osaka East');

-- City Area 4
INSERT INTO city_area (area_id, city_id, area_name) VALUES (3, 1, 'Tokyo West');

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

-- User 1
INSERT INTO users (username, user_password, phone, gps_address)
-- Psswd: dojimanoryu
VALUES ('dojimanoryu', '$2a$04$sLU7NqIQuZVh2XxNQ9RTT.x1HcmE.SoVK/QLXGOw0u/WNWBwyO3dy', '043-939-7851', 'User 0 gps addr');

-- User 2
INSERT INTO users (username, user_password, phone, gps_address)
-- Psswd: maddog
VALUES ('maddog', '$2a$04$wpGe03I/o1wiyibNzIA3VeCKCI6NReTJUVVXxT6K8jZgZang8rcoa', '078-213-0385', 'User 1 gps addr');

-- Client 1
INSERT INTO client (username, branch) VALUES ('dojimanoryu', 4);

-- Client 2
INSERT INTO client (username, branch) VALUES ('maddog', 5);

-- Natural Client 1
INSERT INTO natural_client (username, born_date, client_name, last_name, affiliated_branch, route_distance)
VALUES ('dojimanoryu', '1968-06-17', 'Kiryu', 'Kazuma', 4, 15.0);

-- Natural Client 1
INSERT INTO natural_client (username, born_date, client_name, last_name, affiliated_branch, route_distance)
VALUES ('maddog', '1964-05-14', 'Goro', 'Majima', 5, 25.0);

-- Locker 1
INSERT INTO locker (locker_id, client, country_id, warehouse_id)
VALUES (0, 'dojimanoryu', 0, 0);

-- Locker 2
INSERT INTO locker (locker_id, client, country_id, warehouse_id)
VALUES (1, 'maddog', 0, 3);

-- Legal identifications
INSERT INTO legal_identification (id, country_id, document, due_date, expedition_date)
VALUES (0, 0, 'Legal identification 0', '2024-12-01', '2022-12-01');

INSERT INTO legal_identification (id, country_id, document, due_date, expedition_date)
VALUES (1, 0, 'Legal identification 1', '2024-12-01', '2022-12-01');

-- Admins
INSERT INTO root_user (username, warehouse_id, identity_document, user_password)
-- Passwd: admin0
VALUES ('admin0', 0, 0, '$2a$04$9LHD8K3Icib7/x89QSKOCO1nH2fNH43hj7nd/cob3ZMKwYj2v9edq');

INSERT INTO root_user (username, warehouse_id, identity_document, user_password)
-- Passwd: admin1
VALUES ('admin1', 3, 1, '$2a$04$33X714FkR6Ddmfh8zlZYLuEu5caLY2glCFmoF3dyes74.f0Ff/Okq');

-- Locker 1 Packages
INSERT INTO package (tracking_number, admin_verification, building_id, locker_id, register_date, register_hour)
VALUES (0, 'admin0', 0, 0, '2024-03-20', '10:30:00');

INSERT INTO package (tracking_number, admin_verification, building_id, locker_id, register_date, register_hour)
VALUES (1, 'admin0', 0, 0, '2024-03-20', '10:30:00');

-- Locker 1 Packages Descriptions
INSERT INTO package_description (tracking_number, content, package_value, package_weight, package_lenght, package_width, package_height, delivered)
VALUES (0, 'Package 0 Locker 1', 50.0, 1.0, 2.0, 3.0, 4.0, true);

INSERT INTO package_description (tracking_number, content, package_value, package_weight, package_lenght, package_width, package_height, delivered)
VALUES (1, 'Package 1 Locker 1', 80.0, 2.0, 3.0, 4.0, 5.0, true);

-- Locker 2 Packages
INSERT INTO package (tracking_number, admin_verification, building_id, locker_id, register_date, register_hour)
VALUES (2, 'admin1', 3, 1, '2024-03-20', '10:30:00');

-- Locker 2 Packages Descriptions
INSERT INTO package_description (tracking_number, content, package_value, package_weight, package_lenght, package_width, package_height, delivered)
VALUES (2, 'Package 0 Locker 2', 90.0, 3.0, 4.0, 5.0, 6.0, true);

-- Repeated: country_id on locker