--Trucker 1
INSERT INTO users(username, user_password, phone, gps_address)
-- Psswd: truckkun
VALUES ('truckkun', '$2a$04$O92l.J5pMKVCILfRt4po7usSE2k2B5f3D8/YWa7punDeUHYLv6jX6', '076-743-7463', 'User 3 gps addr');

INSERT INTO driver (username, born_date, first_name, last_name, salary)
VALUES ('truckkun', '1999-5-4', 'isekai', 'maker', '93');

INSERT INTO vehicle (vin_vehicle, brand, model, weight_capacity, width_capacity, height_capacity, length_capacity, vehicle_type)
VALUES ('3N1CN7APXEL805651', 'Fuso', 'FE130', '3.50', '6', '3.40', '10.50', 'Truck');

INSERT INTO truck_driver (username, truck)
VALUES ('truckkun', '3N1CN7APXEL805651');
