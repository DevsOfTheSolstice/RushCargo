--1
ALTER TABLE Legal_Identification
ADD COLUMN identification_type VARCHAR(255);

--2
ALTER TABLE Users
ADD COLUMN identity_document VARCHAR(255),
ADD CONSTRAINT fk_identity_document
FOREIGN KEY (identity_document) REFERENCES Legal_Identification(id),
DROP CONSTRAINT IF EXISTS users_admin_verification_fkey,
DROP CONSTRAINT IF EXISTS users_admin_suspension_fkey,
ADD CONSTRAINT fk_admin_verification
FOREIGN KEY (admin_verification) REFERENCES Root_User(username),
ADD CONSTRAINT fk_admin_suspension
FOREIGN KEY (admin_suspension) REFERENCES Root_User(username);

--3
ALTER TABLE Package
DROP CONSTRAINT IF EXISTS package_admin_verification_fkey,
ADD CONSTRAINT fk_admin_verification
FOREIGN KEY (admin_verification) REFERENCES Root_User(username);

--4
ALTER TABLE Orders
ADD COLUMN verification_admin VARCHAR(255),
ADD CONSTRAINT fk_verification_admin
FOREIGN KEY (verification_admin) REFERENCES Root_User(username);

--5
ALTER TABLE Manual_Orders
DROP CONSTRAINT IF EXISTS manual_orders_admin_verification_fkey,
ADD CONSTRAINT fk_admin_verification
FOREIGN KEY (admin_verification) REFERENCES Root_User(username);

--6
ALTER TABLE Automatic_Orders
DROP CONSTRAINT IF EXISTS automatic_orders_admin_verification_fkey,
ADD CONSTRAINT fk_admin_verification
FOREIGN KEY (admin_verification) REFERENCES Root_User(username);

--7
CREATE TABLE Vehicle (
    vin_vehicle VARCHAR(17) PRIMARY KEY,
    brand VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,
    weight_capacity DECIMAL(4, 2) NOT NULL,
    width_capacity DECIMAL(4, 2) NOT NULL,
    height_capacity DECIMAL(4, 2) NOT NULL,
    length_capacity DECIMAL(4, 2) NOT NULL,
    vehicle_type VARCHAR(255) NOT NULL
);

ALTER TABLE Motocyclist
DROP CONSTRAINT IF EXISTS motocyclist_motorcycle_fkey,
ADD CONSTRAINT fk_motorcycle
FOREIGN KEY (motorcycle) REFERENCES Vehicle(vin_vehicle);

ALTER TABLE Truck_Driver
DROP CONSTRAINT IF EXISTS truck_driver_truck_fkey,
ADD CONSTRAINT fk_truck
FOREIGN KEY (truck) REFERENCES Vehicle(vin_vehicle);

--8
CREATE TABLE Legal_Client_Affiliations (
    affiliation_id BIGSERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    affiliated_branch INT NOT NULL,
    gps_address VARCHAR(255) NOT NULL,
    FOREIGN KEY (username) REFERENCES Legal_Client(username),
    FOREIGN KEY (affiliated_branch) REFERENCES Branch(branch_id)
);

--9
CREATE TABLE Assigned_Delivery_Order (
    order_number BIGSERIAL PRIMARY KEY,
    motorcyclist_username VARCHAR(255) NOT NULL,
    legal_client_affiliation BIGSERIAL NOT NULL,
    package BIGSERIAL NOT NULL,
    delivery_gps_address VARCHAR(255) NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Automatic_Orders(order_number),
    FOREIGN KEY (motorcyclist_username) REFERENCES Motocyclist(username),
    FOREIGN KEY (legal_client_affiliation) REFERENCES Legal_Client_Affiliations(affiliation_id),
    FOREIGN KEY (package) REFERENCES Package(tracking_number)
);

--10
ALTER TABLE Package
DROP COLUMN content,
DROP COLUMN package_value,
DROP COLUMN package_weight,
DROP COLUMN package_lenght,
DROP COLUMN package_width,
DROP COLUMN package_height,
DROP COLUMN delivered,
ADD COLUMN nombre_usuario VARCHAR(255),
ADD CONSTRAINT fk_nombre_usuario
FOREIGN KEY (nombre_usuario) REFERENCES Client(username);
--11

CREATE TABLE Package_Description (
    tracking_number BIGSERIAL PRIMARY KEY,
    content VARCHAR(255) NOT NULL,
    package_value DECIMAL(4,2) NOT NULL,   
    package_weight DECIMAL(4,2) NOT NULL,         
    package_lenght DECIMAL(4,2) NOT NULL,
    package_width DECIMAL(4,2) NOT NULL,
    package_height DECIMAL(4,2) NOT NULL,
    delivered BOOLEAN NOT NULL,
    FOREIGN KEY (tracking_number) REFERENCES Package(tracking_number)
);

--12
CREATE TABLE Allied_Shipping_Office (
    building_id BIGSERIAL PRIMARY KEY,
    warehouse_connection BIGSERIAL,
    affiliated_company BIGSERIAL,
    radial_distance DECIMAL(4,2) NOT NULL,
    route_distance DECIMAL(4,2) NOT NULL,
    type VARCHAR(255) NOT NULL,
    FOREIGN KEY (building_id) REFERENCES Building(building_id),
    FOREIGN KEY (warehouse_connection) REFERENCES Warehouse(warehouse_id),
    FOREIGN KEY (affiliated_company) REFERENCES Allied_Company(company_id)
);

--13
ALTER TABLE Air_Cargo_Order
DROP CONSTRAINT IF EXISTS air_cargo_order_air_freight_forwarder_fkey,
DROP CONSTRAINT IF EXISTS air_cargo_order_shipping_number_fkey,
ADD CONSTRAINT fk_air_freight_forwarder FOREIGN KEY (air_freight_forwarder) REFERENCES Allied_Shipping_Office(building_id),
ADD CONSTRAINT fk_shipping_number FOREIGN KEY (shipping_number) REFERENCES Shipping_Guide(shipping_number);

ALTER TABLE Ocean_Cargo_Order
DROP CONSTRAINT IF EXISTS ocean_cargo_order_ocean_freight_forwarder_fkey,
DROP CONSTRAINT IF EXISTS ocean_cargo_order_shipping_number_fkey,
ADD CONSTRAINT fk_ocean_freight_forwarder FOREIGN KEY (ocean_freight_forwarder) REFERENCES Allied_Shipping_Office(building_id),
ADD CONSTRAINT fk_shipping_number FOREIGN KEY (shipping_number) REFERENCES Shipping_Guide(shipping_number);

--14
ALTER TABLE Building
ADD COLUMN area_id BIGSERIAL,
ADD CONSTRAINT fk_area_id
FOREIGN KEY (area_id) REFERENCES City_area(area_id);

--15
CREATE TABLE Assigned_Delivery (
    motocyclist_user VARCHAR(255) PRIMARY KEY,
    legal_client VARCHAR(255) NOT NULL,
    assigned_area BIGSERIAL,
    FOREIGN KEY (motocyclist_user) REFERENCES Motocyclist(username),
    FOREIGN KEY (legal_client) REFERENCES Legal_Client(username),
    FOREIGN KEY (assigned_area) REFERENCES City_area(area_id)
);

--16
ALTER TABLE Natural_Client
DROP CONSTRAINT IF EXISTS natural_client_identification_document_fkey,
DROP COLUMN IF EXISTS identification_document,
ADD COLUMN affiliated_branch BIGSERIAL,
ADD CONSTRAINT fk_affiliated_branch
FOREIGN KEY (affiliated_branch) REFERENCES Branch(branch_id);

--17
ALTER TABLE Shipping_Guide
ADD COLUMN building_sender BIGSERIAL,
ADD COLUMN branch_receiver BIGSERIAL,
ADD COLUMN shipping_type VARCHAR(255),
ADD CONSTRAINT fk_building_sender FOREIGN KEY (building_sender) REFERENCES Building(building_id),
ADD CONSTRAINT fk_branch_receiver FOREIGN KEY (branch_receiver) REFERENCES Branch(branch_id);

--18
ALTER TABLE Allied_Company
DROP COLUMN IF EXISTS gps_address,
ADD COLUMN gps_latitude DECIMAL(9,6),
ADD COLUMN gps_longitude DECIMAL(9,6),
DROP CONSTRAINT IF EXISTS allied_company_employer_identity_fkey,
DROP COLUMN IF EXISTS employer_identity,
ADD COLUMN fiscal_record_id VARCHAR(255),
ADD CONSTRAINT fk_fiscal_record_id
FOREIGN KEY (fiscal_record_id) REFERENCES Legal_Identification(id);

ALTER TABLE Legal_Client
DROP CONSTRAINT IF EXISTS legal_client_employer_identity_fkey,
DROP COLUMN IF EXISTS employer_identity;

ALTER TABLE Root_User
DROP CONSTRAINT IF EXISTS root_user_identity_document_fkey,
ADD CONSTRAINT fk_identity_document
FOREIGN KEY (identity_document) REFERENCES Legal_Identification(id);

ALTER TABLE Driver
DROP CONSTRAINT IF EXISTS driver_identification_document_fkey,
DROP COLUMN IF EXISTS identification_document;

--19
ALTER TABLE Building
DROP COLUMN IF EXISTS building_name,
DROP CONSTRAINT IF EXISTS building_city_id_fkey,
DROP COLUMN IF EXISTS city_id,
ADD COLUMN email VARCHAR(255),
ADD COLUMN phone VARCHAR(20),
ADD COLUMN gps_latitude DECIMAL(9,6),
ADD COLUMN gps_longitude DECIMAL(9,6);

--20
ALTER TABLE Region
DROP CONSTRAINT IF EXISTS region_main_air_freight_forwarder_fkey,
DROP CONSTRAINT IF EXISTS region_main_ocean_freight_forwarder_fkey,
ADD CONSTRAINT fk_main_air_freight_forwarder
FOREIGN KEY (main_air_freight_forwarder) REFERENCES Allied_Shipping_Office(building_id),
ADD CONSTRAINT fk_main_ocean_freight_forwarder
FOREIGN KEY (main_ocean_freight_forwarder) REFERENCES Allied_Shipping_Office(building_id);

