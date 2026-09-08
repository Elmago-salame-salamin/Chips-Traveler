CREATE DATABASE IF NOT EXISTS club_ciencias;

USE club_ciencias;


-- =========================
-- TABLA ALUMNOS
-- =========================

CREATE TABLE IF NOT EXISTS alumnos (
    dni VARCHAR(20) PRIMARY KEY,
    nombre VARCHAR(50),
    apellido VARCHAR(50)
);


-- =========================
-- TABLA COMPONENTES
-- =========================

CREATE TABLE IF NOT EXISTS componentes (
    id_componente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50),
    stock INT
);


-- =========================
-- TABLA PRÉSTAMOS
-- =========================

CREATE TABLE IF NOT EXISTS prestamos (
    id_prestamo INT AUTO_INCREMENT PRIMARY KEY,
    id_alumno VARCHAR(20),
    id_componente INT,
    fecha_retiro DATE,

    FOREIGN KEY (id_alumno)
        REFERENCES alumnos(dni),

    FOREIGN KEY (id_componente)
        REFERENCES componentes(id_componente)
);