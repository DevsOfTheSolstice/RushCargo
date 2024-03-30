CREATE SCHEMA Locations;
CREATE SCHEMA Connections;

--1
CREATE TABLE Locations.Countries (
    country_id SMALLSERIAL PRIMARY KEY,
    country_name VARCHAR(255) UNIQUE NOT NULL,
    phone_prefix SMALLINT NOT NULL
);

--2
CREATE TABLE Locations.Regions (
    region_id SERIAL PRIMARY KEY,
    region_name VARCHAR(255) NOT NULL,
    country_id SMALLINT NOT NULL,
    main_warehouse INT,
    main_air_freight_forwarder INT,
    main_ocean_freight_forwarder INT,
    FOREIGN KEY (country_id) REFERENCES Locations.Countries(country_id)
);

--3
CREATE TABLE Locations.Cities (
    city_id SERIAL PRIMARY KEY,
    city_name VARCHAR(255) NOT NULL,
    region_id INT NOT NULL,
    main_warehouse INT,
    FOREIGN KEY (region_id) REFERENCES Locations.Regions(region_id)
);

--4
CREATE TABLE Locations.Buildings (
    building_id SERIAL PRIMARY KEY,
    building_name VARCHAR(255) NOT NULL,
    gps_latitude DECIMAL(9,6) NOT NULL,  
    gps_longitude DECIMAL(9,6) NOT NULL,
    address_description VARCHAR(255),  
    email VARCHAR(255),  
    phone BIGINT,  
    city_id INT NOT NULL,
    FOREIGN KEY (city_id) REFERENCES Locations.Cities(city_id)
);

--5
CREATE TABLE Locations.Warehouses (
    warehouse_id SERIAL PRIMARY KEY,
    FOREIGN KEY (warehouse_id) REFERENCES Locations.Buildings(building_id)
);

--6
CREATE TABLE Connections.Warehouse_Connections (
    connection_id BIGSERIAL PRIMARY KEY,
    connection_type VARCHAR(255) NOT NULL,
    route_distance BIGINT NOT NULL,
    warehouse_from_id INT NOT NULL,
    warehouse_to_id INT NOT NULL,
    FOREIGN KEY (warehouse_from_id) REFERENCES Locations.Warehouses(warehouse_id),
    FOREIGN KEY (warehouse_to_id) REFERENCES Locations.Warehouses(warehouse_id)
);

--7
CREATE TABLE Locations.Branches (
    branch_id SERIAL PRIMARY KEY,
    route_distance BIGINT NOT NULL,
    warehouse_id INT NOT NULL,
    FOREIGN KEY (branch_id) REFERENCES Locations.Buildings(building_id),
    FOREIGN KEY (warehouse_id) REFERENCES Locations.Warehouses(warehouse_id)
);

--8
CREATE TABLE Legal_Identifications (
    legal_id SERIAL PRIMARY KEY,
    document_description VARCHAR(255) NOT NULL,
    expedition_date DATE NOT NULL,
    identification_type VARCHAR(255) NOT NULL,
    country_id SMALLSERIAL NOT NULL,
    FOREIGN KEY (country_id) REFERENCES Locations.Countries(country_id)
);

--9
CREATE TABLE Allied_Companies (
    company_id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    phone BIGINT,
    employer_id INT NOT NULL,
    FOREIGN KEY (employer_id) REFERENCES Legal_Identifications(legal_id)
);

--10
CREATE TABLE Locations.Allied_Shipping_Offices (
    office_id BIGSERIAL PRIMARY KEY,
    route_distance DECIMAL(4,2) NOT NULL,
    company_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    FOREIGN KEY (office_id) REFERENCES Locations.Buildings(building_id),
    FOREIGN KEY (warehouse_id) REFERENCES Locations.Warehouses(warehouse_id),
    FOREIGN KEY (company_id) REFERENCES Allied_Companies(company_id)
);

--Modifications
ALTER TABLE Locations.Cities
ADD FOREIGN KEY (main_warehouse) REFERENCES Locations.Warehouses(warehouse_id);

ALTER TABLE Locations.Regions
ADD FOREIGN KEY (main_warehouse) REFERENCES Locations.Warehouses(warehouse_id);

