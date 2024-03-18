-- Make Unique Country Name and Country Phone Prefix
ALTER TABLE Country
ADD CONSTRAINT uq_country_name UNIQUE(country_name)
ADD CONSTRAINT uq_phone_prefix UNIQUE(phone_prefix);

-- Make Unique Region Name per Country
ALTER TABLE Region
ADD CONSTRAINT uq_country_region UNIQUE (country_id, region_name);

-- Make Unique Subregion Name per Region
ALTER TABLE Subregion
ADD CONSTRAINT uq_region_subregion UNIQUE (region_id, subregion_name);

-- Make Unique City Name per Subregion
ALTER TABLE City
ADD CONSTRAINT uq_subregion_city UNIQUE (subregion_id, city_name);

-- Make Unique City Area Name per City
ALTER TABLE City_Area
ADD CONSTRAINT uq_city_city_area UNIQUE (city_id, area_name);
