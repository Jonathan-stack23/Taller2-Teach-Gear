import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = "TechGearDB"

client = MongoClient(MONGODB_URL)
db = client[DATABASE_NAME]

productos_collection = db["productos"]
pedidos_collection = db["pedidos"]


def test_conexion():
    try:
        client.admin.command('ping')
        print("✅ Conexión exitosa a MongoDB Atlas")
        print(f"✅ Base de datos: {DATABASE_NAME}")
        return True
    except Exception as e:
        print(f"❌ Error al conectar a MongoDB: {e}")
        return False
