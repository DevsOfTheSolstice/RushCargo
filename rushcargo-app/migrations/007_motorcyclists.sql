INSERT into vehicle (vin_vehicle, brand, model, weight_capacity, width_capacity, height_capacity, length_capacity, vehicle_type)
VALUES ('AAAABBBBCCCCDDDDE', 'Harley Davidson', 'Sportser 883', 99.0, 40.0, 40.0, 40.0, 'Motorcycle');

INSERT INTO users (username, user_password, phone, gps_address)
VALUES ('yukari', '$2a$04$bBZVzWcAa2u13VIBAbjePur6fP0NhRJHeT5yzNjamxnmI40Re/kAS', '000111222', 'gps address');

INSERT INTO driver (username, born_date, first_name, last_name, salary)
VALUES ('yukari', '1998-05-01', 'Yukari', 'Tanizaki', 99.0);

INSERT INTO motorcyclist (username, motorcycle, assigned_branch)
VALUES ('yukari','AAAABBBBCCCC', 4);