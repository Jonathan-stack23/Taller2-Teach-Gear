import os
import sys

# Asegura que Python encuentre database.py y schemas.py
# sin importar desde que directorio se ejecute uvicorn (necesario en Render)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from database import test_conexion, productos_collection, pedidos_collection
from schemas import (
    ProductoCreate,
    ProductoUpdate,
    ProductoInDB,
    PedidoCreate,
    PedidoUpdate,
    PedidoInDB,
    ItemPedido,
)

load_dotenv()


def _producto_serialize(producto) -> dict:
    return {
        "_id": str(producto["_id"]),
        "nombre": producto.get("nombre", ""),
        "descripcion": producto.get("descripcion", ""),
        "categoria": producto.get("categoria", ""),
        "precio": producto.get("precio", 0.0),
        "stock": producto.get("stock", 0),
        "marca": producto.get("marca"),
        "imagen_url": producto.get("imagen_url"),
        "activo": producto.get("activo", True),
        "fecha_creacion": producto.get("fecha_creacion", datetime.utcnow()),
        "fecha_actualizacion": producto.get("fecha_actualizacion", datetime.utcnow()),
    }


def _pedido_serialize(pedido) -> dict:
    items = []
    for item in pedido.get("items", []):
        items.append({
            "producto_id": str(item.get("producto_id")),
            "cantidad": item.get("cantidad", 0),
            "precio_unitario": item.get("precio_unitario", 0.0),
        })
    return {
        "_id": str(pedido["_id"]),
        "cliente_nombre": pedido.get("cliente_nombre", ""),
        "cliente_email": pedido.get("cliente_email", ""),
        "cliente_telefono": pedido.get("cliente_telefono"),
        "direccion_envio": pedido.get("direccion_envio", ""),
        "items": items,
        "notas": pedido.get("notas"),
        "total": pedido.get("total", 0.0),
        "estado": pedido.get("estado", "pendiente"),
        "fecha_creacion": pedido.get("fecha_creacion", datetime.utcnow()),
        "fecha_actualizacion": pedido.get("fecha_actualizacion", datetime.utcnow()),
        "notas_internas": pedido.get("notas_internas"),
    }


