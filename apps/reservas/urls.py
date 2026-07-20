"""URLs del módulo de reservas."""

from django.urls import path

from .views import (
    CancelarReservaView,
    EstadoReservaVendedorView,
    ReservasVendedorView,
    ReservasView,
)

urlpatterns = [
    # RF-RES-001 / RF-RES-002 (Cliente)
    path('reservas/', ReservasView.as_view(), name='reservas'),
    # RF-RES-005 (Cliente o Vendedor)
    path('reservas/<int:pk>/cancelar/', CancelarReservaView.as_view(), name='reserva-cancelar'),
    # RF-RES-003 / RF-RES-004 (Vendedor)
    path('vendedor/reservas/', ReservasVendedorView.as_view(), name='vendedor-reservas'),
    path(
        'vendedor/reservas/<int:pk>/estado/',
        EstadoReservaVendedorView.as_view(),
        name='vendedor-reserva-estado',
    ),
]
