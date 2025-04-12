# ARTE-SANO
##  Cómo ejecutar el proyecto

## 1. Clonar el repositorio
```bash
git clone https://github.com/jmgarzonv/ARTE-SANO.git
```

## 2. Cambiar a la rama login.
```bash
git checkout login
cd  ARTE-SANO-login
```
## 3. Instalar dependencias.
```bash
pip install -r requirements.txt

```
## Configurar la base de datos:
```bash
python manage.py migrate


```
## Ejecutar el servidor.
```bash
python manage.py runserver




```
## Finalmente abre el navegador e ingresa a la pagina.

### Taller 1

# ARTE-SANO


## 2. Revisión Autocrítica del Proyecto ARTE-SANO

Se analiza este proyecto bajo los parámetros de calidad: **Usabilidad, Compatibilidad, Rendimiento y Seguridad**, con observaciones y sugerencias de mejora e inversión.

---

###  Usabilidad

** Aspectos positivos:**
- Navegación clara con enlaces visibles a funcionalidades clave como "Inicio", "Nuevo Producto", carrito y pedidos.
- Interfaz simple y funcional con botones intuitivos.

** Aspectos a mejorar:**
- Falta retroalimentación visual inmediata tras acciones (por ejemplo, confirmaciones).
- No hay validación visual de formularios (mensajes de error, campos obligatorios).
- Falta optimización para dispositivos móviles.

** Inversión sugerida:**
- Implementar alertas visuales con SweetAlert2.
- Integrar un sistema de diseño responsivo como TailwindCSS o Bootstrap.

---

###  Compatibilidad

** Aspectos positivos:**
- Uso estándar de Django asegura buena compatibilidad con servidores comunes.
- Buenas prácticas en rutas y vistas.

** Aspectos a mejorar:**
- No se han realizado pruebas en diferentes navegadores o dispositivos.
- Falta de uso de clases CSS multiplataforma.

** Inversión sugerida:**
- Usar BrowserStack para pruebas en múltiples navegadores.
- Aplicar estilos con clases compatibles y responsivas.

---

###  Rendimiento

** Aspectos positivos:**
- Uso de `prefetch_related` para optimizar consultas a la base de datos.
- Lógica eficiente en el carrito para evitar duplicados.

** Aspectos a mejorar:**
- No hay cacheo de vistas ni minificación de recursos estáticos.
- Manejo de stock puede fallar bajo alta concurrencia.

** Inversión sugerida:**
- Implementar cache con Redis o Memcached.
- Migrar imágenes a un CDN y comprimirlas.

---

###  Seguridad

** Aspectos positivos:**
- Uso de CSRF y manejo de sesiones para proteger el carrito.
- Manejo de errores con validaciones de stock y productos.

** Aspectos a mejorar:**
- No hay autenticación para acciones críticas (crear/eliminar productos).
- Falta control de permisos por roles.

** Inversión sugerida:**
- Añadir `@login_required` a vistas sensibles.
- Aplicar gestión de roles con `User.groups` o `django-guardian`.

---


## 3 Aplicación del Principio de Inversión de Dependencias

Se creó la clase `CheckoutService` en `services/checkout_service.py` para encapsular la lógica de compra de productos. 
Esto permite desacoplar la lógica de negocio de las vistas y facilita su reutilización y testeo.

**Antes:** la función `comprar_producto()` contenía directamente la lógica de compra.

**Después:** la vista depende de una clase `CheckoutService`, y delega allí toda la lógica de procesamiento de pedidos.

Esto sigue el principio de inversión de dependencias, ya que:
- La vista depende de una abstracción (el servicio), no de detalles.
- Se mejora la mantenibilidad y extensibilidad del proyecto.



##  Refactor: Inversión de Dependencias en el Checkout

Se ha aplicado el principio **Inversión de Dependencias** en la lógica de compra del proyecto ARTE-SANO, refactorizando dos vistas clave para depender de una clase de servicio externa en lugar de implementar la lógica directamente.

---

###  Objetivo
Separar la lógica de negocio del flujo de compra en una clase desacoplada que pueda reutilizarse, testearse y mantenerse con mayor facilidad.

---

###  Archivos involucrados

#### 1. `services/checkout_service.py` (nuevo archivo)
Contiene la clase `CheckoutService` que encapsula la lógica de:

- Verificación de stock
- Descuento del stock
- Creación de pedidos
- Creación de detalles de pedido
- Cálculo del total

#### 2. `views.py` (modificado)
Se refactorizaron dos vistas:

- `comprar_producto(request)`
- `finalizar_compra(request)`
Ambas ahora delegan la lógica a `CheckoutService`.

---
### Beneficios obtenidos

- La lógica de compra puede ser testeada en aislamiento.
- Se facilita su reutilización en APIs, interfaces móviles, etc.
- Las vistas ahora se centran en recibir solicitudes y devolver respuestas.

---
 Refactor completado siguiendo el principio S.O.L.I.D de **Inversión de Dependencias**.


## 4.
___


## 5. Aplicación de Patrones de Diseño

Este proyecto implementa dos patrones clave de diseño: **CRUD** y **Vistas Basadas en Clases (CBV)**, combinados para la gestión de productos y autenticación en Django.

### Patrón CRUD con CBVs

Se implementa un sistema completo de gestión de productos utilizando el patrón **CRUD** con vistas basadas en clases (CBVs). Las vistas se estructuran de la siguiente forma:

| Acción      | Clase Vista Django           | Descripción |
|-------------|------------------------------|-------------|
| Listar      | `ProductoListView`           | Lista los productos con filtros por categoría y nombre. |
| Crear       | `ProductoCreateView`         | Formulario para crear productos (solo usuarios autenticados). |
| Editar      | `ProductoUpdateView`         | Edición de productos existentes. |
| Eliminar    | `ProductoDeleteView`         | Confirmación y eliminación de un producto. |
| Detalle     | `ProductoDetailView`         | Muestra los detalles de un producto. |

> Todas las vistas CRUD, excepto listar y detalle, están protegidas por `LoginRequiredMixin`.

### Autenticación y Protección de Rutas

Se utilizó `LoginRequiredMixin` para proteger las vistas, asegurando que solo usuarios autenticados puedan acceder a las rutas de creación, edición y eliminación de productos.

Se implementó un sistema de login personalizado con una clase `IniciarSesionView` que gestiona tanto el GET como el POST para el inicio de sesión, y se asegura de redirigir a la página solicitada tras un login exitoso.

#### Rutas de Autenticación y CRUD:
```python
path('productos/', ProductoListView.as_view(), name='lista_productos'),
path('productos/crear/', ProductoCreateView.as_view(), name='crear_producto'),
path('login/', IniciarSesionView.as_view(), name='iniciar_sesion'),
