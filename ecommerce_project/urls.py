from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from app.views import HomeView, RegistroView, IniciarSesionView, CerrarSesionView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),

    # Autenticación
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', IniciarSesionView.as_view(), name='iniciar_sesion'),
    path('logout/', CerrarSesionView.as_view(), name='cerrar_sesion'),

    # Rutas del app
    path('', include('app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
