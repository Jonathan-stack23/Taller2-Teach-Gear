import sys
from datetime import datetime
from database import productos_collection, test_conexion


PRODUCTOS_EJEMPLO = [
    {
        "nombre": "Laptop Gaming TechGear Pro X15",
        "descripcion": "Laptop gaming de alto rendimiento con procesador Intel Core i7-13700H, 16GB RAM DDR5, NVIDIA RTX 4060 8GB, 512GB SSD NVMe y pantalla 15.6\" QHD 165Hz. Ideal para juegos y edición de video profesional.",
        "categoria": "Laptops",
        "precio": 1299.99,
        "stock": 15,
        "marca": "TechGear",
        "imagen_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=600",
        "activo": True,
        "fecha_creacion": datetime.utcnow(),
        "fecha_actualizacion": datetime.utcnow(),
    },
    {
        "nombre": "Teclado Mecánico RGB HyperStrike",
        "descripcion": "Teclado mecánico gaming con switches rojos, iluminación RGB personalizable por tecla, reposamuñecas magnético, construcción en aluminio y anti-ghosting completo de 104 teclas. Conectividad USB-C.",
        "categoria": "Periféricos",
        "precio": 129.99,
        "stock": 40,
        "marca": "HyperStrike",
        "imagen_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600",
        "activo": True,
        "fecha_creacion": datetime.utcnow(),
        "fecha_actualizacion": datetime.utcnow(),
    },
    {
        "nombre": "Monitor UltraWide 34\" QHD 144Hz",
        "descripcion": "Monitor curvo UltraWide 34 pulgadas con resolución QHD 3440x1440, frecuencia de actualización 144Hz, 1ms respuesta, HDR400, 95% DCI-P3 y puertos HDMI 2.1 + DisplayPort 1.4.",
        "categoria": "Monitores",
        "precio": 549.99,
        "stock": 12,
        "marca": "VisionPro",
        "imagen_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600",
        "activo": True,
        "fecha_creacion": datetime.utcnow(),
        "fecha_actualizacion": datetime.utcnow(),
    },
    {
        "nombre": "Mouse Gamer Wireless Pro Click",
        "descripcion": "Mouse gaming inalámbrico con sensor óptico 26K DPI, 6 botones programables, batería de 80 horas, iluminación RGB, peso ultraligero de 58g y switches ópticos.",
        "categoria": "Periféricos",
        "precio": 89.99,
        "stock": 60,
        "marca": "ProClick",
        "imagen_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600",
        "activo": True,
        "fecha_creacion": datetime.utcnow(),
        "fecha_actualizacion": datetime.utcnow(),
    },
    {
        "nombre": "Tarjeta Gráfica RTX 4070 Ti Super",
        "descripcion": "Tarjeta gráfica NVIDIA GeForce RTX 4070 Ti Super con 16GB VRAM GDDR6X, arquitectura Ada Lovelace, Ray Tracing de 3ª generación y DLSS 3.7. Rendimiento extremo para 4K.",
        "categoria": "Componentes",
        "precio": 899.99,
        "stock": 8,
        "marca": "NVIDIA",
        "imagen_url": "https://images.unsplash.com/photo-1591488320449-011701bb6704?w=600",
        "activo": True,
        "fecha_creacion": datetime.utcnow(),
        "fecha_actualizacion": datetime.utcnow(),
    },
    {
        "nombre": "Auriculares Gamer 7.1 Surround",
        "descripcion": "Auriculares gaming con sonido envolvente 7.1, drivers de 50mm, micrófono retráctil con cancelación de ruido, diadema acolchada premium e iluminación RGB. Cable de 2.2m con USB.",
        "categoria": "Audio",
        "precio": 119.99,
        "stock": 35,
        "marca": "SoundMax",
        "imagen_url": "https://images.unsplash.com/photo-1599669454699-248893623440?w=600",
        "activo": True,
        "fecha_creacion": datetime.utcnow(),
        "fecha_actualizacion": datetime.utcnow(),
    },
    {
        "nombre": "SSD NVMe 2TB Gen4 Ultra",
        "descripcion": "Unidad de estado sólido NVMe M.2 de 2TB con velocidad de lectura secuencial 7400MB/s y escritura 6800MB/s. Ideal para sistemas de alto rendimiento, edición 4K y gaming.",
        "categoria": "Almacenamiento",
        "precio": 189.99,
        "stock": 50,
        "marca": "SpeedDisk",
        "imagen_url": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=600",
        "activo": True,
        "fecha_creacion": datetime.utcnow(),
        "fecha_actualizacion": datetime.utcnow(),
    },
    {
        "nombre": "Webcam 4K Pro Streaming",
        "descripcion": "Cámara web profesional para streaming 4K 30fps o 1080p 60fps, autoenfoque, corrección de luz HDR, micrófonos duales con cancelación de ruido y soporte para trípode.",
        "categoria": "Accesorios",
        "precio": 159.99,
        "stock": 22,
        "marca": "StreamCam",
        "imagen_url": "https://images.unsplash.com/photo-1587826080692-f439cd0b70da?w=600",
        "activo": True,
        "fecha_creacion": datetime.utcnow(),
        "fecha_actualizacion": datetime.utcnow(),
    },
    {
        "nombre": "Silla Gamer ErgoPro X",
        "descripcion": "Silla gaming ergonómica con respaldo ajustable hasta 180°, soporte lumbar y cervical, reposabrazos 4D, base de acero, pistón clase 4 y tapizado en cuero sintético premium.",
        "categoria": "Accesorios",
        "precio": 399.99,
        "stock": 10,
        "marca": "ErgoPro",
        "imagen_url": "https://images.unsplash.com/photo-1592078615290-033ee584e267?w=600",
        "activo": True,
        "fecha_creacion": datetime.utcnow(),
        "fecha_actualizacion": datetime.utcnow(),
    },
]


def main():
    print("🚀 Iniciando carga de datos de ejemplo...\n")

    ok = test_conexion()
    if not ok:
        print("❌ No se pudo conectar a MongoDB. Saliendo.")
        sys.exit(1)

    try:
        count = productos_collection.count_documents({})
        print(f"📦 Productos existentes: {count}")

        if count > 0:
            print("\n⚠️  La colección ya tiene productos.")
            if "--force" in sys.argv:
                respuesta = "s"
            else:
                try:
                    respuesta = input("¿Deseas eliminar los existentes y cargar los datos de ejemplo? (s/N): ").strip().lower()
                except EOFError:
                    respuesta = "n"
            if respuesta == 's':
                productos_collection.delete_many({})
                print("✅ Eliminados todos los productos anteriores.")
            else:
                print("Operación cancelada.")
                return

        resultado = productos_collection.insert_many(PRODUCTOS_EJEMPLO)
        print(f"\n✅ Cargados {len(resultado.inserted_ids)} productos exitosamente!")

        print("\n📋 Resumen de productos cargados:")
        for prod in productos_collection.find({}):
            print(f"  • [{prod['categoria']}] {prod['nombre']} - ${prod['precio']:.2f} ({prod['stock']} en stock)")

        print("\n🎉 ¡Datos de ejemplo listos! Puedes iniciar la API con:")
        print("   uvicorn main:app --reload --port 8000")

    except Exception as e:
        print(f"\n❌ Error durante la carga: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
