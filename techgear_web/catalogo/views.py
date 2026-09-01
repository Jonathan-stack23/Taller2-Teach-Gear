from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from .api_service import api_client


def home(request: HttpRequest) -> HttpResponse:
    productos, error = api_client.listar_productos(activo=True)
    if productos is None:
        productos = []
        api_error = error
    else:
        api_error = None
        productos = productos[:6]

    return render(request, 'catalogo/home.html', {
        'productos_destacados': productos,
        'api_error': api_error,
    })


def lista_productos(request: HttpRequest) -> HttpResponse:
    categoria = request.GET.get('categoria', '').strip() or None
    busqueda = request.GET.get('q', '').strip()

    productos, error = api_client.listar_productos(categoria=categoria, activo=True)
    if productos is None:
        productos = []
        messages.error(request, f"No se pudieron cargar los productos: {error}")

    # Obtener todas las categorías para los filtros
    todos_productos, _ = api_client.listar_productos(activo=True)
    categorias = []
    if todos_productos:
        categorias = sorted({p['categoria'] for p in todos_productos if p.get('categoria')})

    # Filtrar por búsqueda si se especifica
    if busqueda and productos:
        termino = busqueda.lower()
        productos = [
            p for p in productos
            if termino in p.get('nombre', '').lower()
            or termino in p.get('descripcion', '').lower()
            or (p.get('marca') and termino in p.get('marca', '').lower())
            or (p.get('categoria') and termino in p.get('categoria', '').lower())
        ]

    return render(request, 'catalogo/lista_productos.html', {
        'productos': productos,
        'categorias': categorias,
        'categoria_actual': categoria,
        'busqueda': busqueda,
    })


def crear_producto(request: HttpRequest) -> HttpResponse:
    todos_productos, _ = api_client.listar_productos(activo=None)
    categorias = []
    if todos_productos:
        categorias = sorted({p['categoria'] for p in todos_productos if p.get('categoria')})
    if not categorias:
        categorias = ["Laptops", "Periféricos", "Monitores", "Componentes", "Audio", "Almacenamiento"]

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        categoria = request.POST.get('categoria', '').strip()
        precio_raw = request.POST.get('precio', '').strip()
        stock_raw = request.POST.get('stock', '').strip()
        marca = request.POST.get('marca', '').strip() or None
        imagen_url = request.POST.get('imagen_url', '').strip() or None
        activo = 'activo' in request.POST

        errores = []
        if not nombre or len(nombre) < 2:
            errores.append("El nombre del producto debe tener al menos 2 caracteres.")
        if not descripcion or len(descripcion) < 5:
            errores.append("La descripción debe tener al menos 5 caracteres.")
        if not categoria:
            errores.append("La categoría es obligatoria.")

        try:
            precio = float(precio_raw)
            if precio <= 0:
                errores.append("El precio debe ser un número mayor a 0.")
        except (ValueError, TypeError):
            errores.append("El precio ingresado no es válido.")
            precio = 0.0

        try:
            stock = int(stock_raw)
            if stock < 0:
                errores.append("El stock no puede ser negativo.")
        except (ValueError, TypeError):
            errores.append("El stock ingresado no es un número entero válido.")
            stock = 0

        form_data = {
            'nombre': nombre,
            'descripcion': descripcion,
            'categoria': categoria,
            'precio': precio_raw,
            'stock': stock_raw,
            'marca': marca or '',
            'imagen_url': imagen_url or '',
            'activo': activo,
        }

        if errores:
            for err in errores:
                messages.error(request, err)
            return render(request, 'catalogo/crear_producto.html', {
                'categorias': categorias,
                'form_data': form_data,
            })

        datos_producto = {
            'nombre': nombre,
            'descripcion': descripcion,
            'categoria': categoria,
            'precio': precio,
            'stock': stock,
            'marca': marca,
            'imagen_url': imagen_url,
            'activo': activo,
        }

        resultado, error = api_client.crear_producto(datos_producto)
        if resultado is None:
            messages.error(request, f"Error al crear el producto: {error}")
            return render(request, 'catalogo/crear_producto.html', {
                'categorias': categorias,
                'form_data': form_data,
            })

        nuevo_id = resultado.get('id') or resultado.get('_id')
        messages.success(request, f"¡Producto \"{nombre}\" agregado exitosamente al catálogo!")
        if nuevo_id:
            return redirect('catalogo:detalle_producto', producto_id=nuevo_id)
        return redirect('catalogo:lista_productos')

    return render(request, 'catalogo/crear_producto.html', {
        'categorias': categorias,
        'form_data': {
            'activo': True,
            'stock': 10,
        }
    })


