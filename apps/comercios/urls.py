"""URLs del módulo de comercios."""

from django.urls import path

from .views import CambiarEstadoComercioView, ListaComerciosView

urlpatterns = [
    # RF-COM-001 / RF-COM-002 (Administrador)
    path('admin/comercios/', ListaComerciosView.as_view(), name='admin-comercios'),
    path(
        'admin/comercios/<int:pk>/estado/',
        CambiarEstadoComercioView.as_view(),
        name='admin-comercio-estado',
    ),
]
