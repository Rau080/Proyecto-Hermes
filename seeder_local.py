import mysql.connector
from mysql.connector import Error
from faker import Faker
import random
import logging
from datetime import datetime, timedelta
# Creamos el archivo llamado seed_log.txt donde se guardar los registros que hace el script. Tambien nos sirve saber si falla algo en la base de datos
logging.basicConfig(
    filename='seed_log.txt',
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
# Iniciamos Faker para generar nombres, correos y textos falsos pero realistas
fake = Faker()
# funcion para que actue de controlador de notificaciones, para que cuando el programa se conecte a la base de datos o de error al realizar algo, esta funcion la muestra en pantalla y a la vez la clasifica y lo manda al archivo see_log.txt
def escribir_log(mensaje, nivel="info"):
    if nivel == "info":
        logging.info(mensaje)
    else:
        logging.error(mensaje)
    print(mensaje)
# Conexión a la base de datos 
def conectar_bd():
    try:
        conexion = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Onmula01',
            database='hermes_it_db'
        )
        if conexion.is_connected():
            escribir_log("Conexión exitosa al esquema hermes_it_db.")
            return conexion
    except Error as e:
        escribir_log(f"Error al conectar: {e}", "error")
        return None
def generar_datos_base(conexion):
#Activa el cursor, que nos permite enviar y ejecutar comandos SQL en la base de datos y crea 2 listas vacías ids_operadores y ids_clientes
    cursor = conexion.cursor()
    ids_operadores = []
    ids_clientes = []
    try:
# Con una lista creada dept_data donde esta nombre del departamento y ubicacion. Con el bucle for, recorre la lista y la inserta en la tabla departamento
        depts_data = [
            ('Soporte nivel 1', 'Planta Baja'), ('Administracion', 'Oficina A'),
            ('Soporte nivel 2', 'Planta 1'), ('Soporte nivel 3', 'Planta 2')
        ]
        for nom, ubi in depts_data:
            cursor.execute("INSERT INTO departamento (nombre, ubicacion) VALUES (%s, %s)", (nom, ubi))
# Usando un select extraemos el id generados y los guardamos en una lista llamada lista_depts
        cursor.execute("SELECT id_departamento FROM departamento")
        lista_depts = [fila[0] for fila in cursor.fetchall()]
# Arranca un bucle de 10 ténicos de soporte 
        for _ in range(10):
# Creamos un nombre completo falso
            nombre = fake.name()
# Generamos un correo falso y paramos antes de llegar al @ y le añadimos el dominio de la empresa que es @hermes-it.com
            correo = fake.unique.email().split('@')[0] + "@hermes-it.com"
# Le asignamos un departamento al azar de las listas id que guardamos en la lista lista_depts usando el random.choice
            cursor.execute("INSERT INTO operador (nombre, correo_corporativo, id_departamento) VALUES (%s, %s, %s)", 
                           (nombre, correo, random.choice(lista_depts)))
            ids_operadores.append(cursor.lastrowid)
# Repite el proceso anterios pero en la tabla cliente, crea 50 registros con nombres, correos unicos y telefonos inventados por faker. gracias a [:20] nos aseguramos que el numero de telefono no supere el limites de caracteres permitodo por la columna en la base de datos y cada id generado se guarda en la lista ids_cliente.      
        for _ in range(50):
            cursor.execute("INSERT INTO cliente (nombre_completo, correo_electronico, telefono) VALUES (%s, %s, %s)", 
                           (fake.name(), fake.unique.email(), fake.phone_number()[:20]))
            ids_clientes.append(cursor.lastrowid)
# Usando el commit le da la orden final a mysql de guardar los registros creados y llama los logs para avisar en consola que el proceso termino con exito     
        conexion.commit()
        escribir_log(f"Base lista: {len(lista_depts)} Deptos, 10 Operadores, 50 Clientes.")
        return ids_operadores, ids_clientes
