# -*- coding: utf-8 -*-
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Forzar salida UTF-8 en Windows para soportar emojis en la consola
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = "TechGearDB"

client = MongoClient(MONGODB_URL)
db = client[DATABASE_NAME]

productos_collection = db["productos"]
pedidos_collection = db["pedidos"]


def test_conexion():
    try:
        client.admin.command('ping')
        print("[OK] Conexion exitosa a MongoDB Atlas")
        print(f"[OK] Base de datos: {DATABASE_NAME}")
        return True
    except Exception as e:
        print(f"[ERROR] Error al conectar a MongoDB: {e}")
        return False
