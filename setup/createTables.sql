--1
CREATE TABLE Country (
    country_id BIGSERIAL PRIMARY KEY,
    country_name VARCHAR(50) UNIQUE NOT NULL,
    phone_prefix VARCHAR(50) UNIQUE NOT NULL
);

--2
CREATE TABLE Region (
    region_id BIGSERIAL PRIMARY KEY,
    country_id BIGINT,
    region_name VARCHAR(50) NOT NULL,
    main_air_freight_forwarder BIGINT,
    main_ocean_freight_forwarder BIGINT,
    FOREIGN KEY (country_id) REFERENCES Country(country_id)
);

--3
CREATE TABLE City (
    city_id BIGSERIAL PRIMARY KEY,
    region_id BIGINT,
    city_name VARCHAR(50) NOT NULL,
    main_warehouse BIGINT,
    FOREIGN KEY (region_id) REFERENCES Region(region_id)
);

--4
CREATE TABLE Legal_Identification (
    id VARCHAR(255) PRIMARY KEY,
    country_id BIGSERIAL,
    document VARCHAR(255) NOT NULL,
    due_date DATE NOT NULL,
    expedition_date DATE NOT NULL,
    FOREIGN KEY (country_id) REFERENCES Country(country_id)
);

--5
CREATE TABLE Vigent_Identification (
    id VARCHAR(255) PRIMARY KEY,
    vigent BOOLEAN NOT NULL,
    FOREIGN KEY (id) REFERENCES Legal_Identification(id)
);

--6
CREATE TABLE Identity_Document (
    id VARCHAR(255) PRIMARY KEY,
    FOREIGN KEY (id) REFERENCES Legal_Identification(id)
);

--7
CREATE TABLE Employer_Identity (
    id VARCHAR(255) PRIMARY KEY,
    FOREIGN KEY (id) REFERENCES Legal_Identification(id)
);

--8
CREATE TABLE Building (
    building_id BIGSERIAL PRIMARY KEY,
    city_id BIGSERIAL,
    building_name VARCHAR(50) NOT NULL,
    FOREIGN KEY (city_id) REFERENCES City(city_id)
);

--9
CREATE TABLE Warehouse (
    warehouse_id BIGSERIAL PRIMARY KEY,
    FOREIGN KEY (warehouse_id) REFERENCES Building(building_id)
);

--10
CREATE TABLE Warehouse_Connection (
    warehouse1_id BIGSERIAL,
    warehouse2_id BIGSERIAL,
    radial_distance DECIMAL(4,2) NOT NULL,
    rute_distance DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (warehouse1_id) REFERENCES Warehouse(warehouse_id),
    FOREIGN KEY (warehouse2_id) REFERENCES Warehouse(warehouse_id)
);

--11
CREATE TABLE Branch (
    branch_id BIGSERIAL PRIMARY KEY,
    warehouse_id BIGSERIAL,
    radial_distance DECIMAL(4,2) NOT NULL,
    rute_distance DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (branch_id) REFERENCES Building(building_id),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(warehouse_id)
);

--12
CREATE TABLE Allied_Company (
    company_id INT PRIMARY KEY,
    employer_identity VARCHAR(255) NOT NULL,
    email VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    gps_address VARCHAR(255),
    FOREIGN KEY (employer_identity) REFERENCES Employer_Identity(id)
);

--13
CREATE TABLE Air_Freight_Forwader (
    building_id BIGSERIAL PRIMARY KEY,
    warehouse_id BIGSERIAL,
    company_id BIGSERIAL,
    radial_distance DECIMAL(4,2) NOT NULL,
    rute_distance DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (building_id) REFERENCES Building(building_id),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(warehouse_id),
    FOREIGN KEY (company_id) REFERENCES Allied_Company(company_id)
);

--14
CREATE TABLE Ocean_Freight_Forwarder (
    building_id BIGSERIAL PRIMARY KEY,
    warehouse_id BIGSERIAL,
    company_id BIGSERIAL,
    radial_distance DECIMAL(4,2) NOT NULL,
    rute_distance DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (building_id) REFERENCES Building(building_id),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(warehouse_id),
    FOREIGN KEY (company_id) REFERENCES Allied_Company(company_id)
);

--15
CREATE TABLE Motorcycle (
    vin_vehicle VARCHAR(17) PRIMARY KEY,
    brand VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,
    weight_capacity DECIMAL(4, 2) NOT NULL,
    width_capacity DECIMAL(4, 2) NOT NULL,
    height_capacity DECIMAL(4, 2) NOT NULL,
    length_capacity DECIMAL(4, 2) NOT NULL
);

