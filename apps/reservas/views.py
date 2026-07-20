"""Vistas del módulo de reservas (RF-RES-001 a RF-RES-005)."""

from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.carrito.models import Carrito
from apps.carrito.serializers import precio_vigente
from apps.productos.models import Producto
from core.paginacion import PaginacionEstandar
from core.permisos import EsCliente, EsVendedor
from core.respuestas import respuesta_exito

from .models import Reserva, ReservaItem
from .serializers import ConfirmarReservaSerializer, ReservaSerializer


def _queryset_reservas():
    return Reserva.objects.select_related(
        'comercio', 'cliente__usuario'
    ).prefetch_related('items__producto__oferta')


class ReservasView(APIView):
    """RF-RES-001 (POST) y RF-RES-002 (GET, filtro opcional por estado)."""

    permission_classes = [EsCliente]

    def get(self, request):
        queryset = _queryset_reservas().filter(cliente=request.user.cliente)
        estado = request.query_params.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        paginador = PaginacionEstandar()
        pagina = paginador.paginate_queryset(queryset, request)
        serializer = ReservaSerializer(pagina, many=True)
        return paginador.get_paginated_response(serializer.data)

    def post(self, request):
        cliente = request.user.cliente

        with transaction.atomic():
            carrito, _ = Carrito.objects.get_or_create(cliente=cliente)
            items = list(
                carrito.items.select_related(
                    'producto', 'producto__comercio', 'producto__oferta'
                ).all()
            )
            if not items:
                raise ValidationError({'detail': 'El carrito está vacío.'})

            # Revalidar que los productos sigan Activos (el stock ya se reservó en el carrito)
            for item in items:
                if item.producto.estado != Producto.Estado.ACTIVO:
                    raise ValidationError(
                        {'detail': f'El producto "{item.producto.nombre}" ya no está disponible.'}
                    )

            # Una reserva por comercio, todas en estado Pendiente
            grupos = {}
            for item in items:
                grupos.setdefault(item.producto.comercio_id, []).append(item)

            reservas = []
            for comercio_id, grupo in grupos.items():
                reserva = Reserva.objects.create(cliente=cliente, comercio_id=comercio_id)
                for item in grupo:
                    ReservaItem.objects.create(
                        reserva=reserva,
                        producto=item.producto,
                        cantidad=item.cantidad,
                        precio_unitario=precio_vigente(item.producto),
                    )
                reservas.append(reserva)

            # Vaciado del carrito tras crear las reservas
            carrito.items.all().delete()

        serializer = ReservaSerializer(
            _queryset_reservas().filter(pk__in=[r.pk for r in reservas]), many=True
        )
        return respuesta_exito(
            data=serializer.data,
            message='Reserva(s) creada(s) correctamente.',
            status=201,
        )


class ReservasVendedorView(ListAPIView):
    """RF-RES-003: GET /api/v1/vendedor/reservas/ (Vendedor)."""

    permission_classes = [EsVendedor]
    serializer_class = ReservaSerializer

    def get_queryset(self):
        return _queryset_reservas().filter(comercio=self.request.user.comercio)


class EstadoReservaVendedorView(APIView):
    """RF-RES-004: PATCH /api/v1/vendedor/reservas/{id}/estado/ (Confirmar)."""

    permission_classes = [EsVendedor]

    def patch(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk)
        if reserva.comercio_id != request.user.comercio.id:
            raise PermissionDenied('No puedes gestionar reservas de otro comercio.')

        serializer = ConfirmarReservaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if reserva.estado != Reserva.Estado.PENDIENTE:
            raise ValidationError(
                {'detail': 'Solo se pueden confirmar reservas en estado Pendiente.'}
            )
        reserva.estado = Reserva.Estado.CONFIRMADA
        reserva.save(update_fields=['estado', 'fecha_actualizacion'])
        return respuesta_exito(
            data={'id': reserva.id, 'estado': reserva.estado},
            message='Reserva confirmada correctamente.',
        )


class CancelarReservaView(APIView):
    """RF-RES-005: PATCH /api/v1/reservas/{id}/cancelar/ (Cliente o Vendedor)."""

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk)
        usuario = request.user

        if usuario.rol == usuario.Rol.CLIENTE:
            if reserva.cliente_id != usuario.cliente.id:
                raise PermissionDenied('No puedes cancelar reservas de otro cliente.')
        elif usuario.rol == usuario.Rol.VENDEDOR:
            if reserva.comercio_id != usuario.comercio.id:
                raise PermissionDenied('No puedes cancelar reservas de otro comercio.')
        else:
            raise PermissionDenied('No tiene permisos para cancelar reservas.')

        if reserva.estado != Reserva.Estado.PENDIENTE:
            raise ValidationError(
                {'detail': 'Solo se pueden cancelar reservas en estado Pendiente.'}
            )

        # Cancelar devuelve el stock reservado al producto
        with transaction.atomic():
            reserva.estado = Reserva.Estado.CANCELADA
            reserva.save(update_fields=['estado', 'fecha_actualizacion'])
            for item in reserva.items.all():
                producto = Producto.objects.select_for_update().get(pk=item.producto_id)
                producto.stock = F('stock') + item.cantidad
                producto.save(update_fields=['stock'])

        return respuesta_exito(
            data={'id': reserva.id, 'estado': reserva.estado},
            message='Reserva cancelada correctamente.',
        )
