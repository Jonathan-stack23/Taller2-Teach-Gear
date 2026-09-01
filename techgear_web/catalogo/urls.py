from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    path('', views.home, name='home'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/nuevo/', views.crear_producto, name='crear_producto'),
    path('productos/<str:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('carrito/eliminar/<str:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('pedidos/nuevo/', views.crear_pedido, name='crear_pedido'),
    path('pedidos/', views.lista_pedidos, name='lista_pedidos'),
    path('pedidos/<str:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),
]

