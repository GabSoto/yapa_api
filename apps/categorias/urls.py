"""URLs del módulo de categorías."""

from django.urls import path

from .views import ActualizarCategoriaView, CrearCategoriaView, ListaCategoriasView

urlpatterns = [
    # RF-CAT-001 (público)
    path('categorias/', ListaCategoriasView.as_view(), name='categorias-lista'),
    # RF-CAT-002 / RF-CAT-003 (Administrador)
    path('admin/categorias/', CrearCategoriaView.as_view(), name='admin-categorias'),
    path(
        'admin/categorias/<int:pk>/',
        ActualizarCategoriaView.as_view(),
        name='admin-categoria-detalle',
    ),
]
