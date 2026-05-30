import mysql.connector
import random
import getpass

password = getpass.getpass("Introduce la contraseña root de Mysql:")
conexion = mysql.connector.connect(
    host='localhost',
    user='root',
    password= password,
    database = 'hermes_it_db'
)
cursor = conexion.cursor()
cursor.execute("SELECT codigo_ticket, descripcion FROM ticket")
tickets = cursor.fetchall()
palabras_enfado = ['incompetentes', 'denuncia', 'verguenza', 'lento']
for codigo_ticket, descripcion in tickets:
    if descripcion and random.random() <= 0.10:
        palabras = descripcion.split()
        palabras.insert(random.randint(0,len(palabras)), random.choice(palabras_enfado))
        nueva_descripcion = " ".join(palabras)
        cursor.execute("UPDATE ticket SET descripcion = %s WHERE codigo_ticket = %s",
                       (nueva_descripcion, codigo_ticket)
                    )
conexion.commit()
cursor.close()
conexion.close()