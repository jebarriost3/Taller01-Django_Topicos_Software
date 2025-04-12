# services/checkout_service.py

from django.shortcuts import get_object_or_404
from app.models import Producto, Pedido, DetallePedido

class CheckoutService:
    def procesar_compra(self, productos_data, usuario=None):
        pedido = Pedido.objects.create(usuario=usuario, total=0)
        total_pedido = 0
        detalles = []

        for item in productos_data:
            producto_id = item.get('producto_id')
            cantidad = item.get('cantidad', 1)

            producto = get_object_or_404(Producto, id=producto_id)

            if producto.stock < cantidad:
                raise ValueError(f'Stock insuficiente para {producto.titulo}')

            producto.stock -= cantidad
            producto.save()

            detalle = DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio
            )

            total_pedido += detalle.subtotal()
            detalles.append(detalle)

        pedido.total = total_pedido
        pedido.save()
        return pedido, detalles
