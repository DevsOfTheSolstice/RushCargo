-- Make Unique Country Name
ALTER TABLE Country
ADD CONSTRAINT uq_country_name UNIQUE(country_name);

-- Make Unique Province Name per Country
ALTER TABLE Province
ADD CONSTRAINT uq_country_province UNIQUE (country_id, province_name);

-- Make Unique Region Name per Province
ALTER TABLE Region
ADD CONSTRAINT uq_province_region UNIQUE (province_id, region_name);

-- Make Unique City Name per Region
ALTER TABLE City
ADD CONSTRAINT uq_region_city UNIQUE (region_id, city_name);

-- Make Unique City Area Name per City
ALTER TABLE City_Area
ADD CONSTRAINT uq_city_city_area UNIQUE (city_id, area_name);

-- Make Unique Building Name per City Area
ALTER TABLE Building
ADD CONSTRAINT uq_city_area_building UNIQUE (area_id, building_name)
