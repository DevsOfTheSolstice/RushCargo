-- Locker 1 Packages Descriptions
INSERT INTO shippings.package_descriptions (tracking_number, content, package_value, package_weight, package_lenght, package_width, package_height)
VALUES (0, 'Harina pan', 50.0, 1.0, 2.0, 3.0, 4.0);

INSERT INTO shippings.package_descriptions (tracking_number, content, package_value, package_weight, package_lenght, package_width, package_height)
VALUES (1, 'Caraotas', 80.0, 2.0, 3.0, 4.0, 5.0);

INSERT INTO shippings.package_descriptions (tracking_number, content, package_value, package_weight, package_lenght, package_width, package_height)
VALUES (3, 'Bomba nuclear HS724 Uranio-38', 999.0, 90.0, 2.0, 3.0, 4.0);

INSERT INTO shippings.package_descriptions (tracking_number, content, package_value, package_weight, package_lenght, package_width, package_height)
VALUES (4, 'Daniel Carrizo', 1.0, 80000.0, 2.0, 3.0, 4.0);

INSERT INTO shippings.package_descriptions (tracking_number, content, package_value, package_weight, package_lenght, package_width, package_height)
VALUES (5, 'Sadam Hussein', 1.0, 65000.0, 2.0, 3.0, 4.0);

INSERT INTO shippings.package_descriptions (tracking_number, content, package_value, package_weight, package_lenght, package_width, package_height)
VALUES (6, '938436 naranjas', 1.0, 65000.0, 2.0, 3.0, 4.0);

INSERT INTO shippings.package_descriptions (tracking_number, content, package_value, package_weight, package_lenght, package_width, package_height)
VALUES (7, 'Cocaina 99.9% pura', 999.0, 10.0, 2.0, 3.0, 4.0);

-- Locker 1 Packages
INSERT INTO shippings.packages (tracking_number, admin_verification, holder, building_id, locker_id, register_date, register_hour, delivered)
VALUES (0, 'admin0', 'dojimanoryu', 31, 0, '2024-03-20', '10:30:00', true);

INSERT INTO shippings.packages (tracking_number, admin_verification, holder, building_id, locker_id, register_date, register_hour, delivered)
VALUES (1, 'admin0', 'dojimanoryu', 31, 0, '2024-03-20', '10:30:00', true);

INSERT INTO shippings.packages (tracking_number, admin_verification, holder, building_id, locker_id, register_date, register_hour, delivered)
VALUES (2, 'admin0', 'dojimanoryu', 31, 0, '2024-03-20', '10:30:00', true);

INSERT INTO shippings.packages (tracking_number, admin_verification, holder, building_id, locker_id, register_date, register_hour, delivered)
VALUES (3, 'admin0', 'dojimanoryu', 31, 0, '2024-03-20', '10:30:00', true);

INSERT INTO shippings.packages (tracking_number, admin_verification, holder, building_id, locker_id, register_date, register_hour, delivered)
VALUES (4, 'admin0', 'dojimanoryu', 31, 0, '2024-03-20', '10:30:00', true);

INSERT INTO shippings.packages (tracking_number, admin_verification, holder, building_id, locker_id, register_date, register_hour, delivered)
VALUES (5, 'admin0', 'dojimanoryu', 31, 0, '2024-03-20', '10:30:00', true);

INSERT INTO shippings.packages (tracking_number, admin_verification, holder, building_id, locker_id, register_date, register_hour, delivered)
VALUES (6, 'admin0', 'dojimanoryu', 31, 0, '2024-03-20', '10:30:00', true);

-- Locker 2 Packages Descriptions
INSERT INTO shippings.package_descriptions (tracking_number, content, package_value, package_weight, package_lenght, package_width, package_height)
VALUES (2, 'Arroz', 90.0, 3.0, 4.0, 5.0, 6.0);

-- Locker 2 Packages
INSERT INTO shippings.packages (tracking_number, admin_verification, holder, building_id, locker_id, register_date, register_hour, delivered)
VALUES (2, 'admin1', 'maddog', 40, 1, '2024-03-20', '10:30:00', true);