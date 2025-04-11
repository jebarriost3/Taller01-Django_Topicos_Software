from django.urls import path
from .views import (
    lista_pedidos, lista_productos, crear_producto, eliminar_producto, comprar_producto,ver_wishlist,agregar_a_wishlist,eliminar_de_wishlist,
    ver_carrito, agregar_al_carrito,productos_mas_vendidos,finalizar_compra, eliminar_del_carrito, iniciar_sesion, cerrar_sesion ,registro # Asegurar estas importaciones
)

urlpatterns = [
    path('productos/', lista_productos, name='lista_productos'),
    path('productos/crear/', crear_producto, name='crear_producto'),
    path('productos/eliminar/<int:producto_id>/', eliminar_producto, name='eliminar_producto'),
    path('comprar/', comprar_producto, name='comprar_producto'),
    path('pedidos/', lista_pedidos, name='lista_pedidos'),
    path('carrito/', ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:producto_id>/', eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/finalizar/', finalizar_compra, name='finalizar_compra'),  # Nueva ruta para comprar desde el carrito
    path('productos/', lista_productos, name='lista_productos'),
    path('carrito/finalizar/', finalizar_compra, name='finalizar_compra'),
    path('productos/mas_vendidos/', productos_mas_vendidos, name='productos_mas_vendidos'),
    path('wishlist/', ver_wishlist, name='ver_wishlist'),
    path('wishlist/agregar/<int:producto_id>/', agregar_a_wishlist, name='agregar_a_wishlist'),
    path('wishlist/eliminar/<int:producto_id>/', eliminar_de_wishlist, name='eliminar_de_wishlist'),
    path('registro/', registro, name='registro'),
    path('login/', iniciar_sesion, name='iniciar_sesion'),
    path('logout/', cerrar_sesion, name='cerrar_sesion')
    




]

