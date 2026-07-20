"""URLs del módulo de carrito."""

from django.urls import path

from .views import CarritoItemDetalleView, CarritoItemsView, CarritoView

urlpatterns = [
    # RF-CAR-001 (Cliente)
    path('carrito/', CarritoView.as_view(), name='carrito'),
    path('carrito/items/', CarritoItemsView.as_view(), name='carrito-items'),
    path(
        'carrito/items/<int:pk>/',
        CarritoItemDetalleView.as_view(),
        name='carrito-item-detalle',
    ),
]
