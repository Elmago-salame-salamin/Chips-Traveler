-- ==========================================
-- CREAR BASE DE DATOS
-- ==========================================

CREATE DATABASE IF NOT EXISTS traveler
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE traveler;


-- ==========================================
-- TABLA DE CLIENTES
-- ==========================================

CREATE TABLE IF NOT EXISTS clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    dni VARCHAR(20),
    telefono VARCHAR(30) NOT NULL,
    email VARCHAR(150),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ==========================================
-- TABLA DE LUGARES
-- ==========================================

CREATE TABLE IF NOT EXISTS lugares (
    id_lugar INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    ubicacion VARCHAR(255) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10,2),
    valoracion DECIMAL(2,1) DEFAULT 0.0,
    imagen VARCHAR(255)
);


-- ==========================================
-- TABLA DE RESERVAS
-- ==========================================

CREATE TABLE IF NOT EXISTS reservas (
    id_reserva INT AUTO_INCREMENT PRIMARY KEY,

    id_cliente INT NOT NULL,
    id_lugar INT NOT NULL,

    fecha DATE NOT NULL,
    hora TIME,

    personas INT DEFAULT 1,
    entradas INT DEFAULT 1,

    observaciones TEXT,

    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (id_cliente)
        REFERENCES clientes(id_cliente)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    FOREIGN KEY (id_lugar)
        REFERENCES lugares(id_lugar)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);


-- ==========================================
-- INSERTAR LOS 8 LUGARES
-- ==========================================

INSERT INTO lugares
(nombre, categoria, ubicacion, descripcion, precio, valoracion)
VALUES

(
    'La Casa del Ceibo',
    'hotel',
    'Córdoba, Argentina',
    'Alojamiento ubicado en Córdoba Capital.',
    NULL,
    4.8
),

(
    'Nuna Ayni Departamentos Hotel',
    'hotel',
    'Alta Gracia, Córdoba',
    'Departamentos ideales para alojarse en Alta Gracia.',
    NULL,
    4.7
),

(
    'Ñu Posta Urbana',
    'hotel',
    'Córdoba, Argentina',
    'Hotel ubicado en la zona del Cerro de las Rosas.',
    NULL,
    4.6
),

(
    'La Casa de la Empanada',
    'restaurante',
    'General Paz, Córdoba',
    'Restaurante especializado en empanadas y pizzas.',
    NULL,
    4.5
),

(
    'Santa Calma',
    'restaurante',
    'Córdoba, Argentina',
    'Restaurante ubicado en la zona del Parque Sarmiento.',
    NULL,
    4.7
),

(
    'Café de Barrio',
    'restaurante',
    'Córdoba, Argentina',
    'Café de especialidad y gastronomía.',
    NULL,
    4.6
),

(
    'Súper Park Córdoba',
    'atraccion',
    'Córdoba, Argentina',
    'Parque de diversiones ubicado en Parque Sarmiento.',
    NULL,
    4.4
),

(
    'Infinito Water Park',
    'atraccion',
    'Córdoba, Argentina',
    'Parque acuático para disfrutar en familia y con amigos.',
    NULL,
    4.6
);

-- English Comment: Create users table supporting authentication, profile customizations, and Terms acceptance logging.
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    descripcion TEXT,
    foto_perfil VARCHAR(255) DEFAULT 'default_avatar.png',
    acepto_terminos TINYINT(1) NOT NULL DEFAULT 0,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

