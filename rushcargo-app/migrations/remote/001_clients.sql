-- User 1
INSERT INTO users.users (username, user_password, phone, gps_address)
-- Psswd: dojimanoryu
VALUES ('dojimanoryu', '$2a$04$sLU7NqIQuZVh2XxNQ9RTT.x1HcmE.SoVK/QLXGOw0u/WNWBwyO3dy', '043-939-7851', 'User 0 gps addr');

-- User 2
INSERT INTO users.users (username, user_password, phone, gps_address)
-- Psswd: maddog
VALUES ('maddog', '$2a$04$wpGe03I/o1wiyibNzIA3VeCKCI6NReTJUVVXxT6K8jZgZang8rcoa', '078-213-0385', 'User 1 gps addr');

-- Client 1
INSERT INTO users.clients (username) VALUES ('dojimanoryu');

-- Client 2
INSERT INTO users.clients (username) VALUES ('maddog');

-- Natural Client 1
INSERT INTO users.natural_clients (username, birthdate, first_name, last_name, address_description, affiliated_branch)
VALUES ('dojimanoryu', '1968-06-17', 'Kiryu', 'Kazuma', 'client1 addr desc', 51);

-- Natural Client 1
INSERT INTO users.natural_clients (username, birthdate, first_name, last_name, address_description, affiliated_branch)
VALUES ('maddog', '1964-05-14', 'Goro', 'Majima', 'client2 addr desc', 52);