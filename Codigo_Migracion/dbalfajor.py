import pyodbc
from faker import Faker
import random

fake= Faker('es_CO')

conn_str= (
    r"DRIVER={SQL SERVER};"
    r"SERVER=DESKTOP-7AESIHS\SQLEXPRESS;"
    r"DATABASE=AlfajoresDB;"
    r"Trusted_Connection=yes;"
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("Conexión exitosa a SQL Server.")
except Exception as e:
    print("Error de conexión:", e)
    exit()


sabores_lista = [
    'Limón', 'Maracuyá', 'Lulada', 'Mango', 'Red Velvet', 
    'Oreo', 'Milo', 'Brownie', 'Snickers', 'Chocolatoso', 'Dulce de leche'
]
"""
for sabor in sabores_lista:
    cursor.execute(
        "INSERT INTO Sabores (nombre_sabor) VALUES (?)",
        sabor
    )
conn.commit()
print("1. Sabores insertados correctamente.")
"""


"""
categorias = [
    ('Pequeño', 35),
    ('Grande', 60)
]

for nombre, descripcion_gramos in categorias:
    cursor.execute(
        "INSERT INTO Categorias_Tamano (nombre_tamano, descripcion_gramos) VALUES (?, ?)",
        nombre, descripcion_gramos
    )
conn.commit()
print("2. Categorías de tamaño insertadas.")
"""
"""
# OBTENER IDs DE CATEGORÍAS Y SABORES
cursor.execute("SELECT id_categoria, nombre_tamano FROM Categorias_Tamano")
cat_dict = {row[1]: row[0] for row in cursor.fetchall()}

cursor.execute("SELECT id_sabor, nombre_sabor FROM Sabores")
Sabores_db = cursor.fetchall()
"""
"""
for id_sabor, nombre_sabor in Sabores_db:
    # Versión Pequeña
    cursor.execute(
        "INSERT INTO Producto (id_categoria, id_sabor, precio) VALUES (?, ?, ?)",
        cat_dict['Pequeño'], id_sabor, 5000.00
    )
    # Versión Grande
    cursor.execute(
        "INSERT INTO Producto (id_categoria, id_sabor, precio) VALUES (?, ?, ?)",
        cat_dict['Grande'], id_sabor, 6500.00
    )
conn.commit()
print("3. Productos insertados (2 por sabor: Grande y Pequeño).")
"""

cursor.execute("SELECT id_producto FROM Producto")
productos_ids = [row[0] for row in cursor.fetchall()]
"""
for id_prod in productos_ids:
    cursor.execute(
        "INSERT INTO Inventario (id_producto, stock_disponible) VALUES (?, ?)",
        id_prod, random.randint(50, 500)
    )
conn.commit()
print("4. Inventario inicial creado.")
"""

"""
cursor.execute("INSERT INTO Tipos_Entrega (nombre_modalidad) VALUES ('Envío Nacional')")
cursor.execute("INSERT INTO Tipos_Entrega (nombre_modalidad) VALUES ('Recogida en Tienda')")
conn.commit()
"""
cursor.execute("SELECT id_tipo_entrega, nombre_modalidad FROM Tipos_Entrega")
tipos_entrega_dict = {row[1]: row[0] for row in cursor.fetchall()}
print("5. Tipos de entrega insertados.")

"""
clientes_ids = []
for _ in range(500):
    nombre = fake.name()
    email = fake.unique.email()
    telefono = fake.phone_number()
    direccion = fake.address().replace('\n', ', ')
    
    cursor.execute(
        "INSERT INTO Clientes (nombre, email, telefono, direccion_defecto) VALUES (?, ?, ?, ?)",
        nombre, email, telefono, direccion
    )
conn.commit()
"""
cursor.execute("SELECT id_cliente FROM Clientes")
clientes_ids = [row[0] for row in cursor.fetchall()]
print("6. 500 clientes insertados.")



cursor.execute("SELECT id_producto, precio FROM Producto")
precios_productos = {row[0]: float(row[1]) for row in cursor.fetchall()}

empresas_transporte = ['Servientrega', 'Interrapidísimo', 'Coordinadora', 'Envia']
metodos_pago = ['Nequi', 'Daviplata', 'Bancolombia', 'Tarjeta de Crédito', 'Efectivo']
estados_pedido = ['Entregado', 'Enviado', 'En preparación', 'Pendiente']

print("Generando 1.800 pedidos con sus detalles, envíos y pagos...")

for _ in range(1800):
    id_cliente = random.choice(clientes_ids)
    es_envio_nacional = random.random() < 0.6
    id_tipo_entrega = tipos_entrega_dict['Envío Nacional'] if es_envio_nacional else tipos_entrega_dict['Recogida en Tienda']
    
    fecha_pedido = fake.date_time_between(start_date='-1y', end_date='now')
    estado = random.choice(estados_pedido)
    
    
    cursor.execute(
        "INSERT INTO Pedidos (id_cliente, id_tipo_entrega, fecha_pedido, estado_pedido, monto_total) VALUES (?, ?, ?, ?, 0)",
        id_cliente, id_tipo_entrega, fecha_pedido, estado
    )
    cursor.execute("SELECT @@IDENTITY")
    id_pedido = int(cursor.fetchone()[0])
    
    # Generar de 1 a 4 detalles por pedido
    cant_items = random.randint(1, 11)
    productos_seleccionados = random.sample(productos_ids, cant_items)
    monto_total_pedido = 0
    
    for id_prod in productos_seleccionados:
        cantidad = random.randint(1, 12) # Unidades
        precio_unitario = precios_productos[id_prod]
        subtotal = cantidad * precio_unitario
        monto_total_pedido += subtotal
        
        cursor.execute(
            "INSERT INTO Detalle_Pedidos (id_pedido, id_producto, cantidad, precio_unitario) VALUES (?, ?, ?, ?)",
            id_pedido, id_prod, cantidad, precio_unitario
        )
    
    # Sumar costo de envío si aplica
    costo_envio = 12000.00 if es_envio_nacional else 0.00
    monto_total_pedido += costo_envio
    
    # Actualizar el monto total del pedido
    cursor.execute("UPDATE Pedidos SET monto_total = ? WHERE id_pedido = ?", monto_total_pedido, id_pedido)
    
    # 9. Inserción de Envío Nacional (solo si aplica)
    if es_envio_nacional:
        cursor.execute("SELECT direccion_defecto FROM Clientes WHERE id_cliente = ?", id_cliente)
        direccion_cliente = cursor.fetchone()[0]
        cursor.execute(
            "INSERT INTO Envios_Nacionales (id_pedido, empresa_transporte, numero_guia, direccion_destino, costo_envio) VALUES (?, ?, ?, ?, ?)",
            id_pedido,
            random.choice(empresas_transporte),
            str(fake.random_number(digits=10)),
            direccion_cliente,
            costo_envio
        )
        
    # 10. Inserción del Pago
    cursor.execute(
        "INSERT INTO Pagos (id_pedido, metodo_pago, monto_pagado, fecha_pago, estado_pago) VALUES (?, ?, ?, ?, 'Aprobado')",
        id_pedido, random.choice(metodos_pago), monto_total_pedido, fecha_pedido
    )

conn.commit()
print("7-10. Pedidos, detalles, envíos y pagos insertados exitosamente.")
print("\n¡Poblado completo de la base de datos finalizado!")
cursor.close()
conn.close()













