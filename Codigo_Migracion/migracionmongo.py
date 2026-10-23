import pyodbc
from pymongo import MongoClient

# 1. Conexiones
conn_sql = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=DESKTOP-7AESIHS\SQLEXPRESS;'
    'DATABASE=AlfajoresDB;'
    'Trusted_Connection=yes;'
)
cursor = conn_sql.cursor()

client_mongo = MongoClient("mongodb://localhost:27017/")
db_mongo = client_mongo["AlfajoresMongoDB"]

print("Conexiones establecidas con éxito.")

print("Migrando Clientes...")
cursor.execute("SELECT id_cliente, nombre, email, telefono, direccion_defecto FROM Clientes")
clientes_sql = cursor.fetchall()

coleccion_clientes = db_mongo["clientes"]
coleccion_clientes.delete_many({}) # Limpiar colección destino

mapa_clientes_ids = {} # Para mapear id_cliente de SQL a ObjectId de MongoDB

for row in clientes_sql:
    partes = row.direccion_defecto.split(",") if row.direccion_defecto else []
    if len(partes) == 5:
        direccion = partes[0].strip()
        apartamento = partes[1].strip()
        cod_postal = partes[2].strip()
        ciudad = partes[3].strip()
        departamento = partes[4].strip()
    elif len(partes) == 4:
        direccion = partes[0].strip()
        apartamento = "no aplica"
        cod_postal = partes[1].strip()
        ciudad = partes[2].strip()
        departamento = partes[3].strip()
    else:
        # Caso 3: Datos incompletos o vacíos
        direccion = partes[0].strip() if len(partes) > 0 else "Sin dirección"
        apartamento = "no aplica"
        cod_postal = "sin cod_postal"
        ciudad = "Sin ciudad"
        departamento = "Sin departamento"

    doc_cliente = {
        "sql_id_cliente": row.id_cliente,
        "nombre": row.nombre,
        "email": row.email,
        "telefono": row.telefono,
        "ubicacion_defecto": {
            "direccion": direccion,
            "apartamento":apartamento,
            "cod_postal": cod_postal,
            "ciudad": ciudad,
            "departamento": departamento
        }
    }
    result = coleccion_clientes.insert_one(doc_cliente)
    
    mapa_clientes_ids[row.id_cliente] = result.inserted_id

print(f"-> {len(mapa_clientes_ids)} Clientes migrados.")

print("Migrando Productos (Embebiendo Sabor, Tamaño e Inventario)...")
query_producto = """
    SELECT 
        p.id_producto,
        s.nombre_sabor,
        ct.nombre_tamano,
        p.precio,
        i.stock_disponible
    FROM Producto p
    INNER JOIN Sabores s ON p.id_sabor = s.id_sabor
    INNER JOIN Categorias_Tamano ct ON p.id_categoria = ct.id_categoria
    LEFT JOIN Inventario i ON p.id_producto = i.id_producto
"""
cursor.execute(query_producto)
producto_sql = cursor.fetchall()

coleccion_productos = db_mongo["productos"]
coleccion_productos.delete_many({})

for row in producto_sql:
    doc_producto = {
        "sql_id_producto": row.id_producto,
        "sabor": row.nombre_sabor,
        "categoria": row.nombre_tamano,
        "precio_unitario": float(row.precio),
        "stock_disponible": row.stock_disponible if row.stock_disponible else 0
    }
    coleccion_productos.insert_one(doc_producto)

print(f"-> {len(producto_sql)} Productos migrados.")

# ==========================================
# PASO 3: MIGRAR PEDIDOS (CON EMBEDDING COMPLETO)
# ==========================================
print("Migrando Pedidos (Embebiendo Detalle, Envíos y Pagos)...")


cursor.execute("SELECT id_pedido, id_cliente, fecha_pedido, monto_total FROM Pedidos")
pedidos_sql = cursor.fetchall()

coleccion_pedidos = db_mongo["pedidos"]
coleccion_pedidos.delete_many({})

docs_pedidos = []

for ped in pedidos_sql:
    id_ped = ped.id_pedido
    
    
    cursor.execute("""
        SELECT dp.id_producto, s.nombre_sabor, ct.nombre_tamano, dp.cantidad, dp.precio_unitario
        FROM Detalle_Pedidos dp
        INNER JOIN Producto p ON dp.id_producto = p.id_producto
        INNER JOIN Sabores s ON p.id_sabor = s.id_sabor
        INNER JOIN Categorias_Tamano ct ON p.id_categoria = ct.id_categoria
        WHERE dp.id_pedido = ?
    """, id_ped)
    detalles = cursor.fetchall()
    
    items_array = []
    for d in detalles:
        items_array.append({
            "sql_id_producto": d.id_producto,
            "nombre_producto": f"Alfajor {d.nombre_sabor} {d.nombre_tamano}",
            "cantidad": d.cantidad,
            "precio_unitario": float(d.precio_unitario),
            "subtotal": float(d.cantidad * d.precio_unitario)
        })
        
    
    cursor.execute("""
        SELECT empresa_transporte, numero_guia, direccion_destino, costo_envio
        FROM Envios_Nacionales WHERE id_pedido = ?
    """, id_ped)
    env = cursor.fetchone()
    
  
    es_envio_nacional = True if env else False
    info_envio = None
    
    if env:
        partes_envio = env.direccion_destino.split(",") if env.direccion_destino else []
        if len(partes_envio) == 5:
                direccion_destino = partes_envio[0].strip()
                apartamento = partes_envio[1].strip()
                cod_postal = partes_envio[2].strip()
                ciudad = partes_envio[3].strip()
                departamento = partes_envio[4].strip()
        elif len(partes_envio) == 4:
                direccion_destino = partes_envio[0].strip()
                apartamento = "no aplica"
                cod_postal = partes_envio[1].strip()
                ciudad = partes_envio[2].strip()
                departamento = partes_envio[3].strip()
        else:
                direccion_destino = partes_envio[0].strip() if len(partes_envio) > 0 else "Sin dirección"
                apartamento = "no aplica"
                cod_postal = "sin cod_postal"
                ciudad = "Sin ciudad"
                departamento = "Sin departamento"
        
        info_envio = {
            "empresa_transporte": env.empresa_transporte,
            "numero_guia": env.numero_guia,
            "direccion_destino":direccion_destino,
            "apartamento":apartamento,
            "cod_postal":cod_postal,
            "ciudad": ciudad,
            "departamento": departamento,
            "costo_envio": float(env.costo_envio)
        }
            
    # --- C. Consultar datos de Pago ---
    cursor.execute("SELECT metodo_pago, estado_pago, fecha_pago FROM Pagos WHERE id_pedido = ?", id_ped)
    pago_row = cursor.fetchone()
    info_pago = None
    if pago_row:
        info_pago = {
            "metodo_pago": pago_row.metodo_pago,
            "estado_pago": pago_row.estado_pago,
            "fecha_pago": pago_row.fecha_pago
        }

    doc_pedido = {
        "sql_id_pedido": id_ped,
        "cliente_id": mapa_clientes_ids.get(ped.id_cliente), # Referencia al _id de MongoDB
        "fecha_pedido": ped.fecha_pedido,
        "es_envio_nacional": es_envio_nacional,
        "monto_total": float(ped.monto_total),
        "items": items_array,
        "envio": info_envio,
        "pago": info_pago
    }
    docs_pedidos.append(doc_pedido)

# Inserción masiva
if docs_pedidos:
    coleccion_pedidos.insert_many(docs_pedidos)

print(f"-> {len(docs_pedidos)} Pedidos migrados correctamente.")