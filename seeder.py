
from faker import Faker
from random import randint


fake = Faker()
almacen_ticket = {}

def generar_cliente():

    ids = [randint(1, 100) for _ in range(5)]

    almacen_cliente = {}

    for id in ids:
        almacen_cliente[id] = [fake.name().strip(), fake.email().strip(), fake.text().strip(), fake.date().strip()]

    return almacen_cliente

# print(almacen_cliente)

# print("----------------------------")

# for _ in range(len(almacen_cliente)):
#     id = randint(1, len(almacen_cliente))
#     if id in almacen_cliente:
#         almacen_ticket[id] = almacen_cliente[id]


if "__main__" == __name__:
    datos_cliente = generar_cliente()

    print(datos_cliente)