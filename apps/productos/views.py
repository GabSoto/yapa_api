"""Vistas del módulo de productos."""

import django_filters
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from core.paginacion import PaginacionEstandar
from core.permisos import EsAdministrador, EsVendedor
from core.respuestas import respuesta_exito
from core.serializers import ErrorDetailSerializer, ErrorValidationSerializer
from core.storage import eliminar_imagen, subir_imagen
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view

from .models import Producto
from .serializers import (
    EstadoProductoSerializer,
    ProductoAdminSerializer,
    ProductoEscrituraSerializer,
    ProductoPublicoSerializer,
    ProductoVendedorSerializer,
)


def _queryset_catalogo():
    """Visibilidad pública: producto Activo + comercio Activo + categoría Activa."""
    return (
        Producto.objects.select_related('comercio', 'categoria', 'oferta')
        .filter(
            estado=Producto.Estado.ACTIVO,
            comercio__estado='Activo',
            categoria__estado='Activo',
        )
        .order_by('-fecha_registro')
    )


def _guardar_producto(serializer, comercio, producto=None):
    """Persiste el producto subiendo la imagen al storage si se envió una nueva."""
    archivo = serializer.validated_data.pop('imagen', None)
    if producto is None:
        url = subir_imagen(archivo) if archivo else ''
        return serializer.save(comercio=comercio, imagen=url)
    if archivo:
        eliminar_imagen(producto.imagen)
        producto.imagen = subir_imagen(archivo)  # se persiste con serializer.save()
    producto = serializer.save()
    producto.refresh_from_db()
    return producto


def _producto_propio(request, pk):
    """404 si no existe; 403 si pertenece a otro comercio (RNF-SEG-004)."""
    producto = get_object_or_404(Producto, pk=pk)
    comercio = getattr(request.user, 'comercio', None)
    if comercio is None or producto.comercio_id != comercio.id:
        raise PermissionDenied('No puedes gestionar productos de otro comercio.')
    return producto


class ProductoPublicoFilter(django_filters.FilterSet):
    categoria_id = django_filters.NumberFilter(field_name='categoria_id')
    comercio_id = django_filters.NumberFilter(field_name='comercio_id')
    con_oferta = django_filters.BooleanFilter(method='filtrar_con_oferta')

    def filtrar_con_oferta(self, queryset, name, value):
        hoy = timezone.localdate()
        vigente = Q(
            oferta__estado='Activo',
            oferta__fecha_inicio__lte=hoy,
            oferta__fecha_fin__gte=hoy,
        )
        return queryset.filter(vigente) if value else queryset.exclude(vigente)


@extend_schema(tags=['Productos'])
@extend_schema_view(
    get=extend_schema(
        responses={200: ProductoPublicoSerializer(many=True)},
        parameters=[
            OpenApiParameter('categoria_id', int),
            OpenApiParameter('comercio_id', int),
            OpenApiParameter('con_oferta', bool),
        ],
    ),
    post=extend_schema(
        request=ProductoEscrituraSerializer,
        responses={
            201: ProductoVendedorSerializer,
            400: ErrorValidationSerializer,
            403: ErrorDetailSerializer,
        },
    ),
)
class ProductosView(APIView):
    """RF-PRO-001 (GET, público) y RF-PRO-004 (POST, vendedor)."""

    serializer_class = ProductoPublicoSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [EsVendedor()]
        return [AllowAny()]

    def get(self, request):
        queryset = ProductoPublicoFilter(
            request.query_params, queryset=_queryset_catalogo()
        ).qs
        paginador = PaginacionEstandar()
        pagina = paginador.paginate_queryset(queryset, request)
        serializer = ProductoPublicoSerializer(pagina, many=True)
        return paginador.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ProductoEscrituraSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        producto = _guardar_producto(serializer, comercio=request.user.comercio)
        return respuesta_exito(
            data=ProductoVendedorSerializer(producto).data,
            message='Producto registrado correctamente.',
            status=201,
        )