def detalle_producto(request: HttpRequest, producto_id: str) -> HttpResponse:
    producto, error = api_client.obtener_producto(producto_id)
    if producto is None:
        messages.error(request, f"No se pudo cargar el producto: {error}")
        return redirect('catalogo:lista_productos')

    if request.method == 'POST':
        try:
            cantidad = int(request.POST.get('cantidad', 1))
        except (ValueError, TypeError):
            cantidad = 1

        if cantidad <= 0:
            messages.error(request, "La cantidad debe ser mayor a cero.")
        elif cantidad > producto.get('stock', 0):
            messages.error(request, f"Stock insuficiente. Disponible: {producto.get('stock', 0)}")
        else:
            carrito = request.session.get('carrito', [])
            item_existente = next(
                (item for item in carrito if item['producto_id'] == producto_id),
                None
            )
            if item_existente:
                nueva_cantidad = item_existente['cantidad'] + cantidad
                if nueva_cantidad > producto.get('stock', 0):
                    messages.error(request, f"No puedes agregar más del stock disponible ({producto.get('stock', 0)} unidades).")
                    return render(request, 'catalogo/detalle_producto.html', {'producto': producto})
                item_existente['cantidad'] = nueva_cantidad
            else:
                carrito.append({
                    'producto_id': producto_id,
                    'nombre': producto['nombre'],
                    'precio': producto['precio'],
                    'cantidad': cantidad,
                    'imagen_url': producto.get('imagen_url'),
                })
            request.session['carrito'] = carrito
            request.session.modified = True
            messages.success(request, f"¡{cantidad} unidad(es) de \"{producto['nombre']}\" agregadas al carrito!")
            return redirect('catalogo:crear_pedido')

    return render(request, 'catalogo/detalle_producto.html', {
        'producto': producto,
    })


def eliminar_del_carrito(request: HttpRequest, producto_id: str) -> HttpResponse:
    carrito = request.session.get('carrito', [])
    carrito = [item for item in carrito if item.get('producto_id') != producto_id]
    request.session['carrito'] = carrito
    request.session.modified = True
    messages.info(request, "Producto eliminado del carrito.")
    return redirect('catalogo:crear_pedido')


def vaciar_carrito(request: HttpRequest) -> HttpResponse:
    request.session['carrito'] = []
    request.session.modified = True
    messages.info(request, "El carrito ha sido vaciado.")
    return redirect('catalogo:lista_productos')


def crear_pedido(request: HttpRequest) -> HttpResponse:
    carrito = request.session.get('carrito', [])

    total = sum(item['precio'] * item['cantidad'] for item in carrito) if carrito else 0.0

    if request.method == 'POST':
        if not carrito:
            messages.warning(request, "Tu carrito está vacío. Agrega productos primero.")
            return redirect('catalogo:lista_productos')

        items = []
        for item in carrito:
            items.append({
                'producto_id': item['producto_id'],
                'cantidad': item['cantidad'],
                'precio_unitario': item['precio'],
            })

        datos_pedido = {
            'cliente_nombre': request.POST.get('cliente_nombre', '').strip(),
            'cliente_email': request.POST.get('cliente_email', '').strip(),
            'cliente_telefono': request.POST.get('cliente_telefono', '').strip() or None,
            'direccion_envio': request.POST.get('direccion_envio', '').strip(),
            'items': items,
            'notas': request.POST.get('notas', '').strip() or None,
        }

        resultado, error = api_client.crear_pedido(datos_pedido)
        if resultado is None:
            messages.error(request, f"No se pudo crear el pedido: {error}")
        else:
            request.session['carrito'] = []
            request.session.modified = True
            pedido_id_nuevo = resultado.get('id') or resultado.get('_id')
            messages.success(request, f"¡Pedido creado exitosamente! Número de orden: {pedido_id_nuevo}")
            return redirect('catalogo:detalle_pedido', pedido_id=pedido_id_nuevo)

    return render(request, 'catalogo/crear_pedido.html', {
        'carrito': carrito,
        'total': total,
    })


def lista_pedidos(request: HttpRequest) -> HttpResponse:
    email = request.GET.get('email', '').strip() or None
    pedidos, error = api_client.listar_pedidos(email=email)
    if pedidos is None:
        pedidos = []
        if email:
            messages.error(request, f"No se pudieron cargar los pedidos: {error}")

    return render(request, 'catalogo/lista_pedidos.html', {
        'pedidos': pedidos,
        'email_busqueda': email or '',
    })


def detalle_pedido(request: HttpRequest, pedido_id: str) -> HttpResponse:
    pedido, error = api_client.obtener_pedido(pedido_id)
    if pedido is None:
        messages.error(request, f"No se pudo cargar el pedido: {error}")
        return redirect('catalogo:lista_pedidos')

    return render(request, 'catalogo/detalle_pedido.html', {
        'pedido': pedido,
    })

