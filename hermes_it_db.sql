
-- -----------------------------------------------------
-- Schema hermes_it_db
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `hermes_it_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `hermes_it_db` ;

-- -----------------------------------------------------
-- Tabla cliente
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hermes_it_db`.`cliente` (
  `id_cliente` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `nombre_completo` VARCHAR(150) NOT NULL,
  `correo_electronico` VARCHAR(150) NOT NULL,
  `telefono` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`id_cliente`),
  UNIQUE INDEX `correo_UNIQUE` (`correo_electronico` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Tabla departamento
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hermes_it_db`.`departamento` (
  `id_departamento` INT NOT NULL,
  `nombre` VARCHAR(100) NOT NULL,
  `ubicacion` VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id_departamento`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Tabla ticket
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hermes_it_db`.`ticket` (
  `codigo_ticket` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `titulo` VARCHAR(200) NOT NULL,
  `descripcion` TEXT NOT NULL,
  `fecha_creacion` DATETIME NOT NULL,
  `fecha_cierre` DATETIME NOT NULL,
  `categoria` VARCHAR(100) NOT NULL,
  `prioridad` ENUM('Baja', 'Media', 'Alta', 'Crítica') NOT NULL,
  `estado` ENUM('Abierto', 'En Proceso', 'Cerrado', 'Archivado') NOT NULL DEFAULT 'Abierto',
  `id_cliente` INT NOT NULL,
  PRIMARY KEY (`codigo_ticket`),
  INDEX `fk_ticket_cliente` (`id_cliente` ASC) VISIBLE,
  CONSTRAINT `fk_ticket_cliente`
    FOREIGN KEY (`id_cliente`)
    REFERENCES `hermes_it_db`.`cliente` (`id_cliente`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Tabla operador
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hermes_it_db`.`operador` (
  `id_operador` INT NOT NULL,
  `nombre` VARCHAR(150) NOT NULL,
  `correo_corporativo` VARCHAR(150) NOT NULL,
  `id_ticket` INT NOT NULL,
  `id_departamento` INT NOT NULL,
  PRIMARY KEY (`id_operador`),
  INDEX `id_ticket_idx` (`id_ticket` ASC) VISIBLE,
  INDEX `fk_id_deaprtamento_idx` (`id_departamento` ASC) VISIBLE,
  CONSTRAINT `id_ticket`
    FOREIGN KEY (`id_ticket`)
    REFERENCES `hermes_it_db`.`ticket` (`id_cliente`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_id_deaprtamento`
    FOREIGN KEY (`id_departamento`)
    REFERENCES `hermes_it_db`.`departamento` (`id_departamento`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Tabla mensaje
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `hermes_it_db`.`mensaje` (
  `id_mensaje` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `cuerpo` TEXT NOT NULL,
  `fecha_envio` DATETIME NOT NULL,
  `codigo_ticket` INT UNSIGNED NOT NULL,
  `id_cliente_autor` INT UNSIGNED NOT NULL,
  `id_operador_autor` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`id_mensaje`),
  INDEX `fk_mensaje_ticket` (`codigo_ticket` ASC) VISIBLE,
  INDEX `fk_mensaje_cliente` (`id_cliente_autor` ASC) VISIBLE,
  CONSTRAINT `fk_mensaje_cliente`
    FOREIGN KEY (`id_cliente_autor`)
    REFERENCES `hermes_it_db`.`cliente` (`id_cliente`),
  CONSTRAINT `fk_mensaje_ticket`
    FOREIGN KEY (`codigo_ticket`)
    REFERENCES `hermes_it_db`.`ticket` (`codigo_ticket`),
  CONSTRAINT `fk_id_operador`
    FOREIGN KEY ()
    REFERENCES `hermes_it_db`.`operador` ()
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


