INSERT into vehicles.vehicles (vin_vehicle, brand, model, weight_capacity, width_capacity, height_capacity, length_capacity, vehicle_type)
VALUES ('AAAABBBBCCCCDDDDE', 'Harley Davidson', 'Sportser 883', 99.0, 40.0, 40.0, 40.0, 'Motorcycle');

INSERT INTO users.users (username, user_password, phone, gps_address)
VALUES ('yukari', '$2a$04$bBZVzWcAa2u13VIBAbjePur6fP0NhRJHeT5yzNjamxnmI40Re/kAS', '000111222', 'gps address');

INSERT INTO legal_identifications (legal_id, country_id, document_description, expedition_date, identification_type)
VALUES (2, 0, 'Legal identification 2', '2022-12-01', 'DriverID');

INSERT INTO vehicles.drivers (username, born_date, first_name, last_name, salary, id_document)
VALUES ('yukari', '1998-05-01', 'Yukari', 'Tanizaki', 99.0, 2);

INSERT INTO vehicles.motorcyclists (username, motorcycle, affiliated_branch)
VALUES ('yukari','AAAABBBBCCCCDDDDE', 4);