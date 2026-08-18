from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


def _gridfs_validator(cls, v):
    return v


class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre del producto")
    descripcion: str = Field(..., min_length=5, description="Descripción detallada del producto")
    categoria: str = Field(..., min_length=2, max_length=50, description="Categoría del producto")
    precio: float = Field(..., gt=0, description="Precio unitario en USD")
    stock: int = Field(..., ge=0, description="Cantidad disponible en inventario")
    marca: Optional[str] = Field(None, max_length=50, description="Marca del producto")
    imagen_url: Optional[str] = Field(None, description="URL de la imagen del producto")
    activo: bool = Field(True, description="Indica si el producto está disponible para la venta")


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    descripcion: Optional[str] = Field(None, min_length=5)
    categoria: Optional[str] = Field(None, min_length=2, max_length=50)
    precio: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    marca: Optional[str] = Field(None, max_length=50)
    imagen_url: Optional[str] = None
    activo: Optional[bool] = None


class ProductoInDB(ProductoBase):
    id: str = Field(..., alias="_id", description="Identificador único del producto")
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "60d21b4667d0d8992e610c85",
                "nombre": "Laptop Gaming Pro X15",
                "descripcion": "Laptop gaming con procesador i7, 16GB RAM, RTX 4060, 512GB SSD",
                "categoria": "Laptops",
                "precio": 1299.99,
                "stock": 25,
                "marca": "TechGear",
                "imagen_url": "https://ejemplo.com/laptop.jpg",
                "activo": True,
                "fecha_creacion": "2024-01-15T10:30:00Z",
                "fecha_actualizacion": "2024-01-15T10:30:00Z"
            }
        }
    )


class ItemPedido(BaseModel):
    producto_id: str = Field(..., description="ID del producto")
    cantidad: int = Field(..., gt=0, description="Cantidad de unidades")
    precio_unitario: float = Field(..., gt=0, description="Precio unitario al momento del pedido")


class PedidoBase(BaseModel):
    cliente_nombre: str = Field(..., min_length=2, max_length=100, description="Nombre completo del cliente")
    cliente_email: str = Field(..., description="Correo electrónico del cliente")
    cliente_telefono: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto")
    direccion_envio: str = Field(..., min_length=10, description="Dirección completa de envío")
    items: List[ItemPedido] = Field(..., min_length=1, description="Lista de productos en el pedido")
    notas: Optional[str] = Field(None, description="Notas adicionales del cliente")


class PedidoCreate(PedidoBase):
    pass


class PedidoUpdate(BaseModel):
    estado: Optional[str] = Field(None, description="Estado del pedido: pendiente, procesando, enviado, entregado, cancelado")
    notas_internas: Optional[str] = Field(None, description="Notas internas del administrador")


class PedidoInDB(PedidoBase):
    id: str = Field(..., alias="_id", description="Identificador único del pedido")
    total: float = Field(..., gt=0, description="Total del pedido")
    estado: str = Field("pendiente", description="Estado del pedido")
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow)
    notas_internas: Optional[str] = Field(None, description="Notas internas del administrador")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "_id": "60d21b9997d0d8992e610c88",
                "cliente_nombre": "Juan Pérez",
                "cliente_email": "juan.perez@ejemplo.com",
                "cliente_telefono": "+573001234567",
                "direccion_envio": "Calle 123 #45-67, Bogotá, Colombia",
                "items": [
                    {
                        "producto_id": "60d21b4667d0d8992e610c85",
                        "cantidad": 1,
                        "precio_unitario": 1299.99
                    }
                ],
                "notas": "Entregar en horas de la tarde",
                "total": 1299.99,
                "estado": "pendiente",
                "fecha_creacion": "2024-01-15T11:00:00Z",
                "fecha_actualizacion": "2024-01-15T11:00:00Z"
            }
        }
    )