@extend_schema(tags=['Productos'])
@extend_schema_view(
    get=extend_schema(
        responses={200: ProductoPublicoSerializer, 404: ErrorDetailSerializer}
    ),
    patch=extend_schema(
        request=ProductoEscrituraSerializer,
        responses={
            200: ProductoVendedorSerializer,
            400: ErrorValidationSerializer,
            403: ErrorDetailSerializer,
            404: ErrorDetailSerializer,
        },
    ),
    delete=extend_schema(
        responses={
            200: None,
            403: ErrorDetailSerializer,
            404: ErrorDetailSerializer,
        }
    ),
)
class ProductoDetalleView(APIView):
    """RF-PRO-002 (GET, público) y RF-PRO-005/006 (PATCH/DELETE, vendedor)."""

    serializer_class = ProductoPublicoSerializer

    def get_permissions(self):
        if self.request.method in ('PATCH', 'PUT', 'DELETE'):
            return [EsVendedor()]
        return [AllowAny()]

    def get(self, request, pk):
        producto = get_object_or_404(_queryset_catalogo(), pk=pk)
        return respuesta_exito(data=ProductoPublicoSerializer(producto).data)

    def patch(self, request, pk):
        producto = _producto_propio(request, pk)
        serializer = ProductoEscrituraSerializer(producto, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        producto = _guardar_producto(serializer, producto.comercio, producto)
        return respuesta_exito(
            data=ProductoVendedorSerializer(producto).data,
            message='Producto actualizado correctamente.',
        )

    def delete(self, request, pk):
        producto = _producto_propio(request, pk)
        # Eliminación lógica: se preserva el historial de reservas asociadas
        producto.estado = Producto.Estado.INACTIVO
        producto.save(update_fields=['estado', 'fecha_actualizacion'])
        return respuesta_exito(message='Producto desactivado correctamente.')


@extend_schema_view(
    get=extend_schema(
        responses={200: ProductoVendedorSerializer(many=True), 403: ErrorDetailSerializer}
    ),
)
@extend_schema(tags=['Productos'])
class MisProductosView(ListAPIView):
    """RF-PRO-003: GET /api/v1/productos/mis-productos/ (Vendedor)."""

    permission_classes = [EsVendedor]
    serializer_class = ProductoVendedorSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Producto.objects.none()
        return (
            Producto.objects.select_related('categoria', 'oferta')
            .filter(comercio=self.request.user.comercio)
            .order_by('-fecha_registro')
        )


@extend_schema_view(
    get=extend_schema(
        responses={200: ProductoAdminSerializer(many=True), 403: ErrorDetailSerializer}
    ),
)
@extend_schema(tags=['Productos'])
class ListaProductosAdminView(ListAPIView):
    """RF-PRO-007: GET /api/v1/admin/productos/ (Administrador)."""

    permission_classes = [EsAdministrador]
    serializer_class = ProductoAdminSerializer
    filterset_fields = ['comercio_id', 'categoria_id', 'estado']

    def get_queryset(self):
        return Producto.objects.select_related('comercio', 'categoria').all().order_by('id')


@extend_schema_view(
    patch=extend_schema(
        request=EstadoProductoSerializer,
        responses={
            200: None,
            400: ErrorValidationSerializer,
            403: ErrorDetailSerializer,
            404: ErrorDetailSerializer,
        },
    ),
)
@extend_schema(tags=['Productos'])
class CambiarEstadoProductoAdminView(APIView):
    """RF-PRO-007: PATCH /api/v1/admin/productos/{id}/estado/ (moderación)."""

    permission_classes = [EsAdministrador]
    serializer_class = EstadoProductoSerializer

    def patch(self, request, pk):
        producto = get_object_or_404(Producto, pk=pk)
        serializer = EstadoProductoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        producto.estado = serializer.validated_data['estado']
        producto.save(update_fields=['estado', 'fecha_actualizacion'])
        return respuesta_exito(
            data={'id': producto.id, 'estado': producto.estado},
            message='Estado del producto actualizado correctamente.',
        )
