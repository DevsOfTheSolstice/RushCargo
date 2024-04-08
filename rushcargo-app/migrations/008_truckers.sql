INSERT INTO Vehicles.Vehicles (vin_vehicle, brand, model, weight_capacity, width_capacity, height_capacity, length_capacity, vehicle_type)
VALUES ('3N1CN7APXEL805651', 'Fuso', 'FE130', '3.50', '6', '3.40', '10.50', 'Truck');

--Trucker 1
INSERT INTO Users.Users(username, user_password, phone, gps_address)
-- Psswd: truckkun
VALUES ('truckkun', '$2a$04$O92l.J5pMKVCILfRt4po7usSE2k2B5f3D8/YWa7punDeUHYLv6jX6', '076-743-7463', 'gps address');

INSERT INTO Companies.Legal_Identifications (legal_id, country_id, document_description, expedition_date, identification_type)
VALUES (59, 0, 'Legal identification 59', '2022-12-02', 'DriverID');

INSERT INTO Vehicles.Drivers (username, born_date, first_name, last_name, salary, id_document)
VALUES ('truckkun', '1999-5-4', 'isekai', 'maker', '93', '59');

INSERT INTO Vehicles.Truckers (username, truck, affiliated_warehouse)
VALUES ('truckkun', '3N1CN7APXEL805651', 0);
