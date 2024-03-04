--1
CREATE TABLE Country (
    id BIGSERIAL PRIMARY KEY,
    country_name VARCHAR(50) NOT NULL,
    phone_prefix VARCHAR(50) NOT NULL
);
--2
CREATE TABLE Region (
    id BIGSERIAL PRIMARY KEY,
    country_id BIGINT NOT NULL,
    region_name VARCHAR(50) NOT NULL,
    FOREIGN KEY (country_id) REFERENCES Country(id)
);
--3
CREATE TABLE City (
    id BIGSERIAL PRIMARY KEY,
    region_id BIGINT NOT NULL,
    city_name VARCHAR(50) NOT NULL,
    FOREIGN KEY (region_id) REFERENCES Region(id)
);
--4
CREATE TABLE Building (
    id_building BIGSERIAL PRIMARY KEY,
    city_id BIGINT NOT NULL,
    building_name VARCHAR(50) NOT NULL,
    FOREIGN KEY (city_id) REFERENCES City(id)
);
--5
CREATE TABLE Warehouse (
    id_warehouse INT PRIMARY KEY,
    FOREIGN KEY (id_warehouse) REFERENCES Building(id_building)
);
--6
CREATE TABLE Legal_Identification (
    identification_id VARCHAR(255) PRIMARY KEY,
    country_id INT NOT NULL,
    identification VARCHAR(255) NOT NULL,
    due_date DATE NOT NULL,
    expedition_date DATE NOT NULL,
    FOREIGN KEY (country_id) REFERENCES Country(id)
);
--7
CREATE TABLE Identity_Document (
    identification_id VARCHAR(255) PRIMARY KEY,
    FOREIGN KEY (identification_id) REFERENCES Legal_Identification(identification_id)
);
--8
CREATE TABLE Root_User (
    username VARCHAR(255) PRIMARY KEY,
    warehouse_id INT NOT NULL,
    identification_document VARCHAR NOT NULL,
    user_password VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    gps_address VARCHAR(255),
    FOREIGN KEY (identification_document) REFERENCES Identity_Document(identification_id),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(id_warehouse)
);
--9
CREATE TABLE Admin_user (
    username VARCHAR(255) PRIMARY KEY,
    FOREIGN KEY (username) REFERENCES Root_User(username)
);
--10
CREATE TABLE Users (
    username VARCHAR(255) PRIMARY KEY,
    admin_verification VARCHAR(255) NOT NULL,
    user_password VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    gps_address VARCHAR(255) NOT NULL,
    FOREIGN KEY (admin_verification) REFERENCES Admin_user(username)
);
--11
CREATE TABLE Motorcycle (
    vin_vehicle VARCHAR(17) PRIMARY KEY,
    brand VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,
    weight_capacity DECIMAL(4, 2) NOT NULL,
    width_capacity DECIMAL(4, 2) NOT NULL,
    height_capacity DECIMAL(4, 2) NOT NULL,
    length_capacity DECIMAL(4, 2) NOT NULL
);
--12
CREATE TABLE Truck (
    vin_vehicle VARCHAR(17) PRIMARY KEY,
    brand VARCHAR(255) NOT NULL,
    model VARCHAR(255) NOT NULL,
    weight_capacity DECIMAL(4, 2) NOT NULL,
    width_capacity DECIMAL(4, 2) NOT NULL,
    height_capacity DECIMAL(4, 2) NOT NULL,
    length_capacity DECIMAL(4, 2) NOT NULL
);
--13
CREATE TABLE Conection_Warehouse_Warehouse (
    id_warehouse_transmitter INT NOT NULL,
    id_warehouse_receiver INT NOT NULL,
    distance DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (id_warehouse_transmitter) REFERENCES Warehouse(id_warehouse),
    FOREIGN KEY (id_warehouse_receiver) REFERENCES Warehouse(id_warehouse)
);
--14
CREATE TABLE branch (
    id_branch INT PRIMARY KEY,
    conection_warehouse INT NOT NULL,
    FOREIGN KEY (id_branch) REFERENCES Building(id_building),
    FOREIGN KEY (conection_warehouse) REFERENCES Warehouse(id_warehouse)
);
--15
CREATE TABLE Client (
    username VARCHAR(255) PRIMARY KEY,
    affiliated_branch INT NOT NULL,
    FOREIGN KEY (username) REFERENCES Users(username),
    FOREIGN KEY (affiliated_branch) REFERENCES Branch(id_branch)
);
--16
CREATE TABLE Natural_Client (
    username VARCHAR(255) PRIMARY KEY,
    client_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    FOREIGN KEY (username) REFERENCES Client(username)
);
--17
CREATE TABLE Shipping_guide (
    shipping_number INT PRIMARY KEY,
    client_user_transmitter VARCHAR(255) NOT NULL,
    client_user_receiver VARCHAR(255) NOT NULL,
    commercial_purposes BOOLEAN NOT NULL,
    international_shipping BOOLEAN NOT NULL,
    delivery_included BOOLEAN NOT NULL,
    shipping_date DATE NOT NULL,
    shipping_hour TIME NOT NULL,
    FOREIGN KEY (client_user_transmitter) REFERENCES Client(username),
    FOREIGN KEY (client_user_receiver) REFERENCES Client(username)
);
--18
CREATE TABLE Estimated_cost (
    shipping_number INT PRIMARY KEY,
    cost DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (shipping_number) REFERENCES Shipping_guide(shipping_number)
);
--19
CREATE TABLE Estimates_arriving_date (
    shipping_number INT PRIMARY KEY,
    estimated_arriving_date DATE NOT NULL,
    estimated_arriving_hour TIME NOT NULL,
    FOREIGN KEY (shipping_number) REFERENCES Shipping_guide(shipping_number)
);
--20
CREATE TABLE Land_Guide (
    shipping_number_land INT PRIMARY KEY,
    FOREIGN KEY (shipping_number_land) REFERENCES Shipping_guide(shipping_number)
);
--21
CREATE TABLE Air_Guide (
    shipping_number_air INT PRIMARY KEY,
    FOREIGN KEY (shipping_number_air) REFERENCES Shipping_guide(shipping_number)
);
--22
CREATE TABLE Maritime_Guide (
    shipping_number_maritime INT PRIMARY KEY,
    FOREIGN KEY (shipping_number_maritime) REFERENCES Shipping_guide(shipping_number)
);
--23
CREATE TABLE Package (
    tracking_number INT PRIMARY KEY,
    shipping_number INT NOT NULL,
    content VARCHAR(255) NOT NULL,
    package_value DECIMAL(4,2) NOT NULL,
    package_lenght DECIMAL(4,2) NOT NULL,
    package_width DECIMAL(4,2) NOT NULL,
    package_height DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (shipping_number) REFERENCES Shipping_guide(shipping_number)
);
--24
CREATE TABLE No_Comercial_Package (
    tracking_number INT PRIMARY KEY,
    user_natural_client VARCHAR(255) NOT NULL,
    FOREIGN KEY (tracking_number) REFERENCES Package(tracking_number),
    FOREIGN KEY (user_natural_client) REFERENCES Natural_Client(username)
);
--25
CREATE TABLE EIN (
    ein VARCHAR(255) PRIMARY KEY,
    FOREIGN KEY (ein) REFERENCES Legal_Identification(identification_id)
);
--26
CREATE TABLE Legal_Client (
    username VARCHAR(255) PRIMARY KEY,
    ein VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    company_type VARCHAR(255) NOT NULL,
    FOREIGN KEY (username) REFERENCES Client(username),
    FOREIGN KEY (ein) REFERENCES EIN(ein)
);
--27
CREATE TABLE Comercial_Package (
    tracking_number INT PRIMARY KEY,
    user_legal_client VARCHAR(255) NOT NULL,
    FOREIGN KEY (tracking_number) REFERENCES Package(tracking_number),
    FOREIGN KEY (user_legal_client) REFERENCES Legal_Client(username)
);
--28
CREATE TABLE Vigent_Identification (
    id_legal_identification VARCHAR(255) PRIMARY KEY,
    FOREIGN KEY (id_legal_identification) REFERENCES Legal_Identification(identification_id)
);
--29
CREATE TABLE Allied_Companies (
    id_company INT PRIMARY KEY,
    id_ein VARCHAR(255) NOT NULL,
    email VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    gps_address VARCHAR(255),
    FOREIGN KEY (id_ein) REFERENCES EIN(ein)
);
--30
CREATE TABLE Aerial_Shipping_Office (
    id_building INT PRIMARY KEY,
    conection_warehouse INT NOT NULL,
    allied_company INT NOT NULL,
    FOREIGN KEY (id_building) REFERENCES Building(id_building),
    FOREIGN KEY (conection_warehouse) REFERENCES Warehouse(id_warehouse),
    FOREIGN KEY (allied_company) REFERENCES Allied_Companies(id_company)
);
--31
CREATE TABLE Maritime_Shipping_Office (
    id_building INT PRIMARY KEY,
    conection_warehouse INT NOT NULL,
    allied_company INT NOT NULL,
    FOREIGN KEY (id_building) REFERENCES Building(id_building),
    FOREIGN KEY (conection_warehouse) REFERENCES Warehouse(id_warehouse),
    FOREIGN KEY (allied_company) REFERENCES Allied_Companies(id_company)
);
--32
CREATE TABLE Employee (
    username VARCHAR(255) PRIMARY KEY,
    identification_document VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    gps_address VARCHAR(255),
    born_date DATE NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    salary DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (username) REFERENCES Users(username),
    FOREIGN KEY (identification_document) REFERENCES Identity_Document(identification_id)
);
--33
CREATE TABLE Motocyclist (
     username VARCHAR(255) PRIMARY KEY,
    assigned_motorcycle VARCHAR(17) NOT NULL,
    FOREIGN KEY (username) REFERENCES Employee(username),
    FOREIGN KEY (assigned_motorcycle) REFERENCES Motorcycle(vin_vehicle)
);
--34
CREATE TABLE Truck_Driver (
    username VARCHAR(255) PRIMARY KEY,
    assigned_truck VARCHAR(17) NOT NULL,
    FOREIGN KEY (username) REFERENCES Employee(username),
    FOREIGN KEY (assigned_truck) REFERENCES Truck(vin_vehicle)
);
--35
CREATE TABLE Admin_Package (
    username VARCHAR(255) PRIMARY KEY,
    FOREIGN KEY (username) REFERENCES Root_User(username)
);
--36
CREATE TABLE Admin_Order (
    username VARCHAR(255) PRIMARY KEY,
    FOREIGN KEY (username) REFERENCES Root_User(username)
);
--37 
CREATE TABLE Orders (
    order_number INT PRIMARY KEY,
    admin_verification VARCHAR(255) NOT NULL,
    departure_date DATE NOT NULL,
    departure_hour TIME NOT NULL,
    arrive_date DATE NOT NULL,
    arrive_hour TIME NOT NULL,
    FOREIGN KEY (admin_verification) REFERENCES Admin_Order(username)
);
--38
CREATE TABLE Withdrawal_order (
    order_number INT PRIMARY KEY,
    client_user VARCHAR(255) NOT NULL,
    shipping_number INT NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Orders(order_number),
    FOREIGN KEY (client_user) REFERENCES Client(username),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_guide(shipping_number)
);
--39
CREATE TABLE Delivery_order (
    order_number INT PRIMARY KEY,
    motocyclist_user VARCHAR(255) NOT NULL,
    client_user VARCHAR(255) NOT NULL,
    shipping_number INT NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Orders(order_number),
    FOREIGN KEY (motocyclist_user) REFERENCES Motocyclist(username),
    FOREIGN KEY (client_user) REFERENCES Client(username),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_guide(shipping_number)
);
--40
CREATE TABLE Warehouse_Transfer_Order (
    order_number INT PRIMARY KEY,
    truck_driver_user VARCHAR(255) NOT NULL,
    id_warehouse_transmitter INT NOT NULL,
    id_warehouse_receiver INT NOT NULL,
    shipping_number INT NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Orders(order_number),
    FOREIGN KEY (truck_driver_user) REFERENCES Truck_Driver(username),
    FOREIGN KEY (id_warehouse_transmitter) REFERENCES Warehouse(id_warehouse),
    FOREIGN KEY (id_warehouse_receiver) REFERENCES Warehouse(id_warehouse),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_guide(shipping_number)
);
--41
CREATE TABLE Branch_Transfer_Order (
    order_number INT PRIMARY KEY,
    truck_driver_user VARCHAR(255) NOT NULL,
    shipping_number INT NOT NULL,
    warehouse_id INT NOT NULL,
    branch_id INT NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Orders(order_number),
    FOREIGN KEY (truck_driver_user) REFERENCES Truck_Driver(username),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_guide(shipping_number),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(id_warehouse),
    FOREIGN KEY (branch_id) REFERENCES Branch(id_branch)
);
--42
CREATE TABLE Air_Cargo_Order (
    order_number INT PRIMARY KEY,
    truck_driver_user VARCHAR(255) NOT NULL,
    aerial_ship_number INT NOT NULL,
    warehouse_id INT NOT NULL,
    id_aerial_shipping_office INT NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Orders(order_number),
    FOREIGN KEY (truck_driver_user) REFERENCES Truck_Driver(username),
    FOREIGN KEY (aerial_ship_number) REFERENCES Air_Guide(shipping_number_air),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(id_warehouse),
    FOREIGN KEY (id_aerial_shipping_office) REFERENCES Aerial_Shipping_Office(id_building)
);
--43
CREATE TABLE Maritime_Cargo_Order (
    order_number INT PRIMARY KEY,
    truck_driver_user VARCHAR(255) NOT NULL,
    maritime_ship_number INT NOT NULL,
    warehouse_id INT NOT NULL,
    id_maritime_shipping_office INT NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Orders(order_number),
    FOREIGN KEY (truck_driver_user) REFERENCES Truck_Driver(username),
    FOREIGN KEY (maritime_ship_number) REFERENCES Maritime_Guide(shipping_number_maritime),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(id_warehouse),
    FOREIGN KEY (id_maritime_shipping_office) REFERENCES Maritime_Shipping_Office(id_building)
);