# Si falla cualquier paso anterior, el programa no se detiene si no que salta directamente aquí, regista el fallo exacto de mysql en el archivo see_log.txt 
    except Error as e:
        escribir_log(f"Error en datos base: {e}", "error")
        return [], []
def generar_tickets_e_historial(conexion, ids_ops, ids_clis):
# Abrimos de nuevo el cursor y definomos las listas con las opciones de prioridad y estado que maneja el sistema
    cursor = conexion.cursor()
    prioridades = ['Baja', 'Media', 'Alta', 'Crítica']
    estados = ['Abierto', 'En Proceso', 'Cerrado']   
    try:
# Creamos 200 tickets individuales
        for _ in range(200):
# Le inventamos una fecha de creación realista comprendida entre los ultimos 2 años y el dia de hoy
            f_creacion = fake.date_time_between(start_date='-2y', end_date='now')
# Si el estado se pone en cerrado le calculamos una fecha de cierre sumandole entre 1 y 5 dias a la fecha de creacion. si sigue abierto se queda vacio como None
            estado = random.choice(estados)
            f_cierre = f_creacion + timedelta(days=random.randint(1, 5)) if estado == 'Cerrado' else None
# Insertamos el ticket vinculando de forma aleatoria un id de nuestra lista de clientes y otro de la lista de operadores
            cursor.execute("""INSERT INTO ticket 
                (titulo, descripcion, fecha_creacion, fecha_cierre, categoria, prioridad, estado, id_cliente, id_operador) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (fake.sentence(nb_words=3), fake.text(), f_creacion, f_cierre, 
                 random.choice(['Software', 'Hardware', 'Redes']), random.choice(prioridades), 
                 estado, random.choice(ids_clis), random.choice(ids_ops)))
            cod_ticket = cursor.lastrowid
# Iniciamos un bucle para crear entre 1 y 3 mensajes dentro de este mismo ticket para simular un chat real    
            for _ in range(random.randint(1, 3)):
# Control del tiempo: el mensaje se envia entre 1 y 10 horas despues de haberse abierto el ticket original
                f_envio = f_creacion + timedelta(hours=random.randint(1, 10))
# Aqui hacemos que se ponga aleatoriamente para ver quien responde el chat
                es_cliente = random.choice([True, False])
# Si es el cliente, asignamos su id a la columna autor_cliente y la del tecnico queda vacía o viceversa
                id_cli_autor = random.choice(ids_clis) if es_cliente else None
                id_ope_autor = random.choice(ids_ops) if not es_cliente else None
# Insertamos el mensaje arrastrando el código del ticket al que pertenece     
                cursor.execute("""INSERT INTO mensaje 
                    (cuerpo, fecha_envio, codigo_ticket, id_cliente_autor, id_operador_autor) 
                    VALUES (%s, %s, %s, %s, %s)""",
                    (fake.text(max_nb_chars=150), f_envio, cod_ticket, id_cli_autor, id_ope_autor))
# Despues de haber creado los 200 tickets confirmamos los cambios definitivos  
        conexion.commit()
        escribir_log("200 Tickets y mensajes inyectados con éxito.")
    except Error as e:
# Captura cualquier problema de insercion y lo apunta en el log con la etiqueta de error 
        escribir_log(f"Error en tickets: {e}", "error")
def ejecutar():
# Arranca el flujo del script informando en consola
    escribir_log("Iniciando para Hermes 360...")
    conn = conectar_bd()
# Si la conexion se estableció correctamente, seguimos con el siguiente paso
    if conn:
# Cremos datos maestros independientes y recolectamos sus llaves maestras
        ops, clis = generar_datos_base(conn)
# Si las listas contienen id validos, llamamos a la función encargada de simular las transacciones
        if ops and clis:
            generar_tickets_e_historial(conn, ops, clis)
# Cerramos la conexion con el servidor MySQL
        conn.close()
        escribir_log("Datos completados.")
# Con esto nos aseguramos que el script solo empieza a ejecutarse si se abre este archivo directamente
if __name__ == "__main__":
    ejecutar()