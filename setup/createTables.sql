--1
CREATE TABLE Vehiculo (
    vin BIGSERIAL NOT NULL PRIMARY KEY,
    matricula VARCHAR(50),
    marca VARCHAR(50),
    modelo VARCHAR(50),
    peso DECIMAL(10,2),
    largo DECIMAL(10,2),
    ancho DECIMAL(10,2),
    alto DECIMAL(10,2)
);
--2
CREATE TABLE Ente (
    id_ente BIGSERIAL PRIMARY KEY,
    direccion VARCHAR(50) NOT NULL,
    telefono VARCHAR(50) NOT NULL
);
--3
CREATE TABLE Paquete (
    num_tracking BIGSERIAL PRIMARY KEY,
    peso DECIMAL(10,2) NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    descripcion_contenido VARCHAR(50) NOT NULL,
    largo DECIMAL(10,2) NOT NULL,
    ancho DECIMAL(10,2) NOT NULL,
    alto DECIMAL(10,2) NOT NULL
);
--4
CREATE TABLE Cliente (
    id_ente BIGINT PRIMARY KEY,
    FOREIGN KEY (id_ente) REFERENCES Ente(id_ente)
);
--5
CREATE TABLE Cliente_Natural (
    id_cliente BIGSERIAL PRIMARY KEY,
    primer_nombre VARCHAR(50) NOT NULL,
    primer_apellido VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_ente)
);
--6
CREATE TABLE Cliente_Juridico (
    id_cliente BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_ente)
);
--7
CREATE TABLE Empleado (
    id_ente BIGINT PRIMARY KEY,
    fecha_nacimiento DATE NOT NULL,
    primer_nombre VARCHAR(50) NOT NULL,
    primer_apellido VARCHAR(50) NOT NULL,
    sueldo DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_ente) REFERENCES Ente(id_ente)
);
--8
CREATE TABLE Camionero (
    id_empleado BIGSERIAL PRIMARY KEY,
    FOREIGN KEY (id_empleado) REFERENCES Empleado(id_ente)
);
--9
CREATE TABLE Camion (
    vin_vehiculo BIGINT,
    camionero BIGINT,
    PRIMARY KEY (vin_vehiculo, camionero),
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin),
    FOREIGN KEY (camionero) REFERENCES Camionero(id_empleado)
);
--10
CREATE TABLE Motorizado (
    id_empleado BIGSERIAL PRIMARY KEY,
    FOREIGN KEY (id_empleado) REFERENCES Empleado(id_ente)
);
--11
CREATE TABLE Moto (
    vin_vehiculo BIGINT,
    motorizado BIGINT,
    PRIMARY KEY (vin_vehiculo, motorizado),
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin),
    FOREIGN KEY (motorizado) REFERENCES Motorizado(id_empleado)
);
--12
CREATE TABLE Pais (
    id_pais BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    prefijo_telefonico VARCHAR(50) NOT NULL
);
--13
CREATE TABLE Region (
    id_region BIGSERIAL PRIMARY KEY,
    id_pais BIGINT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_pais) REFERENCES Pais(id_pais)
);
--14
CREATE TABLE Ciudad (
    id_ciudad BIGSERIAL PRIMARY KEY,
    id_region BIGINT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_region) REFERENCES Region(id_region)
);
--15
CREATE TABLE Sucursal (
    id_sucursal BIGSERIAL PRIMARY KEY,
    id_ciudad BIGINT NOT NULL,
    FOREIGN KEY (id_ciudad) REFERENCES Ciudad(id_ciudad)
);
--16
CREATE TABLE Telefono_sucursal (
    id_sucursal BIGINT PRIMARY KEY,
    telefono VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_sucursal) REFERENCES Sucursal(id_sucursal)
);
--17
CREATE TABLE Retiro (
    num_tracking BIGINT PRIMARY KEY,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    FOREIGN KEY (num_tracking) REFERENCES Paquete(num_tracking)
);
--18
CREATE TABLE Traslado (
    id_traslado BIGSERIAL PRIMARY KEY,
    num_tracking BIGINT NOT NULL,
    id_camionero BIGINT NOT NULL,
    id_sucursal BIGINT NOT NULL,
    numero_orden BIGINT NOT NULL,
    fecha_llegada DATE NOT NULL,
    hora_llegada TIME NOT NULL,
    fecha_salida DATE NOT NULL,
    hora_salida TIME NOT NULL,
    FOREIGN KEY (num_tracking) REFERENCES Paquete(num_tracking),
    FOREIGN KEY (id_camionero) REFERENCES Camionero(id_empleado),
    FOREIGN KEY (id_sucursal) REFERENCES Sucursal(id_sucursal)
);
--19
CREATE TABLE Envio (
    num_tracking BIGINT PRIMARY KEY,
    id_cliente_envia BIGINT NOT NULL,
    id_cliente_recibe BIGINT NOT NULL,
    internacional BOOLEAN NOT NULL,
    fines_comerciales BOOLEAN NOT NULL,
    delivery_incluido BOOLEAN NOT NULL,
    fecha_envio DATE NOT NULL,
    hora_envio TIME NOT NULL,
    fecha_llegada_est DATE NOT NULL,
    hora_llegada_est TIME NOT NULL,
    FOREIGN KEY (num_tracking) REFERENCES Paquete(num_tracking),
    FOREIGN KEY (id_cliente_envia) REFERENCES Cliente(id_ente),
    FOREIGN KEY (id_cliente_recibe) REFERENCES Cliente(id_ente)
);
--20
CREATE TABLE Delivery (
    num_tracking BIGINT PRIMARY KEY,
    id_cliente_envia BIGINT NOT NULL,
    id_cliente_recibe BIGINT NOT NULL,
    id_motorizado BIGINT NOT NULL,
    fecha_entrega DATE NOT NULL,
    hora_entrega TIME NOT NULL,
    FOREIGN KEY (num_tracking) REFERENCES Paquete(num_tracking),
    FOREIGN KEY (id_cliente_envia) REFERENCES Cliente(id_ente),
    FOREIGN KEY (id_cliente_recibe) REFERENCES Cliente(id_ente),
    FOREIGN KEY (id_motorizado) REFERENCES Motorizado(id_empleado)
);
