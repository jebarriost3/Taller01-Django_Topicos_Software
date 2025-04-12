from django.urls import path
from .views import (
    ListaPedidosView,
    ProductoListView,
    ProductoCreateView,
    ProductoDeleteView,
    ProductoUpdateView,
    ComprarProductoView,
    VerCarritoView,
    AgregarAlCarritoView,
    EliminarDelCarritoView,
    FinalizarCompraView,
    ProductosMasVendidosView,
    VerWishlistView,
    AgregarAWishlistView,
    EliminarDeWishlistView,
    RegistroView,
    IniciarSesionView,
    CerrarSesionView
)

urlpatterns = [
    path('productos/', ProductoListView.as_view(), name='lista_productos'),
    path('productos/crear/', ProductoCreateView.as_view(), name='crear_producto'),
    path('productos/eliminar/<int:producto_id>/', ProductoDeleteView.as_view(), name='eliminar_producto'),
    path('comprar/', ComprarProductoView.as_view(), name='comprar_producto'),
    path('pedidos/', ListaPedidosView.as_view(), name='lista_pedidos'),
    path('carrito/', VerCarritoView.as_view(), name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', AgregarAlCarritoView.as_view(), name='agregar_al_carrito'),
    path('carrito/eliminar/<int:producto_id>/', EliminarDelCarritoView.as_view(), name='eliminar_del_carrito'),
    path('carrito/finalizar/', FinalizarCompraView.as_view(), name='finalizar_compra'),
    path('productos/mas_vendidos/', ProductosMasVendidosView.as_view(), name='productos_mas_vendidos'),
    path('wishlist/', VerWishlistView.as_view(), name='ver_wishlist'),
    path('wishlist/agregar/<int:producto_id>/', AgregarAWishlistView.as_view(), name='agregar_a_wishlist'),
    path('wishlist/eliminar/<int:producto_id>/', EliminarDeWishlistView.as_view(), name='eliminar_de_wishlist'),
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', IniciarSesionView.as_view(), name='iniciar_sesion'),
    path('logout/', CerrarSesionView.as_view(), name='cerrar_sesion')
]
