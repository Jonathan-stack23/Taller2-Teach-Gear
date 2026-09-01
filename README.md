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
│   │       ├── crear_producto.html
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
7. Agrega nuevos productos en **Nuevo Producto** (`/productos/nuevo/`) con vista previa en tiempo real y validación Pydantic directa a MongoDB Atlas

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

## 📝 Clases 4, 5 y 6 — Desarrollo Frontend y Entrega Final

### 🖼️ Clase 4 — Django: Templates y Catálogo

**Objetivo:** Construcción de las plantillas HTML del Frontend usando Django Template Tags para iterar y renderizar los datos de la API.

**Archivos implementados:**

| Template | Descripción |
|----------|-------------|
| `base.html` | Plantilla base con navbar, footer y bloque de mensajes |
| `catalogo/home.html` | Hero section + productos destacados + estadísticas |
| `catalogo/lista_productos.html` | Grid de productos con filtros por categoría y búsqueda |
| `catalogo/detalle_producto.html` | Vista detallada + formulario de agregar al carrito |

**Template Tags utilizados:**
```django
{% extends 'base.html' %}              {# Herencia de plantillas #}
{% block content %}                    {# Bloques sobreescribibles #}
{% load static %}                      {# Archivos estáticos #}
{% url 'catalogo:home' %}              {# Resolución de URLs por nombre #}
{% for producto in productos %}        {# Iteración sobre listas de la API #}
{% if producto.stock == 0 %}           {# Condicional: badge Agotado #}
{% with estado=pedido.estado %}        {# Asignación de variables temporales #}
{{ producto.precio|floatformat:2 }}    {# Filtro: decimales #}
{{ producto.nombre|truncatechars:50 }} {# Filtro: truncar texto #}
{{ carrito|length }}                   {# Filtro: longitud de lista #}
{{ producto.categoria|default:"General" }} {# Filtro: valor por defecto #}
```

**Commit:**
```bash
git add .
git commit -m "feat(clase4): templates HTML del catálogo con Django Template Tags"
git push origin main
```

---

### 🛒 Clase 5 — Django: Formularios y Pedidos

**Objetivo:** Creación de la vista "Checkout". Captura de datos del cliente mediante un formulario HTML y envío POST hacia el endpoint en FastAPI.

**Flujo de checkout:**
```
1. Usuario navega al catálogo  (lista_productos.html)
2. Entra al detalle del producto (detalle_producto.html)
3. POST → agrega al carrito  (session['carrito'])
4. Va al checkout  (crear_pedido.html) con su formulario
5. Completa datos y hace clic en "Confirmar"
6. Django POST → api_client.crear_pedido() → FastAPI /pedidos
7. FastAPI valida stock, calcula total, guarda en MongoDB
8. Django redirige a detalle_pedido.html con confirmación
```

**Formulario de checkout (`crear_pedido.html`):**
```html
<form method="post" id="pedido-form">
    {% csrf_token %}   {# Obligatorio en todo POST de Django #}
    <input name="cliente_nombre" required>
    <input name="cliente_email" type="email" required>
    <input name="cliente_telefono" type="tel">
    <textarea name="direccion_envio" required></textarea>
    <textarea name="notas"></textarea>
    <button type="submit">Confirmar y Enviar Pedido</button>
</form>
```

**Archivos implementados:**

| Archivo | Descripción |
|---------|-------------|
| `catalogo/crear_pedido.html` | Checkout con resumen de carrito y formulario de cliente |
| `catalogo/detalle_pedido.html` | Confirmación con timeline de estados y desglose de items |
| `catalogo/lista_pedidos.html` | Búsqueda de pedidos por correo electrónico |
| `catalogo/views.py` → `crear_pedido()` | Vista que procesa el POST y llama a FastAPI |

**Commit:**
```bash
git add .
git commit -m "feat(clase5): flujo completo de creación de pedidos con formulario POST"
git push origin main
```

---

### 🛡️ Clase 6 — Refinamiento y Entrega Final

**Objetivo:** Manejo de excepciones, revisión del flujo completo y documentación final.

**Escenarios de excepción manejados:**

| Excepción | Comportamiento |
|-----------|----------------|
| API caída (ConnectionError) | Muestra alerta en home, retorna lista vacía en catálogo |
| Timeout de conexión | Mensaje de error amigable, sin crashear |
| Producto no encontrado (404) | Redirige a lista con `messages.error()` |
| Pedido no encontrado (404) | Redirige a lista_pedidos con mensaje |
| Stock insuficiente (400) | Permanece en checkout con error visible |
| Producto inactivo (400) | Permanece en checkout con error visible |
| Carrito vacío en POST | Redirige al catálogo con `messages.warning()` |

