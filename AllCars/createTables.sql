CREATE TABLE Descripcion_Vehiculo ( 
    id BIGSERIAL NOT NULL PRIMARY KEY, 
    marca VARCHAR(50) NOT NULL, 
    fecha_lanzamiento DATE NOT NULL, 
    modelo VARCHAR(50) NOT NULL, 
    tipo_alimentacion VARCHAR(50) NOT NULL, 
    capacidad_watts INT, 
    cantidad_cilindros INT, 
    litros_motor FLOAT 
);

CREATE TABLE Vehiculo (
    vin BIGSERIAL PRIMARY KEY,
    id_descripcion BIGINT, 
    precio DECIMAL(10,2) NOT NULL,
    color VARCHAR(50) NOT NULL,
    kilometraje INT,
    matricula VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_descripcion) REFERENCES Descripcion_Vehiculo(id)
);

CREATE TABLE Ente (
    id BIGSERIAL PRIMARY KEY,
    telefono VARCHAR(15) NOT NULL,
    direccion VARCHAR(255) NOT NULL
);

CREATE TABLE Clientes (
    id BIGSERIAL PRIMARY KEY,
    id_ente BIGINT,
    FOREIGN KEY (id_ente) REFERENCES Ente(id)
);

CREATE TABLE Cliente_Natural (
    ci BIGINT PRIMARY KEY,
    id_cliente BIGINT,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES Clientes(id)
);

CREATE TABLE Cliente_Juridico (
    rif VARCHAR(15) PRIMARY KEY,
    id_cliente BIGINT,
    nombre VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES Clientes(id)
); 