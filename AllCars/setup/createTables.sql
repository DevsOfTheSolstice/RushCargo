--1
CREATE TABLE Descripcion_Vehiculo ( 
    id_descripcion BIGSERIAL NOT NULL PRIMARY KEY, 
    marca VARCHAR(50) NOT NULL, 
    fecha_lanzamiento DATE NOT NULL, 
    modelo VARCHAR(50) NOT NULL
);

--2
CREATE TABLE Aliemntacion_Electrixa(
    id_descripcion BIGINT NOT NULL,
    capacidad_watts INT NOT NULL,
    FOREIGN KEY (id_descripcion) REFERENCES Descripcion_Vehiculo(id_descripcion)
);

--3
CREATE TABLE Alimentacion_Combustion(
    id_descripcion BIGINT NOT NULL,
    capacidad_cilindros INT NOT NULL,
    litros_motor FLOAT NOT NULL,
    FOREIGN KEY (id_descripcion) REFERENCES Descripcion_Vehiculo(id_descripcion)
);

--4
CREATE TABLE Ente (
    id_ente BIGSERIAL PRIMARY KEY,
    telefono VARCHAR(15) NOT NULL,
    direccion VARCHAR(50) NOT NULL
);

--5
CREATE TABLE Seguro (
    id_seguro BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    porcentaje DECIMAL(5, 2) NOT NULL
);

--6
CREATE TABLE Taller (
    rif_taller VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    direccion VARCHAR(50) NOT NULL
);

--7
CREATE TABLE Proveedor (
    rif_proveedor VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    direccion VARCHAR(50) NOT NULL
);

--8
CREATE TABLE Repuesto (
    numero_parte VARCHAR(25) PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

--9
CREATE TABLE Carrera (
    id_carrera BIGSERIAL PRIMARY KEY,
    numero_vueltas INT NOT NULL,
    nombre_carrera VARCHAR(50) NOT NULL,
    nombre_circuito VARCHAR(50) NOT NULL,
    tipo_carrera VARCHAR(50) NOT NULL
);

--10
CREATE TABLE Piloto (
    id_piloto BIGSERIAL PRIMARY KEY,
    primer_nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    fecha_nacimiento DATE NOT NULL
);

--11
CREATE TABLE Edad_piloto (
    id_piloto BIGINT NOT NULL,
    edad INT NOT NULL,
    FOREIGN KEY (id_piloto) REFERENCES Piloto(id_piloto)
);

--12
CREATE TABLE Vehiculo (
    vin_vehiculo VARCHAR(25) PRIMARY KEY,
    id_descripcion BIGINT NOT NULL, 
    precio DECIMAL(10,2) NOT NULL,
    color VARCHAR(50) NOT NULL,
    kilometraje INT NOT NULL,
    matricula_vehiculo VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_descripcion) REFERENCES Descripcion_Vehiculo(id_descripcion)
);

--13
CREATE TABLE Carro (          
    id_carro VARCHAR(35) PRIMARY KEY,
    traccion INT NOT NULL,
    puertas INT NOT NULL,
    FOREIGN KEY (id_carro) REFERENCES Vehiculo(vin_vehiculo)
);

--14
CREATE TABLE Moto (
    id_moto VARCHAR(25) PRIMARY KEY,
    asientos INT NOT NULL,
    FOREIGN KEY (id_moto) REFERENCES Vehiculo(vin_vehiculo)
);

--15
CREATE TABLE Bicicleta (
    id_bicicleta VARCHAR(25) PRIMARY KEY,
    terreno VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_bicicleta) REFERENCES Vehiculo(vin_vehiculo)
);

--16
CREATE TABLE Tolva (
    id_tolva VARCHAR(25) PRIMARY KEY,
    capacidad_carga INT NOT NULL,
    FOREIGN KEY (id_tolva) REFERENCES Vehiculo(vin_vehiculo)
);

--17
CREATE TABLE Tractor (
    id_tractor VARCHAR(25) PRIMARY KEY,
    traccion INT NOT NULL,
    terreno VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_tractor) REFERENCES Vehiculo(vin_vehiculo)
);

--18
CREATE TABLE Cisterna (
    id_cisterna VARCHAR(25) PRIMARY KEY,
    tipo_liquido VARCHAR(50) NOT NULL,
    capacidad_carga INT NOT NULL,
    FOREIGN KEY (id_cisterna) REFERENCES Vehiculo(vin_vehiculo)
);

--19
CREATE TABLE Camion_Plataforma (
    id_camion VARCHAR(25) PRIMARY KEY,
    tipo_plataforma VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_camion) REFERENCES Vehiculo(vin_vehiculo)
);

--20
CREATE TABLE Cliente (
    id_cliente BIGSERIAL PRIMARY KEY,
    FOREIGN KEY (id_cliente) REFERENCES Ente(id_ente)
);

--21
CREATE TABLE Cliente_Natural (
    ci_cliente_natural BIGINT PRIMARY KEY,
    id_cliente BIGINT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente)
);

--22
CREATE TABLE Cliente_Juridico (
    rif VARCHAR(15) PRIMARY KEY,
    id_cliente BIGINT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente)
); 

--23
CREATE TABLE Empleado (
    ci_empleado BIGINT PRIMARY KEY,
    id_ente BIGINT NOT NULL,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    cargo VARCHAR(50) NOT NULL,
    sueldo DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (id_ente) REFERENCES Ente(id_ente)
);

--24
CREATE TABLE Factura (
    id_factura BIGSERIAL PRIMARY KEY,
    ci_empleado BIGINT NOT NULL,
    id_cliente BIGINT NOT NULL,
    tipo_factura VARCHAR(50) NOT NULL,
    bono DECIMAL(10, 2),
    dia DATE NOT NULL,
    hora TIME NOT NULL,
    FOREIGN KEY (ci_empleado) REFERENCES Empleado(ci_empleado),
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente)
);

--25
CREATE TABLE Detalle (
    id_detalle BIGSERIAL PRIMARY KEY,
    id_factura BIGINT NOT NULL,
    vin_vehiculo VARCHAR(25) NOT NULL,
    id_seguro BIGINT NOT NULL,
    precio_neto DECIMAL(10, 2) NOT NULL,
    impuestos DECIMAL(10, 2) NOT NULL,
    descuento DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (id_factura) REFERENCES Factura(id_factura),
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo),
    FOREIGN KEY (id_seguro) REFERENCES Seguro(id_seguro)
);

--26
CREATE TABLE Detalle_Total (
    id_detalle BIGINT NOT NULL,
    precio_total DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (id_detalle) REFERENCES Detalle(id_detalle)
);

--27
CREATE TABLE Propietario_Vehiculo (
    id_cliente BIGINT NOT NULL,
    vin_vehiculo VARCHAR(25) NOT NULL,
    dia_compra DATE NOT NULL,
    hora_compra TIME NOT NULL,
    propietario_actual BOOLEAN NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente),
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo)
);

--28
CREATE TABLE Repuesto_Suministrado (
    rif_taller VARCHAR(50) NOT NULL,
    rif_proveedor VARCHAR(50) NOT NULL,
    numero_parte VARCHAR(25) NOT NULL,
    cantidad INT NOT NULL,
    FOREIGN KEY (rif_taller) REFERENCES Taller(rif_taller),
    FOREIGN KEY (rif_proveedor) REFERENCES Proveedor(rif_proveedor),
    FOREIGN KEY (numero_parte) REFERENCES Repuesto(numero_parte)
);

--29
CREATE TABLE Vehiculo_Reparado (
    vin_vehiculo VARCHAR(50) NOT NULL,
    rif_proveedor VARCHAR(50) NOT NULL,
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo),
    FOREIGN KEY (rif_proveedor) REFERENCES Proveedor(rif_proveedor)
);

--30
CREATE TABLE Vehiculo_Distribuido (        
    vin_vehiculo VARCHAR(50) NOT NULL,
    rif_taller VARCHAR(50) NOT NULL,
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo),
    FOREIGN KEY (rif_taller) REFERENCES Taller(rif_taller)
);

--31
CREATE TABLE Pits (
    rif_taller VARCHAR(50) NOT NULL,
    vin_vehiculo VARCHAR(50) NOT NULL,
    id_carrera BIGINT NOT NULL,
    FOREIGN KEY (rif_taller) REFERENCES Taller(rif_taller),
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo),
    FOREIGN KEY (id_carrera) REFERENCES Carrera(id_carrera)
);

--32
CREATE TABLE Participante_Carrera (
    id_carrera BIGINT NOT NULL,
    id_carro VARCHAR(50) NOT NULL,
    id_piloto BIGINT NOT NULL,
    FOREIGN KEY (id_piloto) REFERENCES Piloto(id_piloto),
    FOREIGN KEY (id_carro) REFERENCES Carro(id_carro),
    FOREIGN KEY (id_carrera) REFERENCES Carrera(id_carrera)
);

--33
CREATE TABLE Evento (
    id_evento BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
        fecha DATE NOT NULL
);

--34
CREATE TABLE Exposicion_Evento (
    id_evento BIGINT NOT NULL,
    vin_vehiculo VARCHAR(50) NOT NULL,
    tipo_transaccion VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_evento) REFERENCES Evento(id_evento),
    FOREIGN KEY (vin_vehiculo) REFERENCES Vehiculo(vin_vehiculo)
);