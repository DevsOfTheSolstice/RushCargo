--1
CREATE TABLE Country (
    country_id BIGSERIAL PRIMARY KEY,
    country_name VARCHAR(50) UNIQUE NOT NULL,
    phone_prefix VARCHAR(50) UNIQUE NOT NULL
);

--2
CREATE TABLE Province (
    province_id BIGSERIAL PRIMARY KEY,
    country_id BIGINT,
    province_name VARCHAR(50) NOT NULL,
    main_warehouse BIGINT,
    main_air_freight_forwarder BIGINT,
    main_ocean_freight_forwarder BIGINT,
    FOREIGN KEY (country_id) REFERENCES Country(country_id)
);

--3
CREATE TABLE Region (
    region_id BIGSERIAL PRIMARY KEY,
    province_id BIGINT,
    region_name VARCHAR(50) NOT NULL,
    main_warehouse BIGINT,
    FOREIGN KEY (province_id) REFERENCES Province(province_id)
);

--4
CREATE TABLE City (
    city_id BIGSERIAL PRIMARY KEY,
    city_name VARCHAR(255) NOT NULL,
    region_id BIGSERIAL NOT NULL,
    main_warehouse BIGINT,
    FOREIGN KEY (region_id) REFERENCES Region(region_id)
);

--5
CREATE TABLE City_Area ( 
    area_id BIGSERIAL PRIMARY KEY, 
    city_id BIGINT, 
    area_name VARCHAR(255) NOT NULL, 
    area_description VARCHAR(255),
    main_warehouse BIGINT,
    FOREIGN KEY (city_id) REFERENCES City(city_id) 
);

--6
CREATE TABLE Building (
    building_id BIGSERIAL PRIMARY KEY,
    area_id BIGINT,
    address_description VARCHAR(255) NOT NULL;  
    building_name VARCHAR(50) NOT NULL; 
    email VARCHAR(255),  
    phone VARCHAR(20),  
    gps_latitude DECIMAL(9,6),  
    gps_longitude DECIMAL(9,6);
    FOREIGN KEY (area_id) REFERENCES City_Area(area_id)
);

--7
CREATE TABLE Warehouse (
    warehouse_id BIGSERIAL PRIMARY KEY,
    FOREIGN KEY (warehouse_id) REFERENCES Building(building_id)
);

--8
CREATE TABLE Warehouse_Connection (
    connection_id BIGSERIAL PRIMARY KEY,
    warehouse_from_id BIGINT,
    warehouse_to_id BIGINT,
    route_distance INT NOT NULL,
    connection_type VARCHAR(50) NOT NULL,
    FOREIGN KEY (warehouse_from_id) REFERENCES Warehouse(warehouse_id),
    FOREIGN KEY (warehouse_to_id) REFERENCES Warehouse(warehouse_id)
);

--9
CREATE TABLE Branch (
    branch_id BIGSERIAL PRIMARY KEY,
    warehouse_id BIGINT,
    route_distance INT NOT NULL,
    FOREIGN KEY (branch_id) REFERENCES Building(building_id),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(warehouse_id)
);

--Modifications
ALTER TABLE City_Area
ADD FOREIGN KEY (main_warehouse) REFERENCES Warehouse(warehouse_id);

ALTER TABLE City
ADD FOREIGN KEY (main_warehouse) REFERENCES Warehouse(warehouse_id);

ALTER TABLE Region
ADD FOREIGN KEY (main_warehouse) REFERENCES Warehouse(warehouse_id);

ALTER TABLE Province
ADD FOREIGN KEY (main_warehouse) REFERENCES Warehouse(warehouse_id);