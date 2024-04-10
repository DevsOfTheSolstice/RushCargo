-- Country 1
INSERT INTO locations.countries (country_id, country_name, phone_prefix) VALUES (0, 'Japan', 81);

-- Region, Subr, City, City Area 1
INSERT INTO locations.regions (region_id, country_id, region_name) VALUES (0, 0, 'Kansai');
INSERT INTO locations.cities (city_id, region_id, city_name) VALUES (0, 0, 'Osaka');

-- Region, Subr, City, City Area 2
INSERT INTO locations.regions (region_id, country_id, region_name) VALUES (1, 0, 'Kanto');
INSERT INTO locations.cities (city_id, region_id, city_name) VALUES (1, 1, 'Tokyo');

INSERT INTO locations.regions (region_id, country_id, region_name) VALUES (2, 0, 'Kyushu');
INSERT INTO locations.cities (city_id, region_id, city_name) VALUES (2, 2, 'Okinawa');
INSERT INTO locations.cities (city_id, region_id, city_name) VALUES (3, 2, 'Fukuoka');