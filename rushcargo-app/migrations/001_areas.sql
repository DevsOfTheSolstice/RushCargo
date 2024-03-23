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