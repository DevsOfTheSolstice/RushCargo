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

CREATE TABLE Ente (
    id_ente BIGSERIAL PRIMARY KEY,
    telefono VARCHAR(15) NOT NULL,
    direccion VARCHAR(255) NOT NULL
);

CREATE TABLE Seguro (
    id_seguro BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    porcentaje DECIMAL(5, 2) NOT NULL
);

CREATE TABLE Taller (
    rif_taller VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    direccion VARCHAR(50) NOT NULL,
);

CREATE TABLE Proveedor (
    rif_proveedor VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    direccion VARCHAR(50) NOT NULL,
);

CREATE TABLE Repuesto (
    numero_parte_repuesto VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
);

CREATE TABLE Carrera (
    id_carrera BIGSERIAL PRIMARY KEY,
    numero_vueltas INT NOT NULL,
    nombre_carrera VARCHAR(50) NOT NULL,
    nombre_circuito VARCHAR(50) NOT NULL,
    tipo_carrera VARCHAR(50) NOT NULL,
);

CREATE TABLE Piloto (
    id_piloto BIGSERIAL PRIMARY KEY,
    primer_nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    edad INT NOT NULL
);

CREATE TABLE Vehiculo (
    vin_vehiculo BIGSERIAL PRIMARY KEY,
    id_descripcion BIGINT NOT NULL, 
    precio DECIMAL(10,2) NOT NULL,
    color VARCHAR(50) NOT NULL,
    kilometraje INT NOT NULL,
    matricula_vehiculo VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_descripcion) REFERENCES Descripcion_Vehiculo(id_descripcion)
);

CREATE TABLE Carro (
    id_carro BIGSERIAL PRIMARY KEY,
    vin_vehiculo BIGINT NOT NULL,
    traccion INT(2, 4) NOT NULL,
    puertas INT(2, 4) NOT NULL,
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo)
);

CREATE TABLE Moto (
    id_moto BIGSERIAL PRIMARY KEY,
    vin_vehiculo BIGINT NOT NULL,
    asientos INT(1, 2) NOT NULL,
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo)
);

CREATE TABLE Bicicleta (
    id_bicicleta BIGSERIAL PRIMARY KEY,
    vin_vehiculo BIGINT NOT NULL,
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo)
);

CREATE TABLE Tolva (
    id_tolva BIGSERIAL PRIMARY KEY,
    vin_vehiculo BIGINT NOT NULL,
    capacidad_carga INT(1000, 50000) NOT NULL,
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo)
);

CREATE TABLE Tractor (
    id_tractor BIGSERIAL PRIMARY KEY,
    vin_vehiculo BIGINT NOT NULL,
    traccion INT(2, 4) NOT NULL,
    terreno VARCHAR(50) NOT NULL,
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo)
);

CREATE TABLE Cisterna (
    id_cisterna BIGSERIAL PRIMARY KEY,
    vin_vehiculo BIGINT NOT NULL,
    tipo_liquido VARCHAR(50) NOT NULL,
    capacidad_carga INT(1000, 50000) NOT NULL,
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo)
);

CREATE TABLE Camion_Plataforma (
    id_camion BIGSERIAL PRIMARY KEY,
    vin_vehiculo BIGINT NOT NULL,
    tipo_plataforma VARCHAR(50) NOT NULL,
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo)
);

CREATE TABLE Cliente (
    id_cliente BIGSERIAL PRIMARY KEY,
    id_ente BIGINT NOT NULL,
    FOREIGN KEY (id_ente) REFERENCES Ente(id_ente)
);

CREATE TABLE Cliente_Natural (
    ci_cliente_natural BIGINT PRIMARY KEY,
    id_cliente BIGINT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente)
);

CREATE TABLE Cliente_Juridico (
    rif_proveedor VARCHAR(15) PRIMARY KEY,
    id_cliente BIGINT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente)
); 

CREATE TABLE Empleado (
    ci_empleado BIGINT PRIMARY KEY,
    id_ente BIGINT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    cargo VARCHAR(50) NOT NULL,
    sueldo DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (id_ente) REFERENCES Ente(id)
);

CREATE TABLE Factura (
    id_factura BIGSERIAL PRIMARY KEY,
    ci_empleado BIGINT NOT NULL,
    id_cliente BIGINT NOT NULL,
    tipo_factura VARCHAR(50) NOT NULL,
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

CREATE TABLE Repuesto_Suministrado (
    rif_taller VARCHAR(50) NOT NULL,
    rif_proveedor VARCHAR(50) NOT NULL,
    numero_parte BIGINT NOT NULL,
    cantidad INT(1, 1000) NOT NULL,
    FOREIGN KEY (rif_taller) REFERENCES Taller(rif_taller),
    FOREIGN KEY (rif_proveedor) REFERENCES Proveedor(rif_proveedor),
    FOREIGN KEY (numero_parte) REFERENCES Repuesto(numero_parte)
);

CREATE TABLE Vehiculo_Reparado (
    vin_vehiculo VARCHAR(50) NOT NULL,
    rif_proveedor VARCHAR(50) NOT NULL,
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo),
    FOREIGN KEY (rif_proveedor) REFERENCES Proveedor(rif_proveedor)
);

CREATE TABLE Vehiculo_Distribuido (        
    vin_vehiculo VARCHAR(50) NOT NULL,
    rif_taller VARCHAR(50) NOT NULL,
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo),
    FOREIGN KEY (rif_taller) REFERENCES Taller(rif_taller)
);

CREATE TABLE Pits (
    rif_taller VARCHAR(50) NOT NULL,
    vin_vehiculo VARCHAR(50) NOT NULL,
    id_carrera BIGINT NOT NULL,
    FOREIGN KEY (rif_taller) REFERENCES Taller(rif_taller),
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo),
    FOREIGN KEY (id_carrera) REFERENCES Carrera(id_carrera)
);

CREATE TABLE Participante_Carrera (
    id_carrera BIGINT NOT NULL,
    id_carro BIGINT NOT NULL,
    id_piloto BIGINT NOT NULL,
    FOREIGN KEY (id_piloto) REFERENCES Piloto(id_piloto),
    FOREIGN KEY (id_carro) REFERENCES Carro(id_carro),
    FOREIGN KEY (id_carrera) REFERENCES Carrera(id_carrera)
);