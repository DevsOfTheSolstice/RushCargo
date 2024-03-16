-- Make Unique Country Name and Country Phone Prefix
ALTER TABLE Country
ADD CONSTRAINT uq_country_name UNIQUE(country_name)
ADD CONSTRAINT uq_phone_prefix UNIQUE(phone_prefix);

-- Make Unique Region Name per Country
ALTER TABLE Region
ADD CONSTRAINT uq_country_region UNIQUE (country_id, region_name);

-- Make Unique City Name per Region
ALTER TABLE City
ADD CONSTRAINT uq_region_city UNIQUE (region_id, city_name);
