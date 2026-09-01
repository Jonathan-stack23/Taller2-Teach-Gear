from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch


class CatalogoTemplatesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.sample_producto = {
            'id': '60d21b4667d0d8992e610c85',
            'nombre': 'Laptop Gaming Pro X15',
            'descripcion': 'Laptop gaming de alto rendimiento con RTX 4060 y 16GB RAM.',
            'categoria': 'Laptops',
            'precio': 1299.99,
            'stock': 10,
            'marca': 'TechGear',
            'imagen_url': 'https://images.unsplash.com/photo-1603302576837-37561b2e2302',
            'activo': True,
        }
        self.sample_pedido = {
            'id': '60d21b9997d0d8992e610c88',
            'cliente_nombre': 'Carlos Rodriguez',
            'cliente_email': 'carlos@example.com',
            'cliente_telefono': '3001234567',
            'direccion_envio': 'Carrera 7 # 71-21, Bogota',
            'items': [{'producto_id': '60d21b4667d0d8992e610c85', 'cantidad': 1, 'precio_unitario': 1299.99}],
            'total': 1299.99,
            'estado': 'pendiente',
            'fecha_creacion': '2026-08-24T12:00:00Z',
            'fecha_actualizacion': '2026-08-24T12:00:00Z',
        }

    @patch('catalogo.views.api_client.listar_productos')
    def test_home_template_render(self, mock_listar):
        mock_listar.return_value = ([self.sample_producto], None)
        response = self.client.get(reverse('catalogo:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/home.html')
        self.assertContains(response, 'Laptop Gaming Pro X15')
        self.assertContains(response, '1299')

    @patch('catalogo.views.api_client.listar_productos')
    def test_lista_productos_template_render(self, mock_listar):
        mock_listar.return_value = ([self.sample_producto], None)
        response = self.client.get(reverse('catalogo:lista_productos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/lista_productos.html')
        self.assertContains(response, 'Laptop Gaming Pro X15')
        self.assertContains(response, 'Laptops')

    @patch('catalogo.views.api_client.obtener_producto')
    def test_detalle_producto_template_render(self, mock_obtener):
        mock_obtener.return_value = (self.sample_producto, None)
        response = self.client.get(reverse('catalogo:detalle_producto', args=[self.sample_producto['id']]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/detalle_producto.html')
        self.assertContains(response, 'Laptop Gaming Pro X15')
        self.assertContains(response, 'Agregar al Carrito')

    def test_crear_pedido_vacio_render(self):
        response = self.client.get(reverse('catalogo:crear_pedido'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/crear_pedido.html')
        self.assertContains(response, 'carrito')

    @patch('catalogo.views.api_client.listar_pedidos')
    def test_lista_pedidos_render(self, mock_pedidos):
        mock_pedidos.return_value = ([self.sample_pedido], None)
        response = self.client.get(reverse('catalogo:lista_pedidos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/lista_pedidos.html')
        self.assertContains(response, 'Carlos Rodriguez')
        self.assertContains(response, 'carlos@example.com')

    @patch('catalogo.views.api_client.obtener_pedido')
    def test_detalle_pedido_render(self, mock_pedido):
        mock_pedido.return_value = (self.sample_pedido, None)
        response = self.client.get(reverse('catalogo:detalle_pedido', args=[self.sample_pedido['id']]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/detalle_pedido.html')
        self.assertContains(response, 'Detalle de la Orden')
        self.assertContains(response, 'Carrera 7')

    @patch('catalogo.views.api_client.listar_productos')
    def test_badge_agotado_stock_cero(self, mock_listar):
        producto_sin_stock = dict(self.sample_producto, stock=0, id='abc123')
        mock_listar.return_value = ([producto_sin_stock], None)
        response = self.client.get(reverse('catalogo:home'))
        self.assertContains(response, 'Agotado')

    @patch('catalogo.views.api_client.listar_productos')
    def test_estado_vacio_sin_productos(self, mock_listar):
        mock_listar.return_value = ([], None)
        response = self.client.get(reverse('catalogo:home'))
        self.assertContains(response, 'No hay productos disponibles')

    @patch('catalogo.views.api_client.listar_productos')
    def test_busqueda_filtra_por_nombre(self, mock_listar):
        producto2 = dict(
            self.sample_producto,
            nombre='SSD Agotado 2TB',
            descripcion='Disco de estado solido NVMe de alta velocidad.',
            id='abc456',
            categoria='Almacenamiento',
        )
        mock_listar.return_value = ([self.sample_producto, producto2], None)
        response = self.client.get(reverse('catalogo:lista_productos') + '?q=Laptop')
        self.assertContains(response, 'Laptop Gaming Pro X15')
        self.assertNotContains(response, 'SSD Agotado 2TB')

    @patch('catalogo.views.api_client.obtener_producto')
    def test_detalle_producto_sin_stock_muestra_mensaje(self, mock_obtener):
        producto_sin_stock = dict(self.sample_producto, stock=0)
        mock_obtener.return_value = (producto_sin_stock, None)
        url = reverse('catalogo:detalle_producto', args=[self.sample_producto['id']])
        response = self.client.get(url)
        self.assertContains(response, 'Agotado')


class Clase5FormulariosPedidosTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.producto = {
            'id': '60d21b4667d0d8992e610c85',
            'nombre': 'Laptop Gaming Pro X15',
            'descripcion': 'Laptop gaming de alto rendimiento.',
            'categoria': 'Laptops',
            'precio': 1299.99,
            'stock': 10,
            'marca': 'TechGear',
            'imagen_url': None,
            'activo': True,
        }
        self.pedido = {
            'id': '60d21b9997d0d8992e610c88',
            'cliente_nombre': 'Carlos Rodriguez',
            'cliente_email': 'carlos@example.com',
            'cliente_telefono': '3001234567',
            'direccion_envio': 'Carrera 7 # 71-21, Bogota',
            'items': [{'producto_id': '60d21b4667d0d8992e610c85', 'cantidad': 1, 'precio_unitario': 1299.99}],
            'total': 1299.99,
            'estado': 'pendiente',
            'notas': None,
            'fecha_creacion': '2026-08-24T12:00:00Z',
            'fecha_actualizacion': '2026-08-24T12:00:00Z',
        }

    @patch('catalogo.views.api_client.obtener_producto')
    def test_agregar_al_carrito_guarda_en_sesion(self, mock_obtener):
        mock_obtener.return_value = (self.producto, None)
        url = reverse('catalogo:detalle_producto', args=[self.producto['id']])
        response = self.client.post(url, {'cantidad': '1'})
        self.assertRedirects(response, reverse('catalogo:crear_pedido'))
        carrito = self.client.session.get('carrito', [])
        self.assertEqual(len(carrito), 1)
        self.assertEqual(carrito[0]['producto_id'], self.producto['id'])

    @patch('catalogo.views.api_client.obtener_producto')
    def test_cantidad_invalida_no_agrega(self, mock_obtener):
        producto_poco_stock = dict(self.producto, stock=2)
        mock_obtener.return_value = (producto_poco_stock, None)
        url = reverse('catalogo:detalle_producto', args=[self.producto['id']])
        self.client.post(url, {'cantidad': '99'})
        carrito = self.client.session.get('carrito', [])
        self.assertEqual(len(carrito), 0)

    @patch('catalogo.views.api_client.obtener_producto')
    @patch('catalogo.views.api_client.crear_pedido')
    @patch('catalogo.views.api_client.obtener_pedido')
    def test_checkout_post_crea_pedido_y_redirige(self, mock_obtener_pedido, mock_crear, mock_obtener):
        mock_obtener.return_value = (self.producto, None)
        mock_crear.return_value = (self.pedido, None)
        mock_obtener_pedido.return_value = (self.pedido, None)
        url_detalle = reverse('catalogo:detalle_producto', args=[self.producto['id']])
        self.client.post(url_detalle, {'cantidad': '1'})
        datos_form = {
            'cliente_nombre': 'Carlos Rodriguez',
            'cliente_email': 'carlos@example.com',
            'cliente_telefono': '3001234567',
            'direccion_envio': 'Carrera 7 # 71-21, Bogota, Colombia',
            'notas': '',
        }
        response = self.client.post(reverse('catalogo:crear_pedido'), datos_form)
        self.assertRedirects(response, reverse('catalogo:detalle_pedido', args=[self.pedido['id']]))
        self.assertEqual(self.client.session.get('carrito', []), [])

    def test_checkout_post_carrito_vacio_redirige_a_catalogo(self):
        datos_form = {'cliente_nombre': 'Test', 'cliente_email': 'test@test.com',
                      'cliente_telefono': '', 'direccion_envio': 'Calle 1 # 2-3, Ciudad'}
        response = self.client.post(reverse('catalogo:crear_pedido'), datos_form)
        self.assertRedirects(response, reverse('catalogo:lista_productos'))

    @patch('catalogo.views.api_client.obtener_producto')
    def test_eliminar_producto_del_carrito(self, mock_obtener):
        mock_obtener.return_value = (self.producto, None)
        url_detalle = reverse('catalogo:detalle_producto', args=[self.producto['id']])
        self.client.post(url_detalle, {'cantidad': '1'})
        self.assertEqual(len(self.client.session.get('carrito', [])), 1)
        url_eliminar = reverse('catalogo:eliminar_del_carrito', args=[self.producto['id']])
        self.client.get(url_eliminar)
        self.assertEqual(len(self.client.session.get('carrito', [])), 0)

    @patch('catalogo.views.api_client.obtener_producto')
    def test_vaciar_carrito_limpia_sesion(self, mock_obtener):
        mock_obtener.return_value = (self.producto, None)
        url_detalle = reverse('catalogo:detalle_producto', args=[self.producto['id']])
        self.client.post(url_detalle, {'cantidad': '1'})
        response = self.client.get(reverse('catalogo:vaciar_carrito'))
        self.assertRedirects(response, reverse('catalogo:lista_productos'))
        self.assertEqual(self.client.session.get('carrito', []), [])


class Clase6ManejoExcepcionesTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.producto = {
            'id': '60d21b4667d0d8992e610c85',
            'nombre': 'Laptop Gaming Pro X15',
            'descripcion': 'Laptop gaming de alto rendimiento.',
            'categoria': 'Laptops',
            'precio': 1299.99,
            'stock': 10,
            'marca': 'TechGear',
            'imagen_url': None,
            'activo': True,
        }
        self.pedido = {
            'id': '60d21b9997d0d8992e610c88',
            'cliente_nombre': 'Carlos Rodriguez',
            'cliente_email': 'carlos@example.com',
            'cliente_telefono': '3001234567',
            'direccion_envio': 'Carrera 7 # 71-21, Bogota',
            'items': [{'producto_id': '60d21b4667d0d8992e610c85', 'cantidad': 1, 'precio_unitario': 1299.99}],
            'total': 1299.99,
            'estado': 'pendiente',
            'notas': None,
            'fecha_creacion': '2026-08-24T12:00:00Z',
            'fecha_actualizacion': '2026-08-24T12:00:00Z',
        }

    @patch('catalogo.views.api_client.listar_productos')
    def test_home_con_api_caida_muestra_alerta(self, mock_listar):
        mock_listar.return_value = (None, 'Error de conexion: [Errno 111] Connection refused')
        response = self.client.get(reverse('catalogo:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Servicio de Cat')
        self.assertContains(response, 'Connection refused')

    @patch('catalogo.views.api_client.listar_productos')
    def test_catalogo_con_api_caida_retorna_200(self, mock_listar):
        mock_listar.return_value = (None, 'Tiempo de espera agotado')
        response = self.client.get(reverse('catalogo:lista_productos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/lista_productos.html')

    @patch('catalogo.views.api_client.obtener_producto')
    def test_producto_no_encontrado_redirige(self, mock_obtener):
        mock_obtener.return_value = (None, 'Error 404: Producto no encontrado')
        url = reverse('catalogo:detalle_producto', args=['id-inexistente'])
        response = self.client.get(url)
        self.assertRedirects(response, reverse('catalogo:lista_productos'))

    @patch('catalogo.views.api_client.obtener_pedido')
    def test_pedido_no_encontrado_redirige(self, mock_pedido):
        mock_pedido.return_value = (None, 'Error 404: Pedido no encontrado')
        url = reverse('catalogo:detalle_pedido', args=['id-inexistente'])
        response = self.client.get(url)
        self.assertRedirects(response, reverse('catalogo:lista_pedidos'))

    @patch('catalogo.views.api_client.obtener_producto')
    @patch('catalogo.views.api_client.crear_pedido')
    def test_stock_insuficiente_muestra_error(self, mock_crear, mock_obtener):
        mock_obtener.return_value = (self.producto, None)
        mock_crear.return_value = (None, 'Error 400: Stock insuficiente para Laptop Gaming Pro X15.')
        url_detalle = reverse('catalogo:detalle_producto', args=[self.producto['id']])
        self.client.post(url_detalle, {'cantidad': '1'})
        datos_form = {'cliente_nombre': 'Laura Gomez', 'cliente_email': 'laura@test.com',
                      'cliente_telefono': '', 'direccion_envio': 'Avenida El Dorado # 69-76, Bogota'}
        response = self.client.post(reverse('catalogo:crear_pedido'), datos_form)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/crear_pedido.html')

    @patch('catalogo.views.api_client.obtener_producto')
    @patch('catalogo.views.api_client.crear_pedido')
    def test_producto_inactivo_muestra_error(self, mock_crear, mock_obtener):
        mock_obtener.return_value = (self.producto, None)
        mock_crear.return_value = (None, 'Error 400: Producto Laptop Gaming Pro X15 no esta disponible')
        url_detalle = reverse('catalogo:detalle_producto', args=[self.producto['id']])
        self.client.post(url_detalle, {'cantidad': '1'})
        datos_form = {'cliente_nombre': 'Pedro Sanchez', 'cliente_email': 'pedro@test.com',
                      'cliente_telefono': '', 'direccion_envio': 'Calle 100 # 15-20, Bogota'}
        response = self.client.post(reverse('catalogo:crear_pedido'), datos_form)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/crear_pedido.html')

    @patch('catalogo.views.api_client.obtener_producto')
    @patch('catalogo.views.api_client.crear_pedido')
    @patch('catalogo.views.api_client.obtener_pedido')
    def test_flujo_completo_e2e(self, mock_obtener_pedido, mock_crear, mock_obtener):
        mock_obtener.return_value = (self.producto, None)
        mock_crear.return_value = (self.pedido, None)
        mock_obtener_pedido.return_value = (self.pedido, None)
        url_detalle = reverse('catalogo:detalle_producto', args=[self.producto['id']])
        self.assertEqual(self.client.get(url_detalle).status_code, 200)
        resp2 = self.client.post(url_detalle, {'cantidad': '1'})
        self.assertRedirects(resp2, reverse('catalogo:crear_pedido'))
        resp3 = self.client.get(reverse('catalogo:crear_pedido'))
        self.assertEqual(resp3.status_code, 200)
        datos_form = {'cliente_nombre': 'Ana Lopez', 'cliente_email': 'ana@techgear.com',
                      'cliente_telefono': '3209876543',
                      'direccion_envio': 'Transversal 93 # 45-12, Medellin, Antioquia',
                      'notas': 'Llamar antes de entregar'}
        resp4 = self.client.post(reverse('catalogo:crear_pedido'), datos_form)
        self.assertRedirects(resp4, reverse('catalogo:detalle_pedido', args=[self.pedido['id']]))
        resp5 = self.client.get(reverse('catalogo:detalle_pedido', args=[self.pedido['id']]))
        self.assertEqual(resp5.status_code, 200)
        self.assertContains(resp5, 'Detalle de la Orden')


class CreacionProductosTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.nuevo_producto = {
            'id': '60d21b4667d0d8992e610c99',
            'nombre': 'Teclado Mecanico RGB Pro',
            'descripcion': 'Teclado mecanico con switches opticos y retroiluminacion RGB.',
            'categoria': 'Perifericos',
            'precio': 89.99,
            'stock': 15,
            'marca': 'TechGear',
            'imagen_url': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3',
            'activo': True,
        }

    @patch('catalogo.views.api_client.listar_productos')
    def test_crear_producto_get_render(self, mock_listar):
        mock_listar.return_value = ([self.nuevo_producto], None)
        response = self.client.get(reverse('catalogo:crear_producto'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/crear_producto.html')
        self.assertContains(response, 'Agregar Nuevo Producto')
        self.assertContains(response, 'Informaci')

    @patch('catalogo.views.api_client.obtener_producto')
    @patch('catalogo.views.api_client.listar_productos')
    @patch('catalogo.views.api_client.crear_producto')
    def test_crear_producto_post_exitoso(self, mock_crear, mock_listar, mock_obtener):
        mock_listar.return_value = ([], None)
        mock_crear.return_value = (self.nuevo_producto, None)
        mock_obtener.return_value = (self.nuevo_producto, None)
        datos = {
            'nombre': 'Teclado Mecanico RGB Pro',
            'descripcion': 'Teclado mecanico con switches opticos y retroiluminacion RGB.',
            'categoria': 'Perifericos',
            'precio': '89.99',
            'stock': '15',
            'marca': 'TechGear',
            'imagen_url': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3',
            'activo': 'on',
        }
        response = self.client.post(reverse('catalogo:crear_producto'), datos)
        self.assertRedirects(response, reverse('catalogo:detalle_producto', args=[self.nuevo_producto['id']]))
        mock_crear.assert_called_once()
        args_llamada = mock_crear.call_args[0][0]
        self.assertEqual(args_llamada['nombre'], 'Teclado Mecanico RGB Pro')
        self.assertEqual(args_llamada['precio'], 89.99)
        self.assertEqual(args_llamada['stock'], 15)
        self.assertTrue(args_llamada['activo'])

    @patch('catalogo.views.api_client.listar_productos')
    def test_crear_producto_post_validacion_errores(self, mock_listar):
        mock_listar.return_value = ([], None)
        datos_invalidos = {
            'nombre': 'A',  # Demasiado corto (<2)
            'descripcion': 'abc',  # Demasiado corto (<5)
            'categoria': '',
            'precio': '-10',  # Precio negativo
            'stock': '-5',  # Stock negativo
        }
        response = self.client.post(reverse('catalogo:crear_producto'), datos_invalidos)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/crear_producto.html')
        self.assertContains(response, 'al menos 2 caracteres')
        self.assertContains(response, 'al menos 5 caracteres')
        self.assertContains(response, 'La categor')

    @patch('catalogo.views.api_client.listar_productos')
    @patch('catalogo.views.api_client.crear_producto')
    def test_crear_producto_post_api_error(self, mock_crear, mock_listar):
        mock_listar.return_value = ([], None)
        mock_crear.return_value = (None, 'Error 500: Error interno del servidor en FastAPI')
        datos = {
            'nombre': 'Mouse Gaming Ultra',
            'descripcion': 'Mouse ergonomico de 16000 DPI con sensor optico avanzado.',
            'categoria': 'Perifericos',
            'precio': '49.99',
            'stock': '20',
            'marca': 'TechGear',
        }
        response = self.client.post(reverse('catalogo:crear_producto'), datos)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/crear_producto.html')
        self.assertContains(response, 'Error al crear el producto')
