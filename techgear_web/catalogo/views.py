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
    categoria = request.GET.get('categoria', None)
    productos, error = api_client.listar_productos(categoria=categoria, activo=True)
    if productos is None:
        productos = []
        messages.error(request, f"No se pudieron cargar los productos: {error}")

    categorias = []
    if productos:
        categorias_unicas = {p['categoria'] for p in productos if p.get('categoria')}
        categorias = sorted(categorias_unicas)

    return render(request, 'catalogo/lista_productos.html', {
        'productos': productos,
        'categorias': categorias,
        'categoria_actual': categoria,
    })


def detalle_producto(request: HttpRequest, producto_id: str) -> HttpResponse:
    producto, error = api_client.obtener_producto(producto_id)
    if producto is None:
        messages.error(request, f"No se pudo cargar el producto: {error}")
        return redirect('catalogo:lista_productos')

    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        if cantidad <= 0:
            messages.error(request, "La cantidad debe ser mayor a cero.")
        elif cantidad > producto['stock']:
            messages.error(request, f"Stock insuficiente. Disponible: {producto['stock']}")
        else:
            carrito = request.session.get('carrito', [])
            item_existente = next(
                (item for item in carrito if item['producto_id'] == producto_id),
                None
            )
            if item_existente:
                item_existente['cantidad'] += cantidad
            else:
                carrito.append({
                    'producto_id': producto_id,
                    'nombre': producto['nombre'],
                    'precio': producto['precio'],
                    'cantidad': cantidad,
                    'imagen_url': producto.get('imagen_url'),
                })
            request.session['carrito'] = carrito
            messages.success(request, f"Se agregó {cantidad} unidad(es) al carrito.")
            return redirect('catalogo:lista_productos')

    return render(request, 'catalogo/detalle_producto.html', {
        'producto': producto,
    })


def crear_pedido(request: HttpRequest) -> HttpResponse:
    carrito = request.session.get('carrito', [])

    if not carrito:
        messages.warning(request, "Tu carrito está vacío. Agrega productos primero.")
        return redirect('catalogo:lista_productos')

    total = sum(item['precio'] * item['cantidad'] for item in carrito)

    if request.method == 'POST':
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
            pedido_id_nuevo = resultado.get('id') or resultado.get('_id')
            messages.success(request, f"¡Pedido creado exitosamente! Número: {pedido_id_nuevo}")
            return redirect('catalogo:detalle_pedido', pedido_id=pedido_id_nuevo)

    return render(request, 'catalogo/crear_pedido.html', {
        'carrito': carrito,
        'total': total,
    })


def lista_pedidos(request: HttpRequest) -> HttpResponse:
    email = request.GET.get('email', None)
    pedidos, error = api_client.listar_pedidos(email=email)
    if pedidos is None:
        pedidos = []
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