app = FastAPI(
    title="TechGear API - Sistema de Catálogo y Pedidos",
    description="API RESTful de alto rendimiento para la gestión de productos y pedidos de TechGear. "
                "Construida con FastAPI, Pydantic y MongoDB Atlas.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

test_conexion()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Estado"])
def root():
    return {
        "nombre": "TechGear API",
        "version": "1.0.0",
        "estado": "operativo",
        "documentacion": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Estado"])
def health_check():
    db_ok = test_conexion()
    return {
        "estado": "saludable" if db_ok else "error",
        "base_de_datos": "conectada" if db_ok else "desconectada",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/productos", response_model=List[ProductoInDB], tags=["Productos"])
def listar_productos(
    categoria: Optional[str] = Query(None, description="Filtrar por categoría"),
    activo: Optional[bool] = Query(None, description="Filtrar solo productos activos"),
    limit: int = Query(100, ge=1, le=500, description="Cantidad máxima de resultados"),
    skip: int = Query(0, ge=0, description="Número de resultados a saltar"),
):
    filtro = {}
    if categoria:
        filtro["categoria"] = categoria
    if activo is not None:
        filtro["activo"] = activo

    cursor = productos_collection.find(filtro).skip(skip).limit(limit).sort("fecha_creacion", -1)
    productos = list(cursor)
    return [ProductoInDB(**_producto_serialize(p)) for p in productos]


@app.get("/productos/{producto_id}", response_model=ProductoInDB, tags=["Productos"])
def obtener_producto(producto_id: str):
    try:
        obj_id = ObjectId(producto_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de producto inválido")

    producto = productos_collection.find_one({"_id": obj_id})
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return ProductoInDB(**_producto_serialize(producto))


@app.post("/productos", response_model=ProductoInDB, status_code=status.HTTP_201_CREATED, tags=["Productos"])
def crear_producto(producto: ProductoCreate):
    nuevo = producto.model_dump()
    ahora = datetime.utcnow()
    nuevo["fecha_creacion"] = ahora
    nuevo["fecha_actualizacion"] = ahora

    resultado = productos_collection.insert_one(nuevo)
    creado = productos_collection.find_one({"_id": resultado.inserted_id})
    return ProductoInDB(**_producto_serialize(creado))


@app.put("/productos/{producto_id}", response_model=ProductoInDB, tags=["Productos"])
def actualizar_producto(producto_id: str, data: ProductoUpdate):
    try:
        obj_id = ObjectId(producto_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de producto inválido")

    actualizaciones = {k: v for k, v in data.model_dump(exclude_unset=True).items()}
    if not actualizaciones:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
    actualizaciones["fecha_actualizacion"] = datetime.utcnow()

    resultado = productos_collection.update_one(
        {"_id": obj_id}, {"$set": actualizaciones}
    )
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    actualizado = productos_collection.find_one({"_id": obj_id})
    return ProductoInDB(**_producto_serialize(actualizado))


@app.delete("/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Productos"])
def eliminar_producto(producto_id: str):
    try:
        obj_id = ObjectId(producto_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de producto inválido")

    resultado = productos_collection.delete_one({"_id": obj_id})
    if resultado.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return None


@app.get("/pedidos", response_model=List[PedidoInDB], tags=["Pedidos"])
def listar_pedidos(
    estado: Optional[str] = Query(None, description="Filtrar por estado del pedido"),
    cliente_email: Optional[str] = Query(None, description="Filtrar por email del cliente"),
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0),
):
    filtro = {}
    if estado:
        filtro["estado"] = estado
    if cliente_email:
        filtro["cliente_email"] = cliente_email

    cursor = pedidos_collection.find(filtro).skip(skip).limit(limit).sort("fecha_creacion", -1)
    pedidos = list(cursor)
    return [PedidoInDB(**_pedido_serialize(p)) for p in pedidos]


@app.get("/pedidos/{pedido_id}", response_model=PedidoInDB, tags=["Pedidos"])
def obtener_pedido(pedido_id: str):
    try:
        obj_id = ObjectId(pedido_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de pedido inválido")

    pedido = pedidos_collection.find_one({"_id": obj_id})
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return PedidoInDB(**_pedido_serialize(pedido))


@app.post("/pedidos", response_model=PedidoInDB, status_code=status.HTTP_201_CREATED, tags=["Pedidos"])
def crear_pedido(pedido: PedidoCreate):
    datos = pedido.model_dump()
    items_procesados = []
    total = 0.0

    for item in datos["items"]:
        try:
            prod_id = ObjectId(item["producto_id"])
        except (InvalidId, KeyError):
            raise HTTPException(status_code=400, detail=f"ID de producto inválido en el pedido")

        producto = productos_collection.find_one({"_id": prod_id})
        if not producto:
            raise HTTPException(
                status_code=404,
                detail=f"Producto con ID {item['producto_id']} no encontrado"
            )
        if not producto.get("activo", True):
            raise HTTPException(
                status_code=400,
                detail=f"Producto '{producto.get('nombre')}' no está disponible"
            )
        if producto.get("stock", 0) < item["cantidad"]:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para '{producto.get('nombre')}'. "
                       f"Disponible: {producto.get('stock', 0)}, solicitado: {item['cantidad']}"
            )

        precio_unit = producto["precio"]
        subtotal = precio_unit * item["cantidad"]
        total += subtotal
        items_procesados.append({
            "producto_id": prod_id,
            "cantidad": item["cantidad"],
            "precio_unitario": precio_unit,
        })

        nuevo_stock = producto["stock"] - item["cantidad"]
        productos_collection.update_one(
            {"_id": prod_id},
            {"$set": {"stock": nuevo_stock, "fecha_actualizacion": datetime.utcnow()}}
        )

    ahora = datetime.utcnow()
    nuevo_pedido = {
        "cliente_nombre": datos["cliente_nombre"],
        "cliente_email": datos["cliente_email"],
        "cliente_telefono": datos.get("cliente_telefono"),
        "direccion_envio": datos["direccion_envio"],
        "items": items_procesados,
        "notas": datos.get("notas"),
        "total": round(total, 2),
        "estado": "pendiente",
        "fecha_creacion": ahora,
        "fecha_actualizacion": ahora,
        "notas_internas": None,
    }

    resultado = pedidos_collection.insert_one(nuevo_pedido)
    creado = pedidos_collection.find_one({"_id": resultado.inserted_id})
    return PedidoInDB(**_pedido_serialize(creado))


@app.patch("/pedidos/{pedido_id}", response_model=PedidoInDB, tags=["Pedidos"])
def actualizar_estado_pedido(pedido_id: str, data: PedidoUpdate):
    try:
        obj_id = ObjectId(pedido_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="ID de pedido inválido")

    actualizaciones = {k: v for k, v in data.model_dump(exclude_unset=True).items()}
    if not actualizaciones:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")

    estados_validos = {"pendiente", "procesando", "enviado", "entregado", "cancelado"}
    if "estado" in actualizaciones and actualizaciones["estado"] not in estados_validos:
        raise HTTPException(
            status_code=400,
            detail=f"Estado inválido. Válidos: {', '.join(sorted(estados_validos))}"
        )

    actualizaciones["fecha_actualizacion"] = datetime.utcnow()

    resultado = pedidos_collection.update_one(
        {"_id": obj_id}, {"$set": actualizaciones}
    )
    if resultado.matched_count == 0:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    actualizado = pedidos_collection.find_one({"_id": obj_id})
    return PedidoInDB(**_pedido_serialize(actualizado))
