from django.views import View
from django.views.generic import ListView, CreateView, DeleteView, TemplateView, UpdateView, DetailView
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .models import Pedido, Categoria, DetallePedido, Producto, Carrito, CarritoItem
from .forms import ProductoForm, RegisterForm, LoginForm
from django.db.models import Sum
import json
from app.service.checkout_service import CheckoutService
from app.wishlist.factory import get_wishlist_manager #para importar el patron factory


# --- LISTAR Productos con filtros opcionales ---
class ProductoListView(ListView):
    model = Producto
    template_name = 'productos/lista_productos.html'
    context_object_name = 'productos'

    def get_queryset(self):
        queryset = super().get_queryset()
        categoria_id = self.request.GET.get('categoria', '')
        nombre = self.request.GET.get('nombre', '')

        if categoria_id.isdigit():
            queryset = queryset.filter(categoria__id=int(categoria_id))
        if nombre:
            queryset = queryset.filter(titulo__icontains=nombre)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        context['categoria_seleccionada'] = self.request.GET.get('categoria', '')
        context['nombre_buscado'] = self.request.GET.get('nombre', '')
        return context

# --- CREAR Producto ---
class ProductoCreateView(LoginRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/crear_producto.html'
    success_url = reverse_lazy('lista_productos')

    def form_valid(self, form):
        form.instance.artesano = self.request.user
        return super().form_valid(form)

# --- EDITAR Producto ---
class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'productos/editar_producto.html'
    success_url = reverse_lazy('lista_productos')

# --- ELIMINAR Producto ---
class ProductoDeleteView(LoginRequiredMixin, DeleteView):
    model = Producto
    template_name = 'productos/confirmar_eliminar.html'
    success_url = reverse_lazy('lista_productos')

# --- DETALLE de Producto (opcional) ---
class ProductoDetailView(DetailView):
    model = Producto
    template_name = 'productos/detalle_producto.html'
    context_object_name = 'producto'

class ListaPedidosView(View):
    def get(self, request):
        pedidos = Pedido.objects.all().prefetch_related('detalles')
        return render(request, 'productos/pedidos/lista_pedidos.html', {'pedidos': pedidos})

class HomeView(TemplateView):
    template_name = 'index.html'

@method_decorator(csrf_exempt, name='dispatch')
class ComprarProductoView(View):
    def post(self, request):
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
                productos = data.get('productos', [])
            else:
                producto_id = request.POST.get('producto_id')
                cantidad = int(request.POST.get('cantidad', 1))
                productos = [{'producto_id': producto_id, 'cantidad': cantidad}]

            if not productos:
                return JsonResponse({'error': 'No se enviaron productos'}, status=400)

            servicio = CheckoutService()
            pedido, _ = servicio.procesar_compra(productos, usuario=request.user if request.user.is_authenticated else None)

            if request.content_type == 'application/json':
                return JsonResponse({'mensaje': 'Compra realizada con éxito', 'pedido_id': pedido.id})
            else:
                return redirect('lista_pedidos')

        except ValueError as ve:
            return JsonResponse({'error': str(ve)}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Ocurrió un error inesperado: {str(e)}'}, status=500)

    def get(self, request):
        return JsonResponse({'error': 'Método no permitido'}, status=405)

class ObtenerCarritoMixin:
    def obtener_carrito(self, request):
        session_id = request.session.session_key
        if not session_id:
            request.session.create()
            session_id = request.session.session_key
        carrito, created = Carrito.objects.get_or_create(session_id=session_id)
        return carrito

class AgregarAlCarritoView(ObtenerCarritoMixin, View):
    def post(self, request, producto_id):
        carrito = self.obtener_carrito(request)
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = int(request.POST.get('cantidad', 1))
        item, created = CarritoItem.objects.get_or_create(carrito=carrito, producto=producto)
        if not created:
            item.cantidad += cantidad
        else:
            item.cantidad = cantidad
        item.save()
        return redirect('ver_carrito')

class EliminarDelCarritoView(ObtenerCarritoMixin, View):
    def post(self, request, producto_id):
        carrito = self.obtener_carrito(request)
        producto = get_object_or_404(Producto, id=producto_id)
        item = CarritoItem.objects.filter(carrito=carrito, producto=producto).first()
        if item:
            if item.cantidad > 1:
                item.cantidad -= 1
                item.save()
            else:
                item.delete()
        return redirect('ver_carrito')

class VerCarritoView(ObtenerCarritoMixin, View):
    def get(self, request):
        carrito = self.obtener_carrito(request)
        items = carrito.items.all()
        return render(request, 'carrito/ver_carrito.html', {'carrito': carrito, 'items': items})

class FinalizarCompraView(ObtenerCarritoMixin, View):
    def post(self, request):
        carrito = self.obtener_carrito(request)
        items = carrito.items.all()
        if not items:
            return redirect('ver_carrito')
        productos = [{'producto_id': item.producto.id, 'cantidad': item.cantidad} for item in items]
        try:
            servicio = CheckoutService()
            pedido, detalles = servicio.procesar_compra(productos_data=productos, usuario=request.user if request.user.is_authenticated else None)
            carrito.items.all().delete()
            return render(request, 'productos/detalle_compra.html', {'pedido': pedido, 'detalles': detalles})
        except ValueError as ve:
            return JsonResponse({'error': str(ve)}, status=400)
        except Exception as e:

            return JsonResponse({'error': f'Ocurrió un error inesperado: {str(e)}'}, status=500)
#Funciones de wishlist a partir del patrón factory
class ProductosMasVendidosView(View):
    def get(self, request):
        productos_vendidos = (
            DetallePedido.objects.values('producto__titulo')
            .annotate(total_vendido=Sum('cantidad'))
            .order_by('-total_vendido')[:10]
        )
        return render(request, 'productos/productos_mas_vendidos.html', {'productos_vendidos': productos_vendidos})

class AgregarAWishlistView(View):
    def post(self, request, producto_id):
        manager = get_wishlist_manager(request)
        manager.add(producto_id)
        return redirect('ver_wishlist')

class EliminarDeWishlistView(View):
    def post(self, request, producto_id):
        manager = get_wishlist_manager(request)
        manager.remove(producto_id)
        return redirect('ver_wishlist')

class VerWishlistView(View):
    def get(self, request):
        manager = get_wishlist_manager(request)
        wishlist = manager.get()
        productos = Producto.objects.filter(id__in=wishlist)
        return render(request, 'productos/wishlist.html', {'productos': productos})

class RegistroView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'login/registro.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        try:
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, "¡Registro exitoso! Bienvenido a la tienda.")
                return redirect(reverse_lazy('lista_productos'))
        except Exception as e:
            messages.error(request, f"Ocurrió un error durante el registro: {e}")
        return render(request, 'login/registro.html', {'form': form})

class IniciarSesionView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'login/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next') or reverse_lazy('lista_productos')
            return redirect(next_url)
        return render(request, 'login/login.html', {'form': form})

class CerrarSesionView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        return redirect('iniciar_sesion')
