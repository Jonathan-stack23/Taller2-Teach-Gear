from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch


class CatalogoTemplatesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.sample_producto = {
            "id": "60d21b4667d0d8992e610c85",
            "nombre": "Laptop Gaming Pro X15",
            "descripcion": "Laptop gaming de alto rendimiento con RTX 4060 y 16GB RAM.",
            "categoria": "Laptops",
            "precio": 1299.99,
            "stock": 10,
            "marca": "TechGear",
            "imagen_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302",
            "activo": True,
        }
        self.sample_pedido = {
            "id": "60d21b9997d0d8992e610c88",
            "cliente_nombre": "Carlos Rodríguez",
            "cliente_email": "carlos@example.com",
            "cliente_telefono": "3001234567",
            "direccion_envio": "Carrera 7 # 71-21, Bogotá",
            "items": [
                {
                    "producto_id": "60d21b4667d0d8992e610c85",
                    "cantidad": 1,
                    "precio_unitario": 1299.99,
                }
            ],
            "total": 1299.99,
            "estado": "pendiente",
            "fecha_creacion": "2026-08-24T12:00:00Z",
            "fecha_actualizacion": "2026-08-24T12:00:00Z",
        }

    @patch('catalogo.views.api_client.listar_productos')
    def test_home_template_render(self, mock_listar):
        mock_listar.return_value = ([self.sample_producto], None)
        response = self.client.get(reverse('catalogo:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/home.html')
        self.assertContains(response, "Laptop Gaming Pro X15")
        self.assertContains(response, "1299")


    @patch('catalogo.views.api_client.listar_productos')
    def test_lista_productos_template_render(self, mock_listar):
        mock_listar.return_value = ([self.sample_producto], None)
        response = self.client.get(reverse('catalogo:lista_productos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/lista_productos.html')
        self.assertContains(response, "Catálogo de Productos")
        self.assertContains(response, "Laptop Gaming Pro X15")
        self.assertContains(response, "Laptops")

    @patch('catalogo.views.api_client.obtener_producto')
    def test_detalle_producto_template_render(self, mock_obtener):
        mock_obtener.return_value = (self.sample_producto, None)
        response = self.client.get(reverse('catalogo:detalle_producto', args=[self.sample_producto['id']]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/detalle_producto.html')
        self.assertContains(response, "Laptop Gaming Pro X15")
        self.assertContains(response, "Agregar al Carrito")

    def test_crear_pedido_vacio_render(self):
        response = self.client.get(reverse('catalogo:crear_pedido'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/crear_pedido.html')
        self.assertContains(response, "Tu carrito está vacío")

    @patch('catalogo.views.api_client.listar_pedidos')
    def test_lista_pedidos_render(self, mock_pedidos):
        mock_pedidos.return_value = ([self.sample_pedido], None)
        response = self.client.get(reverse('catalogo:lista_pedidos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/lista_pedidos.html')
        self.assertContains(response, "Carlos Rodríguez")
        self.assertContains(response, "carlos@example.com")

    @patch('catalogo.views.api_client.obtener_pedido')
    def test_detalle_pedido_render(self, mock_pedido):
        mock_pedido.return_value = (self.sample_pedido, None)
        response = self.client.get(reverse('catalogo:detalle_pedido', args=[self.sample_pedido['id']]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalogo/detalle_pedido.html')
        self.assertContains(response, "Detalle de la Orden")
        self.assertContains(response, "Carrera 7 # 71-21, Bogotá")