--16
CREATE TABLE Truck (
    vin_vehicle VARCHAR(17) PRIMARY KEY,
    brand VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,
    weight_capacity DECIMAL(4, 2) NOT NULL,
    width_capacity DECIMAL(4, 2) NOT NULL,
    height_capacity DECIMAL(4, 2) NOT NULL,
    length_capacity DECIMAL(4, 2) NOT NULL
);

--17
CREATE TABLE Root_User (
    username VARCHAR(255) PRIMARY KEY,
    warehouse_id BIGSERIAL,
    identity_document VARCHAR(255) NOT NULL,
    user_password VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    gps_address VARCHAR(255),
    FOREIGN KEY (identity_document) REFERENCES Identity_Document(id),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(warehouse_id)
);

--18
CREATE TABLE User_Admin (
    username VARCHAR(255) PRIMARY KEY,
    FOREIGN KEY (username) REFERENCES Root_User(username)
);

--19
CREATE TABLE Package_Admin (
    username VARCHAR(255) PRIMARY KEY,
    FOREIGN KEY (username) REFERENCES Root_User(username)
);

--20   
CREATE TABLE Cashier_Admin (
    username VARCHAR(255) PRIMARY KEY,
    FOREIGN KEY (username) REFERENCES Root_User(username)
);

--21
CREATE TABLE Users (
    username VARCHAR(255) PRIMARY KEY,
    admin_verification VARCHAR(255),
    admin_suspension VARCHAR(255),
    user_password VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    gps_address VARCHAR(255) NOT NULL,
    FOREIGN KEY (admin_verification) REFERENCES User_Admin(username),
    FOREIGN KEY (admin_suspension) REFERENCES User_Admin(username)
);

--22
CREATE TABLE Driver (
    username VARCHAR(255) PRIMARY KEY,
    identification_document VARCHAR(255) NOT NULL,
    born_date DATE NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    salary DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (username) REFERENCES Users(username),
    FOREIGN KEY (identification_document) REFERENCES Identity_Document(id)
);

--23
CREATE TABLE Motocyclist (
    username VARCHAR(255) PRIMARY KEY,
    motorcycle VARCHAR(17),
    FOREIGN KEY (username) REFERENCES Driver(username),
    FOREIGN KEY (motorcycle) REFERENCES Motorcycle(vin_vehicle)
);

--24
CREATE TABLE Truck_Driver (
    username VARCHAR(255) PRIMARY KEY,
    truck VARCHAR(17),
    FOREIGN KEY (username) REFERENCES Driver(username),
    FOREIGN KEY (truck) REFERENCES Truck(vin_vehicle)
);

--25 
CREATE TABLE Client (
    username VARCHAR(255) PRIMARY KEY,
    branch BIGSERIAL,
    FOREIGN KEY (username) REFERENCES Users(username),
    FOREIGN KEY (branch) REFERENCES Branch(branch_id)
);

--26
CREATE TABLE Client_Debt (
    username VARCHAR(255) PRIMARY KEY,
    debt DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (username) REFERENCES Client(username)
);

--27
CREATE TABLE Natural_Client (
    username VARCHAR(255) PRIMARY KEY,
    identification_document VARCHAR(255) NOT NULL,
    born_date DATE NOT NULL,
    client_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    FOREIGN KEY (username) REFERENCES Client(username),
    FOREIGN KEY (identification_document) REFERENCES Identity_Document(id)
);

--28
CREATE TABLE Legal_Client (
    username VARCHAR(255) PRIMARY KEY,
    employer_identity VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    company_type VARCHAR(255) NOT NULL,
    FOREIGN KEY (username) REFERENCES Client(username),
    FOREIGN KEY (employer_identity) REFERENCES Employer_Identity(id)
);

--29
CREATE TABLE Shipping_Guide (
    shipping_number BIGSERIAL PRIMARY KEY,
    client_user_from VARCHAR(255) NOT NULL,
    client_user_to VARCHAR(255) NOT NULL,
    delivery_included BOOLEAN NOT NULL,
    shipping_date DATE NOT NULL,
    shipping_hour TIME NOT NULL,
    FOREIGN KEY (client_user_from) REFERENCES Client(username),
    FOREIGN KEY (client_user_to) REFERENCES Client(username)
);