**Implementación en `api_service.py`:**
```python
# Captura de errores HTTP de FastAPI
except requests.ConnectionError as e:
    return None, f"Error de conexión: {str(e)}"
except requests.Timeout:
    return None, "Tiempo de espera agotado al conectar con la API"
# Para errores HTTP (400, 404, etc.):
detail = response.json().get("detail", response.text)
return None, f"Error {response.status_code}: {detail}"
```

**Implementación en `views.py`:**
```python
# Patrón consistente de manejo de errores en todas las vistas
productos, error = api_client.listar_productos(activo=True)
if productos is None:
    productos = []
    messages.error(request, f"No se pudieron cargar los productos: {error}")
```

**Tests cubiertos (`python manage.py test catalogo`):**

```
Clase 4 — Templates y Catálogo:
  ✅ test_home_template_render
  ✅ test_lista_productos_template_render
  ✅ test_detalle_producto_template_render
  ✅ test_crear_pedido_vacio_render
  ✅ test_lista_pedidos_render
  ✅ test_detalle_pedido_render
  ✅ test_badge_agotado_stock_cero
  ✅ test_estado_vacio_sin_productos
  ✅ test_busqueda_filtra_por_nombre
  ✅ test_detalle_producto_sin_stock_muestra_mensaje

Clase 5 — Formularios y Pedidos:
  ✅ test_agregar_al_carrito_guarda_en_sesion
  ✅ test_cantidad_invalida_no_agrega
  ✅ test_checkout_post_crea_pedido_y_redirige
  ✅ test_checkout_post_carrito_vacio_redirige_a_catalogo
  ✅ test_eliminar_producto_del_carrito
  ✅ test_vaciar_carrito_limpia_sesion

Clase 6 — Manejo de Excepciones:
  ✅ test_home_con_api_caida_muestra_alerta
  ✅ test_catalogo_con_api_caida_retorna_200
  ✅ test_producto_no_encontrado_redirige
  ✅ test_pedido_no_encontrado_redirige
  ✅ test_stock_insuficiente_muestra_error
  ✅ test_producto_inactivo_muestra_error
  ✅ test_flujo_completo_e2e

Creación de Productos:
  ✅ test_crear_producto_get_render
  ✅ test_crear_producto_post_exitoso
  ✅ test_crear_producto_post_validacion_errores
  ✅ test_crear_producto_post_api_error
```

---

## ☁️ Despliegue en Render (Render Blueprint)

El proyecto incluye el archivo [`render.yaml`](file:///c:/Users/Acer/Documents/Jonathan%20SENA/Python/3%20trimestre/Teller2/render.yaml) para desplegar automáticamente la arquitectura completa como un **Blueprint**:

1. Ve a tu cuenta de [Render Dashboard](https://dashboard.render.com/).
2. Haz clic en **New +** → **Blueprint**.
3. Conecta este repositorio de GitHub (`Taller2-Teach-Gear`).
4. Render detectará `render.yaml` y creará dos servicios web:
   - **`techgear-api`**: Servicio FastAPI (`uvicorn techgear_api.main:app`)
   - **`techgear-web`**: Servicio Django (`gunicorn config.wsgi:application` + WhiteNoise para estáticos)
5. Configura las variables de entorno en Render:
   - En **`techgear-api`**:
     - `MONGODB_URL`: Tu URI de conexión a MongoDB Atlas.
   - En **`techgear-web`**:
     - `API_BASE_URL`: La URL pública asignada a `techgear-api` en Render (ej: `https://techgear-api.onrender.com`).
     - `SECRET_KEY`: Tu clave secreta aleatoria para Django.
     - `ALLOWED_HOSTS`: `.onrender.com,localhost`
     - `DEBUG`: `False`
6. ¡Listo! Ambos servicios se compilarán y desplegarán automáticamente.

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
- **Frontend:** Django 4.2 MVT, Requests, Django Sessions, WhiteNoise
- **UI/UX:** Bootstrap 5.3, Bootstrap Icons, CSS personalizado
- **Documentación:** Swagger UI (OpenAPI) + ReDoc
- **Despliegue:** Render Blueprints (`render.yaml`) + Gunicorn
- **Control de Versiones:** Git + GitHub
- **Testing:** Django TestCase + unittest.mock (27 tests)

---

## 📞 Soporte

Si tienes dudas:
1. Consulta `/docs` de la API para ver los esquemas en vivo
2. Revisa los logs de ambos servidores en la terminal
3. Verifica que ambas URLs respondan (API:8000, Web:8001)

---

**¡Listo para vender hardware como un jefe! 🎮💻🚀**
