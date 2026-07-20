"""URLs raíz del proyecto YAPA API (RNF-MAN-003: versión en la ruta /api/v1/)."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Documentación de la API (RNF-MAN-002)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Módulos de la API
    path('api/v1/', include('apps.autenticacion.urls')),
    path('api/v1/', include('apps.usuarios.urls')),
    path('api/v1/', include('apps.comercios.urls')),
    path('api/v1/', include('apps.categorias.urls')),
    path('api/v1/', include('apps.productos.urls')),
    path('api/v1/', include('apps.ofertas.urls')),
    path('api/v1/', include('apps.carrito.urls')),
    path('api/v1/', include('apps.reservas.urls')),
]

# En desarrollo local se sirven las imágenes desde MEDIA (fallback de Storage)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