--30
CREATE TABLE Guide_Price (
    shipping_number BIGSERIAL PRIMARY KEY,
    price DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (shipping_number) REFERENCES Shipping_Guide(shipping_number)
);

--31
CREATE TABLE Guide_Unpaid (
    shipping_number BIGSERIAL PRIMARY KEY,
    unpaid DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (shipping_number) REFERENCES Shipping_Guide(shipping_number)
);

--32
CREATE TABLE Land_Guide (
    shipping_number BIGSERIAL PRIMARY KEY,
    FOREIGN KEY (shipping_number) REFERENCES Shipping_Guide(shipping_number)
);

--33
CREATE TABLE Air_Guide (
    shipping_number BIGSERIAL PRIMARY KEY,
    FOREIGN KEY (shipping_number) REFERENCES Shipping_Guide(shipping_number)
);

--34
CREATE TABLE Ocean_Guide (
    shipping_number BIGSERIAL PRIMARY KEY,
    FOREIGN KEY (shipping_number) REFERENCES Shipping_Guide(shipping_number)
);

--35
CREATE TABLE Payment (
    id BIGSERIAL PRIMARY KEY,
    client VARCHAR(255) NOT NULL,
    reference VARCHAR(255) NOT NULL,
    platform VARCHAR(255) NOT NULL,
    pay_type VARCHAR(255) NOT NULL,
    pay_date DATE NOT NULL,
    pay_hour TIME NOT NULL,
    amount DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (client) REFERENCES Client(username)
);

--36
CREATE TABLE Guide_Payments (
    pay_id BIGSERIAL PRIMARY KEY,
    shipping_number BIGSERIAL,
    amount_paid DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (pay_id) REFERENCES Payment(id),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_Guide(shipping_number)
);

--37
CREATE TABLE Locker (
    locker_id BIGSERIAL PRIMARY KEY,
    client VARCHAR(255) NOT NULL,
    country_id BIGSERIAL,
    warehouse_id BIGSERIAL,
    FOREIGN KEY (client) REFERENCES Client(username),
    FOREIGN KEY (country_id) REFERENCES Country(country_id),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(warehouse_id)
);

--38
CREATE TABLE Package (
    tracking_number BIGSERIAL PRIMARY KEY,
    admin_verification VARCHAR(255) NOT NULL,
    building_id BIGSERIAL,
    shipping_number BIGSERIAL,
    locker_id BIGSERIAL,
    content VARCHAR(255) NOT NULL,
    package_value DECIMAL(4,2) NOT NULL,   
    package_weight DECIMAL(4,2) NOT NULL,         
    package_lenght DECIMAL(4,2) NOT NULL,
    package_width DECIMAL(4,2) NOT NULL,
    package_height DECIMAL(4,2) NOT NULL,
    register_date DATE NOT NULL,
    register_hour TIME NOT NULL,
    delivered BOOLEAN NOT NULL,
    FOREIGN KEY (admin_verification) REFERENCES Package_Admin(username),
    FOREIGN KEY (building_id) REFERENCES Building(building_id),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_Guide(shipping_number),
    FOREIGN KEY (locker_id) REFERENCES Locker(locker_id)
);

--39
CREATE TABLE No_Comercial_Package (
    tracking_number BIGSERIAL PRIMARY KEY,
    client VARCHAR(255) NOT NULL,
    FOREIGN KEY (tracking_number) REFERENCES Package(tracking_number),
    FOREIGN KEY (client) REFERENCES Natural_Client(username)
);

--40
CREATE TABLE Comercial_Package (
    tracking_number BIGSERIAL PRIMARY KEY,
    client VARCHAR(255) NOT NULL,
    FOREIGN KEY (tracking_number) REFERENCES Package(tracking_number),
    FOREIGN KEY (client) REFERENCES Legal_Client(username)
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
    FOREIGN KEY (admin_verification) REFERENCES Cashier_Admin(username)
);

--43
CREATE TABLE Automatic_Orders (
    order_number BIGSERIAL PRIMARY KEY,
    admin_verification VARCHAR(255),
    completed_date DATE,
    completed_hour TIME,
    FOREIGN KEY (order_number) REFERENCES Orders(order_number),
    FOREIGN KEY (admin_verification) REFERENCES Package_Admin(username)
);

--44
CREATE TABLE Order_Pay_Confirmation (
    order_number BIGSERIAL PRIMARY KEY,
    pay_id BIGSERIAL,
    FOREIGN KEY (order_number) REFERENCES Manual_Orders(order_number),
    FOREIGN KEY (pay_id) REFERENCES Payment(id)
);

