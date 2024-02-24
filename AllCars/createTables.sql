CREATE TABLE Descripcion_Vehiculo ( 
    id_descripcion BIGSERIAL NOT NULL PRIMARY KEY, 
    marca VARCHAR(50) NOT NULL, 
    fecha_lanzamiento DATE NOT NULL, 
    modelo VARCHAR(50) NOT NULL, 
    tipo_alimentacion VARCHAR(50) NOT NULL, 
    capacidad_watts INT, 
    cantidad_cilindros INT, 
    litros_motor FLOAT 
);

CREATE TABLE Vehiculo (
    vin_vehiculo BIGSERIAL PRIMARY KEY,
    id_descripcion BIGINT, 
    precio DECIMAL(10,2) NOT NULL,
    color VARCHAR(50) NOT NULL,
    kilometraje INT,
    matricula_vehiculo VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_descripcion) REFERENCES Descripcion_Vehiculo(id_descripcion)
);

CREATE TABLE Carro (
    id_carro BIGSERIAL PRIMARY KEY,
    vin_vehiculo BIGINT,
    traccion INT(2, 4),
    puertas INT(2, 4),
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo)
);

CREATE TABLE Moto (
    id_moto BIGSERIAL PRIMARY KEY,
    vin_vehiculo BIGINT,
    asientos INT(1, 2),
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo)
);

CREATE TABLE Bicicleta (
    id_bicicleta BIGSERIAL PRIMARY KEY,
    vin_vehiculo BIGINT,
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo)
);

CREATE TABLE Tolva (
    id_tolva BIGSERIAL PRIMARY KEY,
    vin_vehiculo BIGINT,
    capacidad_carga INT(1000, 50000),
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo)
);

CREATE TABLE Tractor (
    id_tractor BIGSERIAL PRIMARY KEY,
    vin_vehiculo BIGINT,
    traccion INT(2, 4),
    terreno VARCHAR(50) NOT NULL,
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo)
);

CREATE TABLE Cisterna (
    id_cisterna BIGSERIAL PRIMARY KEY,
    vin_vehiculo BIGINT,
    tipo_liquido VARCHAR(50) NOT NULL,
    capacidad_carga INT(1000, 50000),
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo)
);

CREATE TABLE Camion_Plataforma (
    id_camion BIGSERIAL PRIMARY KEY,
    vin_vehiculo BIGINT,
    tipo_plataforma VARCHAR(50) NOT NULL,
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo)
);

CREATE TABLE Ente (
    id BIGSERIAL PRIMARY KEY,
    telefono VARCHAR(15) NOT NULL,
    direccion VARCHAR(255) NOT NULL
);

CREATE TABLE Clientes (
    id_cliente BIGSERIAL PRIMARY KEY,
    id_ente BIGINT,
    FOREIGN KEY (id_ente) REFERENCES Ente(id)
);

CREATE TABLE Cliente_Natural (
    ci BIGINT PRIMARY KEY NOT NULL,
    id_cliente BIGINT,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente)
);

CREATE TABLE Cliente_Juridico (
    rif VARCHAR(15) PRIMARY KEY NOT NULL,
    id_cliente BIGINT,
    nombre VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente)
); 

CREATE TABLE Seguro (
    id_seguro BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(50),
    porcentaje DECIMAL(5, 2)
);

CREATE TABLE Empleado (
    ci_empleado BIGINT PRIMARY KEY,
    id_ente BIGINT,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    cargo VARCHAR(50) NOT NULL,
    sueldo DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (id_ente) REFERENCES Ente(id)
);

CREATE TABLE Factura(
    id_factura BIGSERIAL PRIMARY KEY,
    ci_empleado BIGINT NOT NULL,
    id_cliente BIGINT NOT NULL,
    tipo_de_factura VARCHAR(50) NOT NULL,
    bono DECIMAL(10, 2),
    dia DATE NOT NULL,
    hora TIME NOT NULL,
    FOREIGN KEY (ci_empleado) REFERENCES Empleado(ci_empleado),
    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente)
);

CREATE TABLE Detalle (
    id_detalle BIGSERIAL PRIMARY KEY,
    id_factura BIGINT NOT NULL,
    id_vehiculo BIGINT NOT NULL,
    id_seguro BIGINT NOT NULL,
    precio_neto DECIMAL(10, 2) NOT NULL,
    impuestos DECIMAL(10, 2) NOT NULL,
    descuento DECIMAL(10, 2) NOT NULL,
    precio_total DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (id_factura) REFERENCES Factura(id_factura),
    FOREIGN KEY (id_vehiculo) REFERENCES Vehiculo(vin_vehiculo),
    FOREIGN KEY (id_seguro) REFERENCES Seguro(id_seguro)
);
