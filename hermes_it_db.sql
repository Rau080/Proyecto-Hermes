-- -----------------------------------------------------
-- Schema hermes_it_db
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `hermes_it_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE `hermes_it_db`;

-- -----------------------------------------------------
-- Table `cliente`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cliente` (
  `id_cliente` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `nombre_completo` VARCHAR(150) NOT NULL,
  `correo_electronico` VARCHAR(150) NOT NULL,
  `telefono` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`id_cliente`),
  UNIQUE INDEX `correo_UNIQUE` (`correo_electronico` ASC)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `departamento`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `departamento` (
  `id_departamento` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(100) NOT NULL,
  `ubicacion` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id_departamento`)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `operador`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `operador` (
  `id_operador` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(150) NOT NULL,
  `correo_corporativo` VARCHAR(150) NOT NULL,
  `id_departamento` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id_operador`),
  CONSTRAINT `fk_operador_departamento`
    FOREIGN KEY (`id_departamento`)
    REFERENCES `departamento` (`id_departamento`)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `ticket`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ticket` (
  `codigo_ticket` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `titulo` VARCHAR(200) NOT NULL,
  `descripcion` TEXT NOT NULL,
  `fecha_creacion` DATETIME NOT NULL,
  `fecha_cierre` DATETIME NULL,  -- Debe ser NULL porque al abrir no está cerrado
  `categoria` VARCHAR(100) NOT NULL,
  `prioridad` ENUM('Baja', 'Media', 'Alta', 'Crítica') NOT NULL,
  `estado` ENUM('Abierto', 'En Proceso', 'Cerrado', 'Archivado') NOT NULL DEFAULT 'Abierto',
  `id_cliente` INT UNSIGNED NOT NULL,
  `id_operador` INT UNSIGNED NULL, -- Debe ser NULL porque un ticket nuevo no tiene operador
  PRIMARY KEY (`codigo_ticket`),
  CONSTRAINT `fk_ticket_cliente`
    FOREIGN KEY (`id_cliente`)
    REFERENCES `cliente` (`id_cliente`),
  CONSTRAINT `fk_ticket_operador`
    FOREIGN KEY (`id_operador`)
    REFERENCES `operador` (`id_operador`)
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `mensaje`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mensaje` (
  `id_mensaje` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `cuerpo` TEXT NOT NULL,
  `fecha_envio` DATETIME NOT NULL,
  `codigo_ticket` INT UNSIGNED NOT NULL,
  `id_cliente_autor` INT UNSIGNED NULL,   -- Debe permitir NULL por exclusividad
  `id_operador_autor` INT UNSIGNED NULL,  -- Debe permitir NULL por exclusividad
  PRIMARY KEY (`id_mensaje`),
  CONSTRAINT `fk_mensaje_ticket`
    FOREIGN KEY (`codigo_ticket`)
    REFERENCES `ticket` (`codigo_ticket`),
  CONSTRAINT `fk_mensaje_cliente`
    FOREIGN KEY (`id_cliente_autor`)
    REFERENCES `cliente` (`id_cliente`),
  CONSTRAINT `fk_mensaje_operador`
    FOREIGN KEY (`id_operador_autor`)
    REFERENCES `operador` (`id_operador`)
) ENGINE = InnoDB;