--45
CREATE TABLE Withdrawal_Order (
    order_number BIGSERIAL PRIMARY KEY,
    client VARCHAR(255) NOT NULL,
    shipping_number BIGSERIAL,
    FOREIGN KEY (order_number) REFERENCES Manual_Orders(order_number),
    FOREIGN KEY (client) REFERENCES Client(username),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_Guide(shipping_number)
);

--46
CREATE TABLE Delivery_Order (
    order_number BIGSERIAL PRIMARY KEY,
    motocyclist VARCHAR(255) NOT NULL,
    client VARCHAR(255) NOT NULL,
    shipping_number BIGSERIAL,
    FOREIGN KEY (order_number) REFERENCES Automatic_Orders(order_number),
    FOREIGN KEY (motocyclist) REFERENCES Motocyclist(username),
    FOREIGN KEY (client) REFERENCES Client(username),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_Guide(shipping_number)
);

--47
CREATE TABLE Warehouse_Transfer_Order (
    order_number BIGSERIAL PRIMARY KEY,
    truck_driver VARCHAR(255) NOT NULL,
    warehouse_id_from BIGSERIAL,
    warehouse_id_to BIGSERIAL,
    shipping_number BIGSERIAL,
    FOREIGN KEY (order_number) REFERENCES Automatic_Orders(order_number),
    FOREIGN KEY (truck_driver) REFERENCES Truck_Driver(username),
    FOREIGN KEY (warehouse_id_from) REFERENCES Warehouse(warehouse_id),
    FOREIGN KEY (warehouse_id_to) REFERENCES Warehouse(warehouse_id),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_Guide(shipping_number)
);

--48
CREATE TABLE Branch_Transfer_Order (
    order_number BIGSERIAL PRIMARY KEY,
    truck_driver VARCHAR(255) NOT NULL,
    shipping_number BIGSERIAL,
    warehouse_id BIGSERIAL,
    branch_id BIGSERIAL,
    withdrawal BOOLEAN NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Automatic_Orders(order_number),
    FOREIGN KEY (truck_driver) REFERENCES Truck_Driver(username),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_Guide(shipping_number),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(warehouse_id),
    FOREIGN KEY (branch_id) REFERENCES Branch(branch_id)
);

--49
CREATE TABLE Air_Cargo_Order (
    order_number BIGSERIAL PRIMARY KEY,
    truck_driver VARCHAR(255) NOT NULL,
    shipping_number BIGSERIAL,
    warehouse_id BIGSERIAL,
    air_freight_forwarder BIGSERIAL,
    withdrawal BOOLEAN NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Automatic_Orders(order_number),
    FOREIGN KEY (truck_driver) REFERENCES Truck_Driver(username),
    FOREIGN KEY (shipping_number) REFERENCES Air_Guide(shipping_number),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(warehouse_id),
    FOREIGN KEY (air_freight_forwarder) REFERENCES Air_Freight_Forwader(building_id)
);

--50
CREATE TABLE Ocean_Cargo_Order (
    order_number BIGSERIAL PRIMARY KEY,
    truck_driver VARCHAR(255) NOT NULL,
    shipping_number BIGSERIAL,
    warehouse_id BIGSERIAL,
    ocean_freight_forwarder BIGSERIAL,
    withdrawal BOOLEAN NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Automatic_Orders(order_number),
    FOREIGN KEY (truck_driver) REFERENCES Truck_Driver(username),
    FOREIGN KEY (shipping_number) REFERENCES Ocean_Guide(shipping_number),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(warehouse_id),
    FOREIGN KEY (ocean_freight_forwarder) REFERENCES Ocean_Freight_Forwarder(building_id)
);

--51
CREATE TABLE City_area ( 
    area_id BIGSERIAL PRIMARY KEY, 
    city_id BIGSERIAL, 
    area_name VARCHAR(255) NOT NULL, 
    area_description VARCHAR(255), 
    FOREIGN KEY (city_id) REFERENCES City(city_id) 
);

--modifications
ALTER TABLE Region
ADD FOREIGN KEY (main_air_freight_forwarder) REFERENCES Air_Freight_Forwader(building_id);

ALTER TABLE Region
ADD FOREIGN KEY (main_ocean_freight_forwarder) REFERENCES Ocean_Freight_Forwarder(building_id);

ALTER TABLE City
ADD FOREIGN KEY (main_warehouse) REFERENCES Warehouse(warehouse_id);