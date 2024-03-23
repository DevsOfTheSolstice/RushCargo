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