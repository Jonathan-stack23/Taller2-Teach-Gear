# 🛒 TechGear - Sistema Híbrido de Catálogo y Pedidos

> Arquitectura de microservicios: **FastAPI** (API Core de alto rendimiento + MongoDB Atlas)
> y **Django MVT** (Portal Web del cliente que consume la API).

TechGear es una tienda especializada en hardware y accesorios tecnológicos. El sistema
procesa inventario y pedidos mediante una API RESTful de alto rendimiento, mientras que la
interfaz de cliente es robusta, segura y renderizada desde el servidor con Django.

---

## 🏗️ Arquitectura del Proyecto

```
Teller2/
├── 📁 techgear_api/          # FastAPI (Backend - API RESTful)
│   ├── main.py              # Aplicación FastAPI + endpoints CRUD
│   ├── database.py          # Conexión MongoDB Atlas (Motor async)
│   ├── schemas.py           # Modelos Pydantic (Producto, Pedido)
│   ├── seed_data.py         # Datos iniciales de ejemplo
│   ├── requirements.txt     # Dependencias del backend
│   ├── .env.example         # Variables de entorno (plantilla)
│   └── .env                 # Variables reales (NO versionar)
│
├── 📁 techgear_web/          # Django (Frontend - Portal Cliente MVT)
│   ├── 📁 config/           # Proyecto Django principal
│   │   ├── settings.py      # Configuración + API_BASE_URL
│   │   ├── urls.py          # Rutas raíz
│   │   └── wsgi.py / asgi.py
│   ├── 📁 catalogo/         # App Django (consume la API)
│   │   ├── views.py         # Vistas (Home, Catálogo, Pedidos)
│   │   ├── urls.py          # Rutas de la app
│   │   ├── api_service.py   # Cliente HTTP (requests → FastAPI)
│   │   └── models.py        # (no usa DB local, todo por API)
│   ├── 📁 templates/        # Plantillas HTML (Bootstrap 5)
│   │   ├── base.html
│   │   └── 📁 catalogo/
│   │       ├── home.html
│   │       ├── lista_productos.html
│   │       ├── detalle_producto.html
│   │       ├── crear_pedido.html
│   │       ├── lista_pedidos.html
│   │       └── detalle_pedido.html
│   ├── 📁 static/css/       # Estilos personalizados
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
│
└── README.md
```

---

## ⚙️ Requisitos Previos

- Python 3.11+
- Cluster de **MongoDB Atlas** (o MongoDB local)
- Conexión a internet (para CDN de Bootstrap y Swagger UI)

---

## 🚀 Instalación y Ejecución Paso a Paso

### 1️⃣ Clonar el repositorio

```bash
git clone <tu-repositorio>
cd Teller2
```

---

### 2️⃣ Configurar y levantar el Backend (FastAPI)

```bash
# Entrar al directorio
cd techgear_api

# (Opcional) Crear entorno virtual
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar y editar variables de entorno
copy .env.example .env          # Windows
# cp .env.example .env          # Linux/Mac
```

Edita `techgear_api/.env` con tu cadena de conexión a MongoDB Atlas:

```env
MONGODB_URL=mongodb+srv://<tu-usuario>:<tu-contraseña>@<tu-cluster>.mongodb.net/?appName=Taller2
API_HOST=0.0.0.0
API_PORT=8000
```

**Cargar datos iniciales (solo la primera vez):**
```bash
python seed_data.py
```

**Levantar la API:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

✅ La API estará en:
- **Swagger UI (documentación interactiva):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Estado de salud:** http://localhost:8000/health

---

### 3️⃣ Configurar y levantar el Frontend (Django)

Abre **otra terminal** (deja la API corriendo en la primera):

```bash
# Entrar al directorio del frontend
cd techgear_web

# (Opcional) Entorno virtual separado o usa el mismo
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Copiar variables de entorno
copy .env.example .env       # Windows
# cp .env.example .env       # Linux/Mac
```

Edita `techgear_web/.env` (debe apuntar a la API FastAPI):

```env
API_BASE_URL=http://localhost:8000
SECRET_KEY=django-insecure-cambia-esta-clave-en-produccion
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Aplicar migraciones (base de datos SQLite local para sesiones):**
```bash
python manage.py migrate
```

**Levantar el servidor Django:**
```bash
python manage.py runserver 8001
```

✅ El portal web estará en: http://localhost:8001

---

## 📋 Flujo de Usuario (Cómo usar la app)

1. Abre el portal web: http://localhost:8001
2. Explora el **Catálogo** de productos
3. Ingresa al detalle de un producto y **agrega al carrito**
4. Ve a **Finalizar Compra** (ícono carrito en la navbar)
5. Llena tus datos y confirma el pedido → se envía POST a FastAPI
6. Consulta tus pedidos en **Mis Pedidos** buscando por tu correo

---

## 🔌 Endpoints Principales de la API (FastAPI)

| Método | Ruta                 | Descripción                               |
|--------|----------------------|-------------------------------------------|
| GET    | `/`                  | Información de la API                     |
| GET    | `/health`            | Estado de salud + conexión MongoDB        |
| GET    | `/productos`         | Listar productos (filtros ?categoria, ?activo) |
| GET    | `/productos/{id}`    | Obtener un producto por ID                |
| POST   | `/productos`         | Crear nuevo producto (Pydantic validado)  |
| PUT    | `/productos/{id}`    | Actualizar producto                       |
| DELETE | `/productos/{id}`    | Eliminar producto                         |
| GET    | `/pedidos`           | Listar pedidos (?estado, ?cliente_email)  |
| GET    | `/pedidos/{id}`      | Obtener pedido por ID                     |
| POST   | `/pedidos`           | **Crear pedido (valida stock y descuenta)** |
| PATCH  | `/pedidos/{id}`      | Actualizar estado / notas internas        |

💡 Prueba todos los endpoints desde la interfaz de **Swagger UI** en
`http://localhost:8000/docs` — incluye ejemplos de request/response y validación Pydantic.

---

## ✅ Criterios de Aceptación Cumplidos

- ✅ **Arquitectura de carpetas:** `/techgear_api` (FastAPI) y `/techgear_web` (Django)
- ✅ **Backend FastAPI:** endpoints CRUD + Pydantic + Motor async a MongoDB Atlas
- ✅ **Validación Pydantic estricta:** esquemas Producto, Pedido, Items
- ✅ **Swagger UI** nativo documentado (`/docs`) con ejemplos
- ✅ **Portal Django MVT:** Models vacíos (datos por API), Views, Templates completos
- ✅ **Django consume API:** servicio HTTP `api_service.py` con `requests`
- ✅ **Carrito por sesión:** Django Sessions (SQLite) sin login
- ✅ **README.md** con comandos, variables de entorno y estructura
- ✅ **`.env.example`** en ambos proyectos (sin contraseñas reales)
- ✅ **Estados de pedido:** pendiente → procesando → enviado → entregado / cancelado
- ✅ **Validación de stock automática** al crear pedidos (API)

---

## 📝 Plan de Desarrollo y Commits Sugeridos

Usa estos mensajes de commit para evidenciar progreso por clase:

**Clase 1 (Entorno y Arquitectura):**
```bash
git init
git add .
git commit -m "feat: estructura inicial techgear_api + techgear_web"
git commit -m "feat: esquemas Pydantic Producto y Pedido + conexión MongoDB"
git commit -m "chore: requirements.txt y variables de entorno"
```

**Clase 2 (API REST y Swagger UI):**
```bash
git commit -m "feat: endpoints CRUD de productos en FastAPI"
git commit -m "feat: endpoint de creación y consulta de pedidos"
git commit -m "feat: validación de stock y cálculo de total en pedidos"
git commit -m "docs: README con instrucciones de instalación"
git push -u origin main
```

---

## 🔐 Variables de Entorno Importantes

| Variable          | Proyecto       | Descripción                                         |
|-------------------|----------------|-----------------------------------------------------|
| `MONGODB_URL`     | techgear_api   | String de conexión completo a MongoDB Atlas         |
| `API_BASE_URL`    | techgear_web   | URL donde corre FastAPI (ej: http://localhost:8000) |
| `SECRET_KEY`      | techgear_web   | Clave secreta de Django (cambiar en producción)     |
| `DEBUG`           | techgear_web   | `True` dev / `False` producción                     |
| `ALLOWED_HOSTS`   | techgear_web   | Hosts permitidos separados por coma                 |

> ⚠️ **NUNCA** hagas commit de los archivos `.env` reales — solo `.env.example`.
> Asegúrate de tener `.env` en tu `.gitignore`.

---

## 🛠️ Tecnologías Utilizadas

- **Backend:** FastAPI, Uvicorn, Motor (async MongoDB), Pydantic v2
- **Base de Datos:** MongoDB Atlas (cluster en la nube)
- **Frontend:** Django 4.2 MVT, Requests, Django Sessions
- **UI/UX:** Bootstrap 5.3, Bootstrap Icons, CSS personalizado
- **Documentación:** Swagger UI (OpenAPI) + ReDoc
- **Control de Versiones:** Git + GitHub

---

## 📞 Soporte

Si tienes dudas:
1. Consulta `/docs` de la API para ver los esquemas en vivo
2. Revisa los logs de ambos servidores en la terminal
3. Verifica que ambas URLs respondan (API:8000, Web:8001)

---

**¡Listo para vender hardware como un jefe! 🎮💻🚀**
