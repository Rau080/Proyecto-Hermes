import mysql.connector
from mysql.connector import Error
import xml.etree.ElementTree as ET
import os
from datetime import datetime

from getpass import getpass

def exportar_tickets_archivados_xml():
    # 1. Pedir credenciales por consola de forma segura
    nombre_bd = input("Introduce el nombre de la base de datos (ej. hermes_it_db): ")
    password_bd = getpass("Introduce la contraseña del usuario 'root': ")
    
    if not os.path.isdir("archivos"):
        os.makedirs("archivos")
    
    conexion = None

    try:
        # 2. Conexión a la base de datos usando las variables ingresadas
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            database=nombre_bd,
            password=password_bd
        )

        if conexion.is_connected():

            print(f"\nConexión exitosa a la base de datos '{nombre_bd}'.")

            cursor = conexion.cursor()

            # 3. Consultar los tickets archivados
            consulta_tickets = """
                SELECT codigo_ticket, fecha_creacion, fecha_cierre, id_cliente, id_operador
                FROM ticket
                WHERE estado = "Archivado";
            """

            cursor.execute(consulta_tickets)

            registros_tickets = cursor.fetchall()

            if not registros_tickets:
                print("No se encontraron tickets con el estado 'Archivado'.")
                return
            
            for num_archivo, ticket in enumerate(registros_tickets):

                codigo_ticket = ticket[0]
                fecha_creacion = ticket[1]
                fecha_cierre = ticket[2]
                id_cliente = ticket[3]
                id_operador = ticket[4]

                consulta_cliente = """
                    SELECT id_cliente, nombre_completo, correo_electronico, telefono
                    FROM cliente
                    WHERE id_cliente = %s;
                """

                cursor.execute(consulta_cliente, (id_cliente,))

                cliente = cursor.fetchone()

                operador = None

                if id_operador != None:

                    consulta_operador = """
                        SELECT id_operador, nombre, correo_corporativo, id_departamento
                        FROM operador
                        WHERE id_operador = %s;
                    """

                    cursor.execute(consulta_operador, (id_operador,))

                    operador = cursor.fetchone()

                consulta_mensajes = """
                    SELECT id_mensaje, cuerpo, fecha_envio, codigo_ticket, id_cliente_autor, id_operador_autor
                    FROM mensaje
                    WHERE codigo_ticket = %s
                    ORDER BY fecha_envio ASC;
                """

                cursor.execute(consulta_mensajes, (codigo_ticket,))

                mensajes = cursor.fetchall()


                root = ET.Element("archivo", id=f"{num_archivo + 1}")

                datos_clientes = ET.SubElement(
                    root,
                    "datos_clientes",
                    id_cliente=str(cliente[0])
                )

                nombre_completo = ET.SubElement(datos_clientes, "nombre_completo")
                nombre_completo.text = f"{cliente[1]}"

                email = ET.SubElement(datos_clientes, "email")
                email.text = f"{cliente[2]}"

                telefono = ET.SubElement(datos_clientes, "tlf")
                telefono.text = f"{cliente[3]}"

                if operador != None:

                    datos_operador = ET.SubElement(
                        root,
                        "datos_operador",
                        id_operador=f"{operador[0]}",
                        id_dpto=f"{operador[3]}"
                    )

                    nombre_operador = ET.SubElement(datos_operador, "nombre")
                    nombre_operador.text = f"{operador[1]}"

                    email_operador = ET.SubElement(datos_operador, "email")
                    email_operador.text = f"{operador[2]}"

                historial = ET.SubElement(root, "historial")

                lista_palabras = ["incompetentes", "denuncia", "vergüenza", "lento"]

                cliente_enfadado = False

                for num_mensaje, mensaje in enumerate(mensajes):

                    id_mensaje = mensaje[0]
                    cuerpo = mensaje[1]
                    fecha = mensaje[2]

                    if mensaje[4] != None:

                        mensaje_xml = ET.SubElement(historial, "mensaje", num=f"{num_mensaje + 1}", emisor="cliente", id_emisor=f"{mensaje[4]}")

                    else:

                        mensaje_xml = ET.SubElement(historial, "mensaje", num=f"{num_mensaje + 1}", emisor="operador", id_emisor=f"{mensaje[5]}")

                    id_ticket = ET.SubElement(mensaje_xml, "id_ticket")
                    id_ticket.text = f"{mensaje[3]}"

                    cuerpo_mensaje = ET.SubElement(mensaje_xml, "cuerpo_mensaje")
                    cuerpo_mensaje.text = f"{cuerpo}"

                    fecha_formateada = fecha.strftime("%d-%m-%Y %H:%M:%S")

                    fecha_hora_mensaje = ET.SubElement(mensaje_xml, "fecha_envio")
                    fecha_hora_mensaje.text = f"{fecha_formateada}"

                    cuerpo_minusculas = cuerpo.lower()

                    for palabra in lista_palabras:

                        if palabra in cuerpo_minusculas:
                            cliente_enfadado = True
                            break

                if cliente_enfadado:
                    ET.SubElement(root, "cliente_enfadado", respuesta="si")
                else:

                    ET.SubElement(root, "cliente_enfadado", respuesta="no")

                if fecha_cierre != None:
                    diferencia_dias = (fecha_cierre - fecha_creacion).days
                    if diferencia_dias > 7:
                        alerta_sla = ET.SubElement(root, "alerta_sla")
                        alerta_sla.text = (f"El ticket tardó {diferencia_dias} días en cerrarse.")

                tree = ET.ElementTree(root)

                ET.indent(tree, space="     ", level=0)

                tree.write(f"archivos/ticket_{codigo_ticket}.xml", encoding="utf-8", xml_declaration=True)

                print(f"Archivo ticket_{codigo_ticket}.xml generado correctamente.")

    except Error as e:
        print(f"\nError de MySQL: {e}")

    except Exception as e:
        print(f"\nError inesperado: {e}")

    finally:
        if conexion is not None and conexion.is_connected():
            cursor.close()
            conexion.close()
            print("Conexión a la base de datos cerrada.")

# Ejecutar el programa
exportar_tickets_archivados_xml()