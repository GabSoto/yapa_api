"""Vistas del módulo de carrito de reservas (RF-CAR-001).

Reglas de stock:
- Al agregar un ítem, el stock disponible se descuenta de inmediato.
- Al quitar el ítem o reducir la cantidad, el stock se libera en la misma proporción.
Toda operación de stock usa bloqueo de fila + transacción atómica (RNF-DIS-001).
"""

from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.productos.models import Producto
from core.permisos import EsCliente

from .models import Carrito, CarritoItem
from .serializers import (
    ActualizarItemSerializer,
    AgregarItemSerializer,
    ItemCarritoSerializer,
)


def _cliente(request):
    """Perfil de cliente del usuario autenticado (siempre existe para rol Cliente)."""
    return request.user.cliente


def _error_stock():
    return ValidationError(
        {'detail': 'La cantidad solicitada supera el stock disponible.'}
    )


def _representacion_carrito(carrito):
    """Carrito multi-comercio: ítems agrupados por comercio en la respuesta."""
    items = (
        carrito.items.select_related('producto', 'producto__comercio', 'producto__oferta')
        .all()
        .order_by('id')
    )
    grupos = {}
    for item in items:
        comercio = item.producto.comercio
        grupo = grupos.setdefault(
            comercio.id,
            {
                'comercio': {'id': comercio.id, 'nombre_comercio': comercio.nombre_comercio},
                'items': [],
                'subtotal_comercio': 0,
            },
        )
        datos_item = ItemCarritoSerializer(item).data
        grupo['items'].append(datos_item)
        grupo['subtotal_comercio'] += datos_item['subtotal']

    comercios = list(grupos.values())
    total = sum(grupo['subtotal_comercio'] for grupo in comercios)
    return {'id': carrito.id, 'comercios': comercios, 'total': total}


class CarritoView(APIView):
    """GET /api/v1/carrito/ — carrito activo del cliente."""

    permission_classes = [EsCliente]

    def get(self, request):
        carrito, _ = Carrito.objects.get_or_create(cliente=_cliente(request))
        return Response(_representacion_carrito(carrito))


class CarritoItemsView(APIView):
    """POST /api/v1/carrito/items/ — agregar producto (reserva stock al instante)."""

    permission_classes = [EsCliente]

    def post(self, request):
        serializer = AgregarItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        producto_id = serializer.validated_data['producto_id']
        cantidad = serializer.validated_data['cantidad']

        with transaction.atomic():
            producto = get_object_or_404(
                Producto.objects.select_for_update(), pk=producto_id
            )
            if producto.estado != Producto.Estado.ACTIVO:
                raise ValidationError(
                    {'detail': 'El producto no está disponible.'}
                )
            if producto.stock < cantidad:
                raise _error_stock()
            producto.stock = F('stock') - cantidad
            producto.save(update_fields=['stock'])

            carrito, _ = Carrito.objects.get_or_create(cliente=_cliente(request))
            item = CarritoItem.objects.filter(
                carrito=carrito, producto=producto
            ).first()
            if item is not None:
                item.cantidad = F('cantidad') + cantidad
                item.save(update_fields=['cantidad'])
            else:
                CarritoItem.objects.create(
                    carrito=carrito, producto=producto, cantidad=cantidad
                )

        carrito.refresh_from_db()
        return Response(
            _representacion_carrito(carrito), status=201
        )


class CarritoItemDetalleView(APIView):
    """PATCH y DELETE /api/v1/carrito/items/{id}/ — solo ítems propios."""

    permission_classes = [EsCliente]

    def _item_propio(self, request, pk):
        return get_object_or_404(
            CarritoItem.objects.select_related('producto', 'carrito'),
            pk=pk,
            carrito__cliente__usuario=request.user,
        )

    def patch(self, request, pk):
        item = self._item_propio(request, pk)
        serializer = ActualizarItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        nueva_cantidad = serializer.validated_data['cantidad']

        with transaction.atomic():
            producto = Producto.objects.select_for_update().get(pk=item.producto_id)
            diferencia = nueva_cantidad - item.cantidad
            if diferencia > 0:
                if producto.stock < diferencia:
                    raise _error_stock()
                producto.stock = F('stock') - diferencia
            elif diferencia < 0:
                # Reducir la cantidad libera el stock en la misma proporción
                producto.stock = F('stock') + (-diferencia)
            if diferencia != 0:
                producto.save(update_fields=['stock'])
            item.cantidad = nueva_cantidad
            item.save(update_fields=['cantidad'])

        return Response(_representacion_carrito(item.carrito))

    def delete(self, request, pk):
        item = self._item_propio(request, pk)
        carrito = item.carrito
        with transaction.atomic():
            producto = Producto.objects.select_for_update().get(pk=item.producto_id)
            # Quitar el ítem libera todo el stock reservado
            producto.stock = F('stock') + item.cantidad
            producto.save(update_fields=['stock'])
            item.delete()
        return Response(_representacion_carrito(carrito))
