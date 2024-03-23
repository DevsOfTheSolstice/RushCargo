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