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

-- Modifications
ALTER TABLE Locations.Regions
ADD FOREIGN KEY (main_warehouse) REFERENCES Locations.Warehouses(warehouse_id);

ALTER TABLE Locations.Cities
ADD FOREIGN KEY (main_warehouse) REFERENCES Locations.Warehouses(warehouse_id);

---vvv PROTOTYPE vvv---

--7
CREATE TABLE Vehicles (
    vin_vehicle VARCHAR(17) PRIMARY KEY,
    brand VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,
    weight_capacity DECIMAL(7, 2) NOT NULL,
    width_capacity DECIMAL(7, 2) NOT NULL,
    height_capacity DECIMAL(7, 2) NOT NULL,
    length_capacity DECIMAL(7, 2) NOT NULL,
    vehicle_type VARCHAR(255) NOT NULL
);

--17
CREATE TABLE Root_Users (
    username VARCHAR(255) PRIMARY KEY,
    id_document INT NOT NULL,
    warehouse_id BIGSERIAL NOT NULL,
    user_password VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    birthdate DATE,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    -- should be 'PkgAdmin' or 'UsrAdmin'
    user_type VARCHAR(20) NOT NULL,
    FOREIGN KEY (id_document) REFERENCES Legal_Identifications(legal_id),
    FOREIGN KEY (warehouse_id) REFERENCES locations.Warehouses(warehouse_id)
);

--21
CREATE TABLE Users (
    username VARCHAR(255) PRIMARY KEY,
    admin_verification VARCHAR(255),
    admin_suspension VARCHAR(255),
    user_password VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    gps_address VARCHAR(255) NOT NULL,
    FOREIGN KEY (admin_verification) REFERENCES Root_Users(username),
    FOREIGN KEY (admin_suspension) REFERENCES Root_Users(username)
);

--22
CREATE TABLE Drivers (
    username VARCHAR(255) PRIMARY KEY,
    id_document INT NOT NULL,
    born_date DATE NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    salary DECIMAL(7,2) NOT NULL,
    FOREIGN KEY (username) REFERENCES Users(username),
    FOREIGN KEY (id_document) REFERENCES Legal_Identifications(legal_id)
);

--23
CREATE TABLE Motorcyclists (
    username VARCHAR(255) PRIMARY KEY,
    motorcycle VARCHAR(17),
    affiliated_branch BIGINT NOT NULL,
    FOREIGN KEY (username) REFERENCES Drivers(username),
    FOREIGN KEY (motorcycle) REFERENCES Vehicles(vin_vehicle),
    FOREIGN KEY (affiliated_branch) REFERENCES locations.Branches(branch_id)
);

--24
CREATE TABLE Truckers (
    username VARCHAR(255) PRIMARY KEY,
    truck VARCHAR(17),
    affiliated_warehouse BIGINT NOT NULL,
    FOREIGN KEY (username) REFERENCES Drivers(username),
    FOREIGN KEY (truck) REFERENCES Vehicles(vin_vehicle),
    FOREIGN KEY (affiliated_warehouse) REFERENCES locations.Warehouses(warehouse_id)
);

--25 
CREATE TABLE Clients (
    username VARCHAR(255) PRIMARY KEY,
    FOREIGN KEY (username) REFERENCES Users(username)
);

--26
CREATE TABLE Client_Debts (
    username VARCHAR(255) PRIMARY KEY,
    debt DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (username) REFERENCES Clients(username)
);

--27
CREATE TABLE Natural_Clients (
    username VARCHAR(255) PRIMARY KEY,
    affiliated_branch INT NOT NULL,
    birthdate DATE NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    address_description VARCHAR (255) NOT NULL,
    FOREIGN KEY (username) REFERENCES Clients(username),
    FOREIGN KEY (affiliated_branch) REFERENCES locations.Branches(branch_id)
);

--28
CREATE TABLE Legal_Clients (
    username VARCHAR(255) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    company_type VARCHAR(255) NOT NULL,
    FOREIGN KEY (username) REFERENCES Clients(username)
);

--8
CREATE TABLE Legal_Client_Affiliations (
    affiliation_id BIGSERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    affiliated_branch BIGINT NOT NULL,
    gps_address VARCHAR(255) NOT NULL,
    FOREIGN KEY (username) REFERENCES Legal_Clients(username),
    FOREIGN KEY (affiliated_branch) REFERENCES locations.Branches(branch_id)
);

--37
CREATE TABLE Lockers (
    locker_id BIGSERIAL PRIMARY KEY,
    client VARCHAR(255) NOT NULL,
    country BIGINT,
    warehouse BIGINT,
    FOREIGN KEY (client) REFERENCES Clients(username),
    FOREIGN KEY (country) REFERENCES locations.Countries(country_id),
    FOREIGN KEY (warehouse) REFERENCES locations.Warehouses(warehouse_id)
);

--29
CREATE TABLE Shipping_Guides (
    shipping_number BIGSERIAL PRIMARY KEY,
    client_from VARCHAR(255) NOT NULL,
    client_to VARCHAR(255) NOT NULL,
    branch_from BIGINT,
    locker_from BIGINT,
    branch_to BIGINT,
    locker_to BIGINT,
    delivery_included BOOLEAN NOT NULL,
    shipping_date DATE NOT NULL,
    shipping_hour TIME NOT NULL,
    shipping_type VARCHAR(20) NOT NULL,
    FOREIGN KEY (client_from) REFERENCES Clients(username),
    FOREIGN KEY (client_to) REFERENCES Clients(username),
    FOREIGN KEY (branch_from) REFERENCES locations.Branches(branch_id),
    FOREIGN KEY (locker_from) REFERENCES Lockers(locker_id),
    FOREIGN KEY (branch_to) REFERENCES locations.Branches(branch_id),
    FOREIGN KEY (locker_to) REFERENCES Lockers(locker_id)
);

--35
CREATE TABLE Payments (
    id BIGSERIAL PRIMARY KEY,
    client VARCHAR(255) NOT NULL,
    reference VARCHAR(255) NOT NULL,
    platform VARCHAR(255) NOT NULL,
    pay_type VARCHAR(255) NOT NULL,
    pay_date DATE NOT NULL,
    pay_hour TIME NOT NULL,
    amount DECIMAL(7,2) NOT NULL,
    FOREIGN KEY (client) REFERENCES Clients(username)
);

--36
CREATE TABLE Guide_Payments (
    pay_id BIGSERIAL PRIMARY KEY,
    shipping_number BIGSERIAL,
    FOREIGN KEY (pay_id) REFERENCES Payments(id),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_Guides(shipping_number)
);


CREATE TABLE Package_Descriptions (
    tracking_number BIGSERIAL PRIMARY KEY,
    content VARCHAR(255) NOT NULL,
    package_value DECIMAL(10,2) NOT NULL,   
    package_weight DECIMAL(7,2) NOT NULL,         
    package_lenght DECIMAL(7,2) NOT NULL,
    package_width DECIMAL(7,2) NOT NULL,
    package_height DECIMAL(7,2) NOT NULL
);

--38
CREATE TABLE Packages (
    tracking_number BIGSERIAL PRIMARY KEY,
    admin_verification VARCHAR(255) NOT NULL,
    holder VARCHAR(255) NOT NULL,
    building_id BIGINT,
    shipping_number BIGINT,
    locker_id BIGINT,
    register_date DATE NOT NULL,
    register_hour TIME NOT NULL,
    delivered BOOLEAN NOT NULL,
    FOREIGN KEY (tracking_number) REFERENCES Package_Descriptions(tracking_number),
    FOREIGN KEY (admin_verification) REFERENCES Root_Users(username),
    FOREIGN KEY (holder) REFERENCES Users(username),
    FOREIGN KEY (building_id) REFERENCES locations.Buildings(building_id),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_Guides(shipping_number),
    FOREIGN KEY (locker_id) REFERENCES Lockers(locker_id)
);

--41 
CREATE TABLE Orders (
    order_number BIGSERIAL PRIMARY KEY,
    previous_order BIGINT,
    generated_date DATE NOT NULL,
    generated_hour TIME NOT NULL,
    FOREIGN KEY (previous_order) REFERENCES Orders(order_number)
);

--42
CREATE TABLE Manual_Orders (
    order_number BIGSERIAL PRIMARY KEY,
    admin_verification VARCHAR(255) NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Orders(order_number),
    FOREIGN KEY (admin_verification) REFERENCES Root_Users(username)
);

--43
CREATE TABLE Automatic_Orders (
    order_number BIGSERIAL PRIMARY KEY,
    admin_verification VARCHAR(255),
    completed_date DATE,
    completed_hour TIME,
    FOREIGN KEY (order_number) REFERENCES Orders(order_number),
    FOREIGN KEY (admin_verification) REFERENCES Root_Users(username)
);

--44
CREATE TABLE Order_Pay_Confirmations (
    order_number BIGINT PRIMARY KEY,
    pay_id BIGINT,
    FOREIGN KEY (order_number) REFERENCES Manual_Orders(order_number),
    FOREIGN KEY (pay_id) REFERENCES Payments(id)
);

--45
CREATE TABLE Withdrawal_Order (
    order_number BIGINT PRIMARY KEY,
    client VARCHAR(255) NOT NULL,
    shipping_number BIGINT,
    FOREIGN KEY (order_number) REFERENCES Manual_Orders(order_number),
    FOREIGN KEY (client) REFERENCES Clients(username),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_Guides(shipping_number)
);

--46
CREATE TABLE Delivery_Orders (
    order_number BIGINT PRIMARY KEY,
    motorcyclist VARCHAR(255) NOT NULL,
    client VARCHAR(255) NOT NULL,
    shipping_number BIGINT,
    FOREIGN KEY (order_number) REFERENCES Automatic_Orders(order_number),
    FOREIGN KEY (motorcyclist) REFERENCES Motorcyclists(username),
    FOREIGN KEY (client) REFERENCES Clients(username),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_Guides(shipping_number)
);

--47
CREATE TABLE Warehouse_Transfer_Orders (
    order_number BIGINT PRIMARY KEY,
    trucker VARCHAR(255) NOT NULL,
    warehouse_from BIGINT,
    warehouse_to BIGINT,
    shipping_number BIGSERIAL,
    FOREIGN KEY (order_number) REFERENCES Automatic_Orders(order_number),
    FOREIGN KEY (trucker) REFERENCES Truckers(username),
    FOREIGN KEY (warehouse_from) REFERENCES locations.Warehouses(warehouse_id),
    FOREIGN KEY (warehouse_to) REFERENCES locations.Warehouses(warehouse_id),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_Guides(shipping_number)
);

--48
CREATE TABLE Branch_Transfer_Order (
    order_number BIGINT PRIMARY KEY,
    trucker VARCHAR(255) NOT NULL,
    shipping_number BIGSERIAL,
    warehouse BIGSERIAL,
    branch BIGSERIAL,
    -- true if transfer is warehouse->branch, false if transfer is branch->warehouse
    withdrawal BOOLEAN NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Automatic_Orders(order_number),
    FOREIGN KEY (trucker) REFERENCES Truckers(username),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_Guides(shipping_number),
    FOREIGN KEY (warehouse) REFERENCES locations.Warehouses(warehouse_id),
    FOREIGN KEY (branch) REFERENCES locations.Branches(branch_id)
);

--49
CREATE TABLE Air_Cargo_Order (
    order_number BIGINT PRIMARY KEY,
    trucker VARCHAR(255) NOT NULL,
    shipping_number BIGINT,
    warehouse BIGINT,
    air_freight_forwarder BIGINT,
    -- true if transfer is warehouse->forwarder, false if transfer is forwarder->warehouse
    withdrawal BOOLEAN NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Automatic_Orders(order_number),
    FOREIGN KEY (trucker) REFERENCES Truckers(username),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_Guides(shipping_number),
    FOREIGN KEY (warehouse) REFERENCES locations.Warehouses(warehouse_id),
    FOREIGN KEY (air_freight_forwarder) REFERENCES locations.Allied_Shipping_Offices(office_id)
);

--50
CREATE TABLE Ocean_Cargo_Order (
    order_number BIGINT PRIMARY KEY,
    trucker VARCHAR(255) NOT NULL,
    shipping_number BIGINT,
    warehouse BIGINT,
    -- true if transfer is warehouse->forwarder, false if transfer is forwarder->warehouse
    ocean_freight_forwarder BIGINT,
    withdrawal BOOLEAN NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Automatic_Orders(order_number),
    FOREIGN KEY (trucker) REFERENCES Truckers(username),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_Guides(shipping_number),
    FOREIGN KEY (warehouse) REFERENCES locations.Warehouses(warehouse_id),
    FOREIGN KEY (ocean_freight_forwarder) REFERENCES locations.Allied_Shipping_Offices(office_id)
);