"""URLs del módulo de productos."""

from django.urls import path

from .views import (
    CambiarEstadoProductoAdminView,
    ListaProductosAdminView,
    MisProductosView,
    ProductoDetalleView,
    ProductosView,
)

urlpatterns = [
    # RF-PRO-001 (público) / RF-PRO-004 (vendedor)
    path('productos/', ProductosView.as_view(), name='productos'),
    # RF-PRO-003 (vendedor) — antes de <int:pk> por claridad
    path('productos/mis-productos/', MisProductosView.as_view(), name='mis-productos'),
    # RF-PRO-002 (público) / RF-PRO-005 / RF-PRO-006 (vendedor)
    path('productos/<int:pk>/', ProductoDetalleView.as_view(), name='producto-detalle'),
    # RF-PRO-007 (Administrador)
    path('admin/productos/', ListaProductosAdminView.as_view(), name='admin-productos'),
    path(
        'admin/productos/<int:pk>/estado/',
        CambiarEstadoProductoAdminView.as_view(),
        name='admin-producto-estado',
    ),
]
