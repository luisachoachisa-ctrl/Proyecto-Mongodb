CREATE DATABASE AlfajoresDB;
GO

USE AlfajoresDB;
GO


CREATE TABLE Clientes (
    id_cliente INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    direccion_defecto VARCHAR(200) NULL
);


CREATE TABLE Categorias_Tamano (
    id_categoria INT IDENTITY(1,1) PRIMARY KEY,
    nombre_tamano VARCHAR(50) NOT NULL,
    descripcion_gramos VARCHAR(200) NULL
);


CREATE TABLE Sabores (
    id_sabor INT IDENTITY(1,1) PRIMARY KEY,
    nombre_sabor VARCHAR(50) NOT NULL,
);


CREATE TABLE Producto (
    id_producto INT IDENTITY(1,1) PRIMARY KEY,
    id_sabor INT NOT NULL,
    id_categoria INT NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_categoria) REFERENCES Categorias_Tamano(id_categoria),
    FOREIGN KEY (id_sabor) REFERENCES Sabores(id_sabor)
);


CREATE TABLE Inventario (
    id_inventario INT IDENTITY(1,1) PRIMARY KEY,
    id_producto INT UNIQUE NOT NULL,
    stock_disponible INT NOT NULL,
    fecha_actualizacion DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (id_producto) REFERENCES Producto(id_producto)
);


CREATE TABLE Tipos_Entrega (
    id_tipo_entrega INT IDENTITY(1,1) PRIMARY KEY,
    nombre_modalidad VARCHAR(50) NOT NULL
);


CREATE TABLE Pedidos (
    id_pedido INT IDENTITY(1,1) PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_tipo_entrega INT NOT NULL,
    fecha_pedido DATETIME DEFAULT GETDATE(),
    estado_pedido VARCHAR(30), 
    monto_total DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES Clientes(id_cliente),
    FOREIGN KEY (id_tipo_entrega) REFERENCES Tipos_Entrega(id_tipo_entrega)
);


CREATE TABLE Detalle_Pedidos (
    id_detalle INT IDENTITY(1,1) PRIMARY KEY,
    id_pedido INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_pedido) REFERENCES Pedidos(id_pedido),
    FOREIGN KEY (id_producto) REFERENCES Producto(id_producto)
);


CREATE TABLE Envios_Nacionales (
    id_envio INT IDENTITY(1,1) PRIMARY KEY,
    id_pedido INT UNIQUE NOT NULL,
    empresa_transporte VARCHAR(50) NOT NULL,
    numero_guia VARCHAR(100) NOT NULL,
    direccion_destino VARCHAR(200) NOT NULL,
    costo_envio DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_pedido) REFERENCES Pedidos(id_pedido)
);

ALTER TABLE Envios_Nacionales DROP COLUMN ciudad;
ALTER TABLE Envios_Nacionales DROP COLUMN departamento;


CREATE TABLE Pagos (
    id_pago INT IDENTITY(1,1) PRIMARY KEY,
    id_pedido INT NOT NULL,
    metodo_pago VARCHAR(50) NOT NULL, 
    monto_pagado DECIMAL(10,2) NOT NULL,
    fecha_pago DATETIME DEFAULT GETDATE(),
    estado_pago VARCHAR(30),
    FOREIGN KEY (id_pedido) REFERENCES Pedidos(id_pedido)
);


SELECT * FROM Sabores;

DELETE FROM Sabores
WHERE id_sabor BETWEEN 12 AND 22;

SELECT *FROM Producto;
SELECT *FROM Inventario;

Select *from Clientes;