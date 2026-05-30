import mysql.connector
from mysql.connector import Error
from getpass import getpass
from faker import Faker
import random
import logging
from datetime import datetime, timedelta

# Configuración del logger: guarda los registros en 'seed_log.txt' y los muestra en consola.
logging.basicConfig(
    filename='seed_log.txt',
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Inicialización de Faker para la generación de datos ficticios pero realistas.
fake = Faker()


def escribir_log(mensaje, nivel="info"):
    """
    Clasifica y registra los mensajes tanto en el archivo de log como en la consola.

    Args:
        mensaje (str): El texto o notificación que se desea registrar.
        nivel (str, optional): El nivel de severidad del log ("info" o "error"). 
        Por defecto es "info".
    """
    if nivel == "info":
        logging.info(mensaje)
    else:
        logging.error(mensaje)
    print(mensaje)


def conectar_bd():
    """
    Establece una conexión con la base de datos MySQL 'hermes_it_db'.

    Returns:
        mysql: El objeto de conexión si 
        fuesen exitosas las credenciales, o None si ocurre un error.
    """
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password=getpass('Introduce tu contraseña: '),
            database='hermes_it_db'
        )
        if conexion.is_connected():
            escribir_log("Conexión exitosa al esquema hermes_it_db.")
            return conexion
    except Error as e:
        escribir_log(f"Error al conectar: {e}", "error")
        return None


def generar_datos_base(conexion):
    """
    Inserta los datos iniciales (departamentos, operadores y clientes).

    Crea 4 departamentos fijos, genera 10 operadores vinculados aleatoriamente 
    a estos departamentos y registra 50 clientes con datos ficticios.

    Args:
        conexion (mysql): Conexión activa a la base de datos.

    Returns:
        tuple: Un par de listas conteniendo ([ids_operadores], [ids_clientes]). 
        Si el proceso falla, devuelve dos listas vacías ([], []).
    """
    cursor = conexion.cursor()
    ids_operadores = []
    ids_clientes = []
    
    try:
        # 1. Inserción de departamentos predefinidos
        depts_data = [
            ('Soporte nivel 1', 'Planta Baja'), ('Administracion', 'Oficina A'),
            ('Soporte nivel 2', 'Planta 1'), ('Soporte nivel 3', 'Planta 2')
        ]
        for nom, ubi in depts_data:
            cursor.execute("INSERT INTO departamento (nombre, ubicacion) VALUES (%s, %s)", (nom, ubi))
        
        # Extracción de los IDs generados para los departamentos
        cursor.execute("SELECT id_departamento FROM departamento")
        lista_depts = [fila[0] for fila in cursor.fetchall()]

        # 2. Generación e inserción de 10 técnicos/operadores de soporte
        for _ in range(10):
            nombre = fake.name()
            # Genera un correo único usando el dominio corporativo de la empresa
            correo = fake.unique.email().split('@')[0] + "@hermes-it.com"
            
            cursor.execute(
                "INSERT INTO operador (nombre, correo_corporativo, id_departamento) VALUES (%s, %s, %s)", 
                (nombre, correo, random.choice(lista_depts))
            )
            ids_operadores.append(cursor.lastrowid)

        # 3. Generación e inserción de 50 clientes ficticios
        for _ in range(50):
            # [:20] asegura que el número telefónico no exceda el límite de la columna
            cursor.execute(
                "INSERT INTO cliente (nombre_completo, correo_electronico, telefono) VALUES (%s, %s, %s)", 
                (fake.name(), fake.unique.email(), fake.phone_number()[:20])
            )
            ids_clientes.append(cursor.lastrowid)
        
        # Confirmación de los cambios en la base de datos
        conexion.commit()
        escribir_log(f"Base lista: {len(lista_depts)} Deptos, 10 Operadores, 50 Clientes.")
        return ids_operadores, ids_clientes

    except Error as e:
        escribir_log(f"Error en datos base: {e}", "error")
        return [], []


def generar_tickets_e_historial(conexion, ids_ops, ids_clis):
    """
    Simula la creación de 200 tickets junto con sus mensajes.

    Asigna fechas de creación realistas en un rango de los últimos 2 años. Si el 
    estado del ticket se define como 'Cerrado', calcula automáticamente una fecha 
    de cierre coherente. Además, genera un hilo de chat simulado de entre 1 y 3 
    mensajes por cada ticket.

    Args:
        conexion (mysql): Conexión activa a la base de datos.
        ids_ops (list): Lista de IDs de operadores válidos en el sistema.
        ids_clis (list): Lista de IDs de clientes válidos en el sistema.
    """
    cursor = conexion.cursor()
    prioridades = ['Baja', 'Media', 'Alta', 'Crítica']
    estados = ['Abierto', 'En Proceso', 'Cerrado']   
    
    try:
        # Generación de los 200 tickets individuales
        for _ in range(200):
            f_creacion = fake.date_time_between(start_date='-2y', end_date='now')
            estado = random.choice(estados)
            
            # Si está cerrado, se calcula el cierre sumando entre 1 y 5 días a la creación
            f_cierre = f_creacion + timedelta(days=random.randint(1, 5)) if estado == 'Cerrado' else None
            
            cursor.execute("""INSERT INTO ticket 
                (titulo, descripcion, fecha_creacion, fecha_cierre, categoria, prioridad, estado, id_cliente, id_operador) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (fake.sentence(nb_words=3), fake.text(), f_creacion, f_cierre, 
                 random.choice(['Software', 'Hardware', 'Redes']), random.choice(prioridades), 
                 estado, random.choice(ids_clis), random.choice(ids_ops)))
            
            cod_ticket = cursor.lastrowid

            # Simulación de un chat real: crea entre 1 y 3 mensajes internos por ticket
            for _ in range(random.randint(1, 3)):
                # El mensaje se envía de manera realista entre 1 y 10 horas después de la apertura
                f_envio = f_creacion + timedelta(hours=random.randint(1, 10))
                
                # Determina aleatoriamente si el autor del mensaje es el cliente o el técnico
                es_cliente = random.choice([True, False])
                id_cli_autor = random.choice(ids_clis) if es_cliente else None
                id_ope_autor = random.choice(ids_ops) if not es_cliente else None
                
                cursor.execute("""INSERT INTO mensaje 
                    (cuerpo, fecha_envio, codigo_ticket, id_cliente_autor, id_operador_autor) 
                    VALUES (%s, %s, %s, %s, %s)""",
                    (fake.text(max_nb_chars=150), f_envio, cod_ticket, id_cli_autor, id_ope_autor))
        
        # Confirmación definitiva de todos los tickets y mensajes inyectados
        conexion.commit()
        escribir_log("200 Tickets y mensajes inyectados con éxito.")
        
    except Error as e:
        escribir_log(f"Error en tickets: {e}", "error")


def ejecutar():
    """
    Controla el flujo completo de ejecución del script.

    Se encarga de abrir la conexión, validar la creación de los datos
    e iniciar la simulación del historial.
    """
    escribir_log("Iniciando para Hermes 360...")
    conn = conectar_bd()
    
    if conn:
        # Genera los datos independientes y recupera sus llaves primarias
        ops, clis = generar_datos_base(conn)
        
        # Si la estructura base se generó correctamente, procede con los tickets
        if ops and clis:
            generar_tickets_e_historial(conn, ops, clis)
        
        # Cierre seguro de la conexión con el servidor MySQL
        conn.close()
        escribir_log("Datos completados.")

if __name__ == "__main__":
    ejecutar()