--21
ALTER TABLE Warehouse
ADD COLUMN warehouse_name VARCHAR(255);

--22
ALTER TABLE Warehouse_Connection
ADD COLUMN id BIGSERIAL PRIMARY KEY;

--23
ALTER TABLE Legal_Client
ADD COLUMN route_distance DECIMAL(4,2) NOT NULL;

--24
ALTER TABLE Natural_Client
ADD COLUMN route_distance DECIMAL(4,2) NOT NULL;

--25
ALTER TABLE Branch
DROP COLUMN IF EXISTS radial_distance;

--26
ALTER TABLE Allied_Shipping_Office
DROP COLUMN IF EXISTS radial_distance;

--27
ALTER TABLE Warehouse_Connection
DROP COLUMN IF EXISTS radial_distance;

--28
ALTER TABLE City_Area
DROP CONSTRAINT IF EXISTS city_area_city_id_fkey;

ALTER TABLE City RENAME TO Subregion;

ALTER TABLE Subregion
RENAME COLUMN city_id TO subregion_id;

ALTER TABLE Subregion
RENAME COLUMN city_name TO subregion_name;

--29
CREATE TABLE City (
    city_id BIGSERIAL PRIMARY KEY,
    city_name VARCHAR(255) NOT NULL,
    subregion_id BIGSERIAL NOT NULL,
    FOREIGN KEY (subregion_id) REFERENCES Subregion(subregion_id)
);

ALTER TABLE building
DROP CONSTRAINT IF EXISTS fk_area_id;

ALTER TABLE assigned_delivery
DROP CONSTRAINT IF EXISTS fk_area_id;

ALTER TABLE City_Area
DROP COLUMN city_id,
ADD COLUMN city_id BIGINT NOT NULL,
ADD CONSTRAINT city_area_city_id_fkey
FOREIGN KEY (city_id) REFERENCES City(city_id);

--30
ALTER TABLE Allied_Shipping_Office
RENAME COLUMN building_id TO office_id;

ALTER TABLE Building
ADD COLUMN address_description VARCHAR(255) NOT NULL;

ALTER TABLE Branch
RENAME COLUMN warehouse_id TO warehouse_connection;

--31
ALTER TABLE Warehouse
DROP COLUMN warehouse_name;

ALTER TABLE Building
ADD COLUMN building_name VARCHAR(50) NOT NULL;

--32 
ALTER TABLE Package
DROP COLUMN shipping_number;

ALTER TABLE Package
ADD COLUMN shipping_number BIGINT;

ALTER TABLE Package
RENAME COLUMN nombre_usuario to username;

ALTER TABLE Package
DROP COLUMN locker_id;

ALTER TABLE Package
ADD COLUMN locker_id BIGINT
FOREIGN KEY (locker_id) REFERENCES Locker(locker_id);

--33
ALTER TABLE Shipping_Guide
ADD COLUMN locker_sender BIGINT,
ADD COLUMN locker_receiver BIGINT,
FOREIGN KEY (locker_sender) REFERENCES Locker(locker_id),
FOREIGN KEY (locker_receiver) REFERENCES Locker(locker_id);

--34
ALTER TABLE Warehouse_connection
DROP CONSTRAINT IF EXISTS warehouse_connection_warehouse1_id_fkey,
DROP CONSTRAINT IF EXISTS warehouse_connection_warehouse2_id_fkey,
DROP COLUMN warehouse1_id,
DROP COLUMN warehouse2_id;

ALTER TABLE Warehouse_connection
ADD COLUMN warehouse1_id BIGINT,
ADD COLUMN warehouse2_id BIGINT,
ADD CONSTRAINT warehouse_connection_warehouse1_id_fkey FOREIGN KEY (warehouse1_id) REFERENCES warehouse(warehouse_id),
ADD CONSTRAINT warehouse_connection_warehouse2_id_fkey FOREIGN KEY (warehouse2_id) REFERENCES Warehouse(warehouse_id);


--Dropped tables
DROP TABLE IF EXISTS Motorcycle;
DROP TABLE IF EXISTS Truck;
DROP TABLE IF EXISTS Land_Guide;
DROP TABLE IF EXISTS Air_Guide;
DROP TABLE IF EXISTS Ocean_Guide;
DROP TABLE IF EXISTS Employer_Identity;
DROP TABLE IF EXISTS Identity_Document;
DROP TABLE IF EXISTS Air_Freight_Forwader;
DROP TABLE IF EXISTS Ocean_Freight_Forwarder;
DROP TABLE IF EXISTS User_Admin;
DROP TABLE IF EXISTS Package_Admin;
DROP TABLE IF EXISTS Cashier_Admin;
DROP TABLE IF EXISTS No_Comercial_Package;
DROP TABLE IF EXISTS Comercial_Package;
