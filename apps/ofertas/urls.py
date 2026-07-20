"""URLs del módulo de ofertas."""

from django.urls import path

from .views import OfertaView

urlpatterns = [
    # RF-DES-001 (Vendedor)
    path('productos/<int:producto_id>/oferta/', OfertaView.as_view(), name='producto-oferta'),
]
