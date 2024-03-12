--1
ALTER TABLE Country
ADD CONSTRAINT uq_country_name UNIQUE(country_name)
ADD CONSTRAINT uq_phone_prefix UNIQUE(phone_prefix);