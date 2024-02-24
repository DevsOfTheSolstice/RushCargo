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
