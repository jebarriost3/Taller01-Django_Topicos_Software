import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Pedido, Categoria, DetallePedido, Producto, Carrito, CarritoItem
from .forms import ProductoForm, RegisterForm, LoginForm
from django.views.decorators.csrf import csrf_exempt  # Asegurar esta importación
from django.http import JsonResponse
from django.contrib.sessions.models import Session
from .models import Carrito, CarritoItem, Producto
from django.db.models import Sum
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse

# Vista para listar productos
def lista_productos(request):
    categoria_id = request.GET.get('categoria', '')
    nombre = request.GET.get('nombre', '')

    productos = Producto.objects.all()
    
    # Filtrar por categoría si se seleccionó una
    if categoria_id.isdigit():  # Verifica si es un número
        productos = productos.filter(categoria__id=int(categoria_id))

    # Filtrar por nombre si se ingresó algo en la barra de búsqueda
    if nombre:
        productos = productos.filter(titulo__icontains=nombre)

    # Obtener todas las categorías disponibles
    categorias = Categoria.objects.all()

    return render(request, 'productos/lista_productos.html', {
        'productos': productos,
        'categorias': categorias,
        'categoria_seleccionada': categoria_id,
        'nombre_buscado': nombre,
    })
# Vista para agregar productos
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save(commit=False)

            # Solo asignar un usuario si está autenticado
            if request.user.is_authenticated:
                producto.artesano = request.user  
            else:
                producto.artesano = None  # Permitir productos sin usuario
            
            producto.save()
            return redirect('lista_productos')
    else:
        form = ProductoForm()
    
    return render(request, 'productos/crear_producto.html', {'form': form})


def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    return redirect('lista_productos') 



def lista_pedidos(request):
    pedidos = Pedido.objects.all().prefetch_related('detalles')  # Muestra todos los pedidos
    return render(request, 'productos/pedidos/lista_pedidos.html', {'pedidos': pedidos})



def home(request):
    return render(request, 'index.html')  # Asegúrate de tener este template

@csrf_exempt
def comprar_producto(request):
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                # Manejo de solicitudes JSON (API)
                data = json.loads(request.body)
                productos = data.get('productos', [])
            else:
                # Manejo de formularios HTML
                producto_id = request.POST.get('producto_id')
                cantidad = int(request.POST.get('cantidad', 1))
                productos = [{'producto_id': producto_id, 'cantidad': cantidad}]

            if not productos:
                return JsonResponse({'error': 'No se enviaron productos'}, status=400)

            pedido = Pedido.objects.create(total=0)
            total_pedido = 0

            for item in productos:
                producto_id = item.get('producto_id')
                cantidad = item.get('cantidad', 1)

                producto = get_object_or_404(Producto, id=producto_id)

                if producto.stock < cantidad:
                    return JsonResponse({'error': f'Stock insuficiente para {producto.titulo}'}, status=400)

                producto.stock -= cantidad
                producto.save()

                detalle = DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio
                )

                total_pedido += detalle.subtotal()

            pedido.total = total_pedido
            pedido.save()

            if request.content_type == 'application/json':
                return JsonResponse({'mensaje': 'Compra realizada con éxito', 'pedido_id': pedido.id})
            else:
                return redirect('lista_pedidos')  # Redirigir a la página de pedidos en HTML

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

def obtener_carrito(request):
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key
    
    carrito, created = Carrito.objects.get_or_create(session_id=session_id)
    return carrito

def agregar_al_carrito(request, producto_id):
    carrito = obtener_carrito(request)
    producto = get_object_or_404(Producto, id=producto_id)

    cantidad = int(request.POST.get('cantidad', 1))  # Obtener la cantidad desde el formulario

    item, created = CarritoItem.objects.get_or_create(carrito=carrito, producto=producto)
    
    if not created:
        item.cantidad += cantidad  # Sumar cantidad si ya existe en el carrito
    else:
        item.cantidad = cantidad

    item.save()

    return redirect('ver_carrito')  # Redirige al carrito después de agregar un producto

def eliminar_del_carrito(request, producto_id):
    carrito = obtener_carrito(request)
    producto = get_object_or_404(Producto, id=producto_id)

    item = CarritoItem.objects.filter(carrito=carrito, producto=producto).first()

    if item:
        if item.cantidad > 1:
            item.cantidad -= 1  # Reduce la cantidad en 1 si hay más de una unidad
            item.save()
        else:
            item.delete()  # Si solo hay una unidad, elimina el producto del carrito

    return redirect('ver_carrito')  # Redirige de nuevo al carrito después de eliminar

def ver_carrito(request):
    carrito = obtener_carrito(request)
    items = carrito.items.all()
    
    return render(request, 'carrito/ver_carrito.html', {'carrito': carrito, 'items': items})

def agregar_al_carrito(request, producto_id):
    carrito = obtener_carrito(request)
    producto = get_object_or_404(Producto, id=producto_id)

    item, created = CarritoItem.objects.get_or_create(carrito=carrito, producto=producto)
    if not created:
        item.cantidad += 1
        item.save()

    return redirect('ver_carrito')  # Redirige al carrito después de agregar un producto

def finalizar_compra(request):
    carrito = obtener_carrito(request)
    items = carrito.items.all()

    if not items:
        return redirect('ver_carrito')

    usuario = request.user if request.user.is_authenticated else None
    pedido = Pedido.objects.create(usuario=usuario, total=0)
    total_pedido = 0
    detalles = []

    for item in items:
        producto = item.producto
        cantidad = item.cantidad

        if producto.stock < cantidad:
            return JsonResponse({'error': f'Stock insuficiente para {producto.titulo}'}, status=400)

        # Reducir stock
        producto.stock -= cantidad
        producto.save()

        # Guardar detalle de pedido
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

    # Vaciar el carrito después de la compra
    carrito.items.all().delete()

    return render(request, 'productos/detalle_compra.html', {
        'pedido': pedido,
        'detalles': detalles
    })




def productos_mas_vendidos(request):
    productos_vendidos = (
        DetallePedido.objects.values('producto__titulo')
        .annotate(total_vendido=Sum('cantidad'))
        .order_by('-total_vendido')[:10]  # Obtener los 10 más vendidos
    )

    return render(request, 'productos/productos_mas_vendidos.html', {
        'productos_vendidos': productos_vendidos
    })

def obtener_wishlist(request):
    return request.session.get('wishlist', [])  # Obtener la wishlist desde la sesión

def guardar_wishlist(request, wishlist):
    request.session['wishlist'] = wishlist  # Guardar en la sesión
    request.session.modified = True  # Asegurar que Django guarde los cambios

def agregar_a_wishlist(request, producto_id):
    wishlist = obtener_wishlist(request)

    if producto_id not in wishlist:
        wishlist.append(producto_id)  # Agregar producto si no está en la lista

    guardar_wishlist(request, wishlist)
    return redirect('ver_wishlist')

def eliminar_de_wishlist(request, producto_id):
    wishlist = obtener_wishlist(request)

    if producto_id in wishlist:
        wishlist.remove(producto_id)  # Eliminar producto de la lista

    guardar_wishlist(request, wishlist)
    return redirect('ver_wishlist')

def ver_wishlist(request):
    wishlist = obtener_wishlist(request)
    productos = Producto.objects.filter(id__in=wishlist)  # Obtener productos guardados
    return render(request, 'productos/wishlist.html', {'productos': productos})

def registro(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        try:
            print(form.is_valid())
            if form.is_valid():
                print(form.errors)
                user = form.save()
                login(request, user)
                print(request.user.is_authenticated)
                messages.success(request, "¡Registro exitoso! Bienvenido a la tienda.")
                print("Redirigiendo a lista_productos")
                print(reverse('lista_productos'))
                return redirect(reverse('lista_productos'))
        except Exception as e:
            messages.error(request, f"Ocurrió un error durante el registro: {e}")
    else:
        form = RegisterForm()
    return render(request, 'login/registro.html', {'form': form})

def iniciar_sesion(request):
    form = AuthenticationForm()

    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('lista_productos')
    else:
        form = LoginForm()
    return render(request, 'login/login.html', {'form': form})

@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect('iniciar_sesion')