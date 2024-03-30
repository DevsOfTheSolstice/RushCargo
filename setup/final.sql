CREATE SCHEMA locations;
CREATE SCHEMA connections;

--1
CREATE TABLE locations.Country (
    country_id BIGSERIAL PRIMARY KEY,
    country_name VARCHAR(50) UNIQUE NOT NULL,
    phone_prefix VARCHAR(50) UNIQUE NOT NULL
);

--2
CREATE TABLE locations.Region (
    region_id BIGSERIAL PRIMARY KEY,
    country_id BIGINT,
    region_name VARCHAR(50) NOT NULL,
    main_warehouse BIGINT,
    main_air_freight_forwarder BIGINT,
    main_ocean_freight_forwarder BIGINT,
    FOREIGN KEY (country_id) REFERENCES locations.Country(country_id)
);

--3
CREATE TABLE locations.City (
    city_id BIGSERIAL PRIMARY KEY,
    city_name VARCHAR(255) NOT NULL,
    region_id BIGSERIAL NOT NULL,
    main_warehouse BIGINT,
    FOREIGN KEY (region_id) REFERENCES locations.Region(region_id)
);

--4
CREATE TABLE locations.Building (
    building_id BIGSERIAL PRIMARY KEY,
    city_id BIGINT,
    address_description VARCHAR(255) NOT NULL,  
    building_name VARCHAR(50) NOT NULL,
    email VARCHAR(255),  
    phone VARCHAR(20),  
    gps_latitude DECIMAL(9,6),  
    gps_longitude DECIMAL(9,6),
    FOREIGN KEY (city_id) REFERENCES locations.City(city_id)
);

--5
CREATE TABLE locations.Warehouse (
    warehouse_id BIGSERIAL PRIMARY KEY,
    FOREIGN KEY (warehouse_id) REFERENCES locations.Building(building_id)
);

--6
CREATE TABLE connections.Warehouse_Connection (
    connection_id BIGSERIAL PRIMARY KEY,
    warehouse_from_id BIGINT,
    warehouse_to_id BIGINT,
    route_distance INT NOT NULL,
    connection_type VARCHAR(50) NOT NULL,
    FOREIGN KEY (warehouse_from_id) REFERENCES locations.Warehouse(warehouse_id),
    FOREIGN KEY (warehouse_to_id) REFERENCES locations.Warehouse(warehouse_id)
);

--7
CREATE TABLE locations.Branch (
    branch_id BIGSERIAL PRIMARY KEY,
    warehouse_id BIGINT,
    route_distance INT NOT NULL,
    FOREIGN KEY (branch_id) REFERENCES locations.Building(building_id),
    FOREIGN KEY (warehouse_id) REFERENCES locations.Warehouse(warehouse_id)
);

--8
CREATE TABLE Legal_Identification (
    id VARCHAR(255) PRIMARY KEY,
    country_id BIGSERIAL,
    document VARCHAR(255) NOT NULL,
    due_date DATE NOT NULL,
    expedition_date DATE NOT NULL,
    identification_type VARCHAR(255),
    FOREIGN KEY (country_id) REFERENCES locations.Country(country_id)
);

--9
CREATE TABLE Allied_Company (
    company_id INT PRIMARY KEY,
    email VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    gps_latitude DECIMAL(9,6),
    gps_longitude DECIMAL(9,6),
    fiscal_record_id VARCHAR(255),
    FOREIGN KEY (fiscal_record_id) REFERENCES Legal_Identification(id)
);

--10
CREATE TABLE locations.Allied_Shipping_Office (
    office_id BIGSERIAL PRIMARY KEY,
    warehouse_connection BIGSERIAL,
    affiliated_company BIGSERIAL,
    route_distance DECIMAL(4,2) NOT NULL,
    type VARCHAR(255) NOT NULL,
    FOREIGN KEY (office_id) REFERENCES locations.Building(building_id),
    FOREIGN KEY (warehouse_connection) REFERENCES connections.Warehouse_Connection(connection_id),
    FOREIGN KEY (affiliated_company) REFERENCES Allied_Company(company_id)
);
--Modifications
ALTER TABLE locations.City
ADD FOREIGN KEY (main_warehouse) REFERENCES locations.Warehouse(warehouse_id);

ALTER TABLE locations.Region
ADD FOREIGN KEY (main_warehouse) REFERENCES locations.Warehouse(warehouse_id);

