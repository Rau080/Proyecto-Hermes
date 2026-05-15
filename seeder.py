import mysql.connector
from mysql.connector import Error
from faker import Faker
import random
import logging
from datetime import datetime, timedelta

logging.basicConfig(
    filename='seed_log.txt',
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
fake = Faker()

def escribir_log(mensaje, nivel="info"):
    if nivel == "info":
        logging.info(mensaje)
    else:
        logging.error(mensaje)
    print(mensaje)
    
def conectar_bd():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Onmula01',
            database='hermes_it_db'
        )
        if conexion.is_connected():
            escribir_log("Conectado a la base de datos.")
            return conexion
    except Error as e:
        escribir_log(f"Error al conectar: {e}", "error")
        return None
    
def generar_datos_base(conexion):
    cursor = conexion.cursor()
    ids_operadores = []
    ids_clientes = []
    try:
        departamentos = [
            ('Soporte nivel 1', 'Planta Baja'), 
            ('Administracion', 'Oficina A'), 
            ('Soporte nivel 2', 'Planta 1'), 
            ('Soporte nivel 3', 'Planta 2')
        ]
        for nombre, ubicacion in departamentos:
            cursor.execute("INSERT INTO departamentos (nombre, ubicacion) VALUES (%s, %s)", 
                           (nombre, ubicacion))
        departamentos = ['IT Support', 'Network', 'Security', 'DevOps']
        for nombre in departamentos:
            cursor.execute("INSERT INTO departamentos (nombre) VALUES (%s)", (nombre,))
        cursor.execute("SELECT id FROM departamentos")
        lista_depts = [fila[0] for fila in cursor.fetchall()]
        for _ in range(10):
            cursor.execute("INSERT INTO operadores (nombre, id_depto) VALUES (%s, %s)", 
                           (fake.name(), random.choice(lista_depts)))
            ids_operadores.append(cursor.lastrowid)
        for _ in range(50):
            cursor.execute("INSERT INTO clientes (nombre, email) VALUES (%s, %s)", 
                           (fake.company(), fake.unique.email()))
            ids_clientes.append(cursor.lastrowid)
        conexion.commit()
        escribir_log("Departamentos, Operadores y Clientes creados.")
        return ids_operadores, ids_clientes
    except Error as e:
        escribir_log(f"Error en datos base: {e}", "error")
        return [], []
    
def generar_tickets_e_historial(conexion, ids_ops, ids_clis):
    cursor = conexion.cursor()
    try:
        for _ in range(200):
            fecha_inicio = fake.date_time_between(start_date='-2y', end_date='now')
            estado_tkt = random.choice(['Open', 'In Progress', 'Closed'])
            fecha_fin = None
            if estado_tkt == 'Closed':
                fecha_fin = fecha_inicio + timedelta(days=random.randint(1, 5))
            cursor.execute("""INSERT INTO tickets 
                (id_cliente, id_operador, asunto, estado, prioridad, fecha_creacion, fecha_cierre) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (random.choice(ids_clis), random.choice(ids_ops), fake.sentence(nb_words=3), 
                 estado_tkt, random.choice(['Low', 'Medium', 'High']), fecha_inicio, fecha_fin))
            nuevo_ticket_id = cursor.lastrowid
            for _ in range(random.randint(1, 3)):
                fecha_msj = fecha_inicio + timedelta(hours=random.randint(1, 10))
                cursor.execute("INSERT INTO historial (id_ticket, emisor, mensaje, fecha) VALUES (%s, %s, %s, %s)",
                               (nuevo_ticket_id, random.choice(['Client', 'Staff']), fake.text(max_nb_chars=100), fecha_msj))
        conexion.commit()
        escribir_log("200 Tickets y sus mensajes creados.")
    except Error as e:
        escribir_log(f"Error en tickets: {e}", "error")

def ejecutar_todo():
    escribir_log("Comenzando el proceso...")
    conn = conectar_bd()
    if conn:
        lista_ops, lista_clis = generar_datos_base(conn)
        if lista_ops and lista_clis:
            generar_tickets_e_historial(conn, lista_ops, lista_clis)
        conn.close()
        escribir_log("Proceso terminado.")

if __name__ == "__main__":
    ejecutar_todo()