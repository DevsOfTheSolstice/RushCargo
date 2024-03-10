--1
CREATE TABLE Country (
    id BIGSERIAL PRIMARY KEY,
    country_name VARCHAR(50) NOT NULL,
    phone_prefix VARCHAR(50) NOT NULL
);

--2
CREATE TABLE Region (
    region_id BIGSERIAL PRIMARY KEY,
    country_id BIGINT NOT NULL,
    region_name VARCHAR(50) NOT NULL,
    aerial_office_principal INT NOT NULL,
    maritime_office_principal INT NOT NULL,
    FOREIGN KEY (country_id) REFERENCES Country(id)
);

--3
CREATE TABLE Warehouse (
    id_warehouse INT PRIMARY KEY
);

--4
CREATE TABLE City (
    id BIGSERIAL PRIMARY KEY,
    region_id BIGINT NOT NULL,
    city_name VARCHAR(50) NOT NULL,
    id_principal_warehouse INT NOT NULL,
    FOREIGN KEY (region_id) REFERENCES Region(region_id),
    FOREIGN KEY (id_principal_warehouse) REFERENCES Warehouse(id_warehouse)
);

--5
CREATE TABLE Building (
    id_building BIGSERIAL PRIMARY KEY,
    city_id BIGINT NOT NULL,
    building_name VARCHAR(50) NOT NULL,
    FOREIGN KEY (city_id) REFERENCES City(id)
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
    admin_suspension VARCHAR(255) NOT NULL,
    user_password VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    gps_address VARCHAR(255) NOT NULL,
    FOREIGN KEY (admin_verification) REFERENCES Admin_user(username),
    FOREIGN KEY (admin_suspension) REFERENCES Admin_user(username)
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
    radial_distance DECIMAL(4,2) NOT NULL,
    rute_distance DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (id_warehouse_transmitter) REFERENCES Warehouse(id_warehouse),
    FOREIGN KEY (id_warehouse_receiver) REFERENCES Warehouse(id_warehouse)
);

--14
CREATE TABLE branch (
    id_branch INT PRIMARY KEY,
    conection_warehouse INT NOT NULL,
    radial_distance DECIMAL(4,2) NOT NULL,
    rute_distance DECIMAL(4,2) NOT NULL,
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
CREATE TABLE Client_Debt (
    username VARCHAR(255) PRIMARY KEY,
    debt DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (username) REFERENCES Client(username)
);

--17
CREATE TABLE Natural_Client (
    username VARCHAR(255) PRIMARY KEY,
    identification_document VARCHAR(255) NOT NULL,
    born_date DATE NOT NULL,
    client_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    FOREIGN KEY (username) REFERENCES Client(username),
    FOREIGN KEY (identification_document) REFERENCES Identity_Document(identification_id)
);

--18
CREATE TABLE Shipping_guide (
    shipping_number INT PRIMARY KEY,
    client_user_transmitter VARCHAR(255) NOT NULL,
    client_user_receiver VARCHAR(255) NOT NULL,
    delivery_included BOOLEAN NOT NULL,
    shipping_date DATE NOT NULL,
    shipping_hour TIME NOT NULL,
    FOREIGN KEY (client_user_transmitter) REFERENCES Client(username),
    FOREIGN KEY (client_user_receiver) REFERENCES Client(username)
);

--19
CREATE TABLE Pay (
    id_pay BIGSERIAL PRIMARY KEY,
    client_user VARCHAR(255) NOT NULL,
    reference_number VARCHAR(255) NOT NULL,
    platform VARCHAR(255) NOT NULL,
    pay_type VARCHAR(255) NOT NULL,
    pay_date DATE NOT NULL,
    pay_hour TIME NOT NULL,
    pay_value DECIMAL(4,2) NOT NULL,
    amount_to_pay DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (client_user) REFERENCES Client(username)
);

--20
CREATE TABLE guide_pay (
    id_pay BIGSERIAL PRIMARY KEY,
    shipping_number INT NOT NULL,
    amount_paid DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (id_pay) REFERENCES Pay(id_pay),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_guide(shipping_number)
);

--21
CREATE TABLE Shipping_Cost (
    shipping_number INT PRIMARY KEY,
    cost DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (shipping_number) REFERENCES Shipping_guide(shipping_number)
);

--22
CREATE TABLE Pending_Payment (
    shipping_number INT PRIMARY KEY,
    Pending DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (shipping_number) REFERENCES Shipping_guide(shipping_number)
);

--23
CREATE TABLE Land_Guide (
    shipping_number_land INT PRIMARY KEY,
    FOREIGN KEY (shipping_number_land) REFERENCES Shipping_guide(shipping_number)
);

--24
CREATE TABLE Air_Guide (
    shipping_number_air INT PRIMARY KEY,
    FOREIGN KEY (shipping_number_air) REFERENCES Shipping_guide(shipping_number)
);

--25
CREATE TABLE Maritime_Guide (
    shipping_number_maritime INT PRIMARY KEY,
    FOREIGN KEY (shipping_number_maritime) REFERENCES Shipping_guide(shipping_number)
);

--26
CREATE TABLE Admin_Package (
    username VARCHAR(255) PRIMARY KEY,
    FOREIGN KEY (username) REFERENCES Root_User(username)
);

--27   
CREATE TABLE Admin_Cashier (
    username VARCHAR(255) PRIMARY KEY,
    FOREIGN KEY (username) REFERENCES Root_User(username)
);

--28
CREATE TABLE Locker (
    id_locker BIGSERIAL PRIMARY KEY,
    client_user VARCHAR(255) NOT NULL,
    country_id INT NOT NULL,
    warehouse_id INT NOT NULL,
    FOREIGN KEY (client_user) REFERENCES Client(username),
    FOREIGN KEY (country_id) REFERENCES Country(id),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(id_warehouse)
);

--29
CREATE TABLE Package (
    tracking_number INT PRIMARY KEY,
    admin_verification VARCHAR(255) NOT NULL,
    ubication_id INT NOT NULL,
    shipping_number INT NOT NULL,
    id_locker INT NOT NULL,
    content VARCHAR(255) NOT NULL,
    package_value DECIMAL(4,2) NOT NULL,   
    package_weight DECIMAL(4,2) NOT NULL,         
    package_lenght DECIMAL(4,2) NOT NULL,
    package_width DECIMAL(4,2) NOT NULL,
    package_height DECIMAL(4,2) NOT NULL,
    register_date DATE NOT NULL,
    register_hour TIME NOT NULL,
    delivered BOOLEAN NOT NULL,
    FOREIGN KEY (admin_verification) REFERENCES Admin_Package(username),
    FOREIGN KEY (ubication_id) REFERENCES Building(id_building),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_guide(shipping_number),
    FOREIGN KEY (id_locker) REFERENCES Locker(id_locker)
);

--30
CREATE TABLE No_Comercial_Package (
    tracking_number INT PRIMARY KEY,
    user_natural_client VARCHAR(255) NOT NULL,
    FOREIGN KEY (tracking_number) REFERENCES Package(tracking_number),
    FOREIGN KEY (user_natural_client) REFERENCES Natural_Client(username)
);

--31
CREATE TABLE EIN (
    ein VARCHAR(255) PRIMARY KEY,
    FOREIGN KEY (ein) REFERENCES Legal_Identification(identification_id)
);

--32
CREATE TABLE Legal_Client (
    username VARCHAR(255) PRIMARY KEY,
    ein VARCHAR(255) NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    company_type VARCHAR(255) NOT NULL,
    FOREIGN KEY (username) REFERENCES Client(username),
    FOREIGN KEY (ein) REFERENCES EIN(ein)
);

--33
CREATE TABLE Comercial_Package (
    tracking_number INT PRIMARY KEY,
    user_legal_client VARCHAR(255) NOT NULL,
    FOREIGN KEY (tracking_number) REFERENCES Package(tracking_number),
    FOREIGN KEY (user_legal_client) REFERENCES Legal_Client(username)
);

--34
CREATE TABLE Vigent_Identification (
    id_legal_identification VARCHAR(255) PRIMARY KEY,
    vigent BOOLEAN NOT NULL,
    FOREIGN KEY (id_legal_identification) REFERENCES Legal_Identification(identification_id)
);

--35
CREATE TABLE Allied_Companies (
    id_company INT PRIMARY KEY,
    id_ein VARCHAR(255) NOT NULL,
    email VARCHAR(50) NOT NULL,
    phone VARCHAR(20),
    gps_address VARCHAR(255),
    FOREIGN KEY (id_ein) REFERENCES EIN(ein)
);

--36
CREATE TABLE Aerial_Shipping_Office (
    id_building INT PRIMARY KEY,
    conection_warehouse INT NOT NULL,
    allied_company INT NOT NULL,
    radial_distance DECIMAL(4,2) NOT NULL,
    rute_distance DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (id_building) REFERENCES Building(id_building),
    FOREIGN KEY (conection_warehouse) REFERENCES Warehouse(id_warehouse),
    FOREIGN KEY (allied_company) REFERENCES Allied_Companies(id_company)
);

--37
CREATE TABLE Maritime_Shipping_Office (
    id_building INT PRIMARY KEY,
    conection_warehouse INT NOT NULL,
    allied_company INT NOT NULL,
    radial_distance DECIMAL(4,2) NOT NULL,
    rute_distance DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (id_building) REFERENCES Building(id_building),
    FOREIGN KEY (conection_warehouse) REFERENCES Warehouse(id_warehouse),
    FOREIGN KEY (allied_company) REFERENCES Allied_Companies(id_company)
);

--38
CREATE TABLE Driver (
    username VARCHAR(255) PRIMARY KEY,
    identification_document VARCHAR(255) NOT NULL,
    born_date DATE NOT NULL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    salary DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (username) REFERENCES Users(username),
    FOREIGN KEY (identification_document) REFERENCES Identity_Document(identification_id)
);

--39
CREATE TABLE Motocyclist (
    username VARCHAR(255) PRIMARY KEY,
    assigned_motorcycle VARCHAR(17) NOT NULL,
    FOREIGN KEY (username) REFERENCES Driver(username),
    FOREIGN KEY (assigned_motorcycle) REFERENCES Motorcycle(vin_vehicle)
);

--40
CREATE TABLE Truck_Driver (
    username VARCHAR(255) PRIMARY KEY,
    assigned_truck VARCHAR(17) NOT NULL,
    FOREIGN KEY (username) REFERENCES Driver(username),
    FOREIGN KEY (assigned_truck) REFERENCES Truck(vin_vehicle)
);

--41 
CREATE TABLE Orders (
    order_number INT PRIMARY KEY,
    previus_order INT NOT NULL,
    generated_date DATE NOT NULL,
    generated_hour TIME NOT NULL,
    FOREIGN KEY (previus_order) REFERENCES Orders(order_number)
);

--42
CREATE TABLE Manual_order (
    order_number INT PRIMARY KEY,
    admin_verification VARCHAR(255) NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Orders(order_number),
    FOREIGN KEY (admin_verification) REFERENCES Admin_Cashier(username)
);

--43
CREATE TABLE Automatic_order (
    order_number INT PRIMARY KEY,
    admin_verification VARCHAR(255) NOT NULL,
    completed_date DATE NOT NULL,
    completed_hour TIME NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Orders(order_number),
    FOREIGN KEY (admin_verification) REFERENCES Admin_Package(username)
);

--44
CREATE TABLE Order_pay_confirmation (
    order_number INT PRIMARY KEY,
    id_pay INT NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Manual_order(order_number),
    FOREIGN KEY (id_pay) REFERENCES Pay(id_pay)
);

--45
CREATE TABLE Withdrawal_order (
    order_number INT PRIMARY KEY,
    client_user VARCHAR(255) NOT NULL,
    shipping_number INT NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Manual_order(order_number),
    FOREIGN KEY (client_user) REFERENCES Client(username),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_guide(shipping_number)
);

--46
CREATE TABLE Delivery_order (
    order_number INT PRIMARY KEY,
    motocyclist_user VARCHAR(255) NOT NULL,
    client_user VARCHAR(255) NOT NULL,
    shipping_number INT NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Automatic_order(order_number),
    FOREIGN KEY (motocyclist_user) REFERENCES Motocyclist(username),
    FOREIGN KEY (client_user) REFERENCES Client(username),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_guide(shipping_number)
);

--47
CREATE TABLE Warehouse_Transfer_Order (
    order_number INT PRIMARY KEY,
    truck_driver_user VARCHAR(255) NOT NULL,
    id_warehouse_transmitter INT NOT NULL,
    id_warehouse_receiver INT NOT NULL,
    shipping_number INT NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Automatic_order(order_number),
    FOREIGN KEY (truck_driver_user) REFERENCES Truck_Driver(username),
    FOREIGN KEY (id_warehouse_transmitter) REFERENCES Warehouse(id_warehouse),
    FOREIGN KEY (id_warehouse_receiver) REFERENCES Warehouse(id_warehouse),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_guide(shipping_number)
);

--48
CREATE TABLE Branch_Transfer_Order (
    order_number INT PRIMARY KEY,
    truck_driver_user VARCHAR(255) NOT NULL,
    shipping_number INT NOT NULL,
    warehouse_id INT NOT NULL,
    branch_id INT NOT NULL,
    withdrawal BOOLEAN NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Automatic_order(order_number),
    FOREIGN KEY (truck_driver_user) REFERENCES Truck_Driver(username),
    FOREIGN KEY (shipping_number) REFERENCES Shipping_guide(shipping_number),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(id_warehouse),
    FOREIGN KEY (branch_id) REFERENCES Branch(id_branch)
);

--49
CREATE TABLE Air_Cargo_Order (
    order_number INT PRIMARY KEY,
    truck_driver_user VARCHAR(255) NOT NULL,
    aerial_ship_number INT NOT NULL,
    warehouse_id INT NOT NULL,
    id_aerial_shipping_office INT NOT NULL,
    withdrawal BOOLEAN NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Automatic_order(order_number),
    FOREIGN KEY (truck_driver_user) REFERENCES Truck_Driver(username),
    FOREIGN KEY (aerial_ship_number) REFERENCES Air_Guide(shipping_number_air),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(id_warehouse),
    FOREIGN KEY (id_aerial_shipping_office) REFERENCES Aerial_Shipping_Office(id_building)
);

--50
CREATE TABLE Maritime_Cargo_Order (
    order_number INT PRIMARY KEY,
    truck_driver_user VARCHAR(255) NOT NULL,
    maritime_ship_number INT NOT NULL,
    warehouse_id INT NOT NULL,
    id_maritime_shipping_office INT NOT NULL,
    withdrawal BOOLEAN NOT NULL,
    FOREIGN KEY (order_number) REFERENCES Automatic_order(order_number),
    FOREIGN KEY (truck_driver_user) REFERENCES Truck_Driver(username),
    FOREIGN KEY (maritime_ship_number) REFERENCES Maritime_Guide(shipping_number_maritime),
    FOREIGN KEY (warehouse_id) REFERENCES Warehouse(id_warehouse),
    FOREIGN KEY (id_maritime_shipping_office) REFERENCES Maritime_Shipping_Office(id_building)
);

ALTER TABLE Warehouse
ADD FOREIGN KEY (id_warehouse) REFERENCES Building(id_building);

ALTER TABLE Region
ADD FOREIGN KEY (aerial_office_principal) REFERENCES Aerial_Shipping_Office(id_building);

ALTER TABLE Region
ADD FOREIGN KEY (maritime_office_principal) REFERENCES Maritime_Shipping_Office(id_building);