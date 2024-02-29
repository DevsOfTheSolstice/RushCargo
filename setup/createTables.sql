--1
CREATE TABLE Moto (
    vin BIGSERIAL PRIMARY KEY,
    matricula VARCHAR(50) NOT NULL,
    marca VARCHAR(50),
    modelo VARCHAR(50),
    cap_peso DECIMAL(10,2) NOT NULL,
    cap_largo DECIMAL(10,2) NOT NULL,
    cap_ancho DECIMAL(10,2) NOT NULL,
    cap_alto DECIMAL(10,2) NOT NULL
);
--2
CREATE TABLE Camion (
    vin BIGSERIAL PRIMARY KEY,
    matricula VARCHAR(50) NOT NULL,
    marca VARCHAR(50),
    modelo VARCHAR(50),
    cap_peso DECIMAL(10,2) NOT NULL,
    cap_largo DECIMAL(10,2) NOT NULL,
    cap_ancho DECIMAL(10,2) NOT NULL,
    cap_alto DECIMAL(10,2) NOT NULL
);
--3
CREATE TABLE Camionero (
    id BIGINT PRIMARY KEY,
    camion_asignado BIGSERIAL,
    telefono BIGINT,
    direccion VARCHAR(50),
    fecha_nacimiento DATE,
    primer_nombre VARCHAR(50) NOT NULL,
    primer_apellido VARCHAR(50) NOT NULL,
    sueldo BIGINT NOT NULL,
    FOREIGN KEY (camion_asignado) REFERENCES Camion(vin)
);
CREATE TABLE Pais (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    prefijo_telefonico VARCHAR(50) NOT NULL
);
--12
CREATE TABLE Region (
    id BIGSERIAL PRIMARY KEY,
    id_pais BIGINT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_pais) REFERENCES Pais(id)
);

CREATE TABLE Ciudad (
    id BIGSERIAL PRIMARY KEY,
    id_region BIGINT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_region) REFERENCES Region(id)
);
--6
CREATE TABLE Cliente (
    id BIGSERIAL PRIMARY KEY,
    ciudad_actual BIGSERIAL NOT NULL,
    telefono BIGINT,
    direccion VARCHAR(50),
    FOREIGN KEY (ciudad_actual) REFERENCES Ciudad(id)
);
--4
CREATE TABLE Motorizado (
    id BIGINT PRIMARY KEY,
    moto_asignada BIGSERIAL,
    telefono BIGINT,
    direccion VARCHAR(50),
    fecha_nacimiento DATE,
    primer_nombre VARCHAR(50) NOT NULL,
    primer_apellido VARCHAR(50) NOT NULL,
    sueldo BIGINT NOT NULL,
    FOREIGN KEY (moto_asignada) REFERENCES Moto(vin)
);
--10
CREATE TABLE Guia_Envio (
    num_envio BIGSERIAL PRIMARY KEY,
    id_cliente BIGINT,
    fines_comerciales BOOLEAN,
    envio_internacional BOOLEAN,
    delivery_incluido BOOLEAN,
    costo_envio DECIMAL(10,2),
    fecha_envio DATE,
    hora_envio TIME,
    fecha_estimada_llegada DATE,
    hora_estimada_llegada TIME,
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id)
);
--5
CREATE TABLE Paquete (
    num_tracking BIGSERIAL PRIMARY KEY,
    num_envio BIGINT,
    peso DECIMAL(10,2) NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    desc_contenido VARCHAR(50) NOT NULL,
    largo DECIMAL(10,2) NOT NULL,
    ancho DECIMAL(10,2) NOT NULL,
    alto DECIMAL(10,2) NOT NULL
);

--7
CREATE TABLE Cliente_Natural (
    id BIGINT PRIMARY KEY,
    primer_nombre VARCHAR(50) NOT NULL,
    primer_apellido VARCHAR(50) NOT NULL,
    FOREIGN KEY (id) REFERENCES Cliente(id)
);
--8
CREATE TABLE Cliente_Juridico (
    id BIGINT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    FOREIGN KEY (id) REFERENCES Cliente(id)
);

--14
CREATE TABLE Sucursal (
    id_sucursal BIGSERIAL PRIMARY KEY,
    id_ciudad BIGINT NOT NULL,
    direccion VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_ciudad) REFERENCES Ciudad(id)
);
--9
CREATE TABLE Envios_Cliente (
    num_tracking BIGINT PRIMARY KEY,
    id_cliente_emisor BIGINT,
    id_cliente_destino BIGINT,
    id_sucursal_emisor BIGINT,
    id_sucursal_destino BIGINT,
    FOREIGN KEY (num_tracking) REFERENCES Paquete(num_tracking),
    FOREIGN KEY (id_cliente_emisor) REFERENCES Cliente(id),
    FOREIGN KEY (id_cliente_destino) REFERENCES Cliente(id),
    FOREIGN KEY (id_sucursal_emisor) REFERENCES Sucursal(id_sucursal),
    FOREIGN KEY (id_sucursal_destino) REFERENCES Sucursal(id_sucursal)
);

--15
CREATE TABLE Telefonos_sucursal (
    id_sucursal BIGINT PRIMARY KEY,
    telefono BIGINT NOT NULL,
    FOREIGN KEY (id_sucursal) REFERENCES Sucursal(id_sucursal)
);
--16
CREATE TABLE Retira_Paquete (
    num_tracking BIGINT PRIMARY KEY,
    id_cliente_receptor BIGINT NOT NULL,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    FOREIGN KEY (num_tracking) REFERENCES Paquete(num_tracking)
);
--19
CREATE TABLE Orden_Delivery (
    num_orden BIGINT PRIMARY KEY,
    id_sucursal_salida BIGINT,
    id_motorizado BIGINT,
    fecha_salida DATE,
    hora_salida TIME,
    FOREIGN KEY (id_sucursal_salida) REFERENCES Sucursal(id_sucursal)
);
--17
CREATE TABLE Paquete_Delivery (
    num_tracking BIGINT PRIMARY KEY,
    num_orden BIGINT NOT NULL,
    FOREIGN KEY (num_tracking) REFERENCES Paquete(num_tracking),
    FOREIGN KEY (num_orden) REFERENCES Orden_Delivery(num_orden)
);
--18
CREATE TABLE Orden_Traslado (
    num_orden BIGINT PRIMARY KEY,
    id_sucursal_salida BIGINT NOT NULL,
    id_sucursal_destino BIGINT NOT NULL,
    id_camionero BIGINT NOT NULL,
    fecha_salida DATE,
    hora_salida TIME,
    status_salida VARCHAR(50) NOT NULL,
    status_llegada VARCHAR(50) NOT NULL
);
--20
CREATE TABLE Paquete_Traslado (
    num_orden BIGINT PRIMARY KEY,
    num_tracking BIGINT,
    FOREIGN KEY (num_orden) REFERENCES Orden_Traslado(num_orden),
    FOREIGN KEY (num_tracking) REFERENCES Paquete(num_tracking)
);
--21
CREATE TABLE Recibe_Delivery (
    num_tracking BIGINT PRIMARY KEY,
    id_cliente_receptor BIGINT NOT NULL,
    FOREIGN KEY (num_tracking) REFERENCES Paquete(num_tracking),
    FOREIGN KEY (id_cliente_receptor) REFERENCES Cliente(id)
);