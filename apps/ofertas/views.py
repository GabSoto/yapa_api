"""Vistas del módulo de ofertas."""

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.productos.models import Producto
from drf_spectacular.utils import extend_schema, extend_schema_view

from core.permisos import EsVendedor
from core.respuestas import respuesta_exito
from core.serializers import ErrorDetailSerializer, ErrorValidationSerializer

from .serializers import OfertaSerializer


@extend_schema(tags=['Ofertas'])
@extend_schema_view(
    post=extend_schema(
        request=OfertaSerializer,
        responses={
            201: OfertaSerializer,
            400: ErrorValidationSerializer,
            403: ErrorDetailSerializer,
            404: ErrorDetailSerializer,
            409: ErrorDetailSerializer,
        },
    ),
    patch=extend_schema(
        request=OfertaSerializer,
        responses={
            200: OfertaSerializer,
            400: ErrorValidationSerializer,
            403: ErrorDetailSerializer,
            404: ErrorDetailSerializer,
        },
    ),
)
class OfertaView(APIView):
    """RF-DES-001: POST y PATCH /api/v1/productos/{producto_id}/oferta/"""

    permission_classes = [EsVendedor]
    serializer_class = OfertaSerializer

    def _producto_propio(self, request, producto_id):
        producto = get_object_or_404(Producto, pk=producto_id)
        comercio = getattr(request.user, 'comercio', None)
        if comercio is None or producto.comercio_id != comercio.id:
            raise PermissionDenied('No puedes gestionar ofertas de otro comercio.')
        return producto

    def post(self, request, producto_id):
        producto = self._producto_propio(request, producto_id)
        if hasattr(producto, 'oferta'):
            return Response(
                {'detail': 'El producto ya tiene una oferta. Usa PATCH para modificarla.'},
                status=409,
            )
        serializer = OfertaSerializer(data=request.data, context={'producto': producto})
        serializer.is_valid(raise_exception=True)
        oferta = serializer.save(producto=producto)
        return respuesta_exito(
            data=OfertaSerializer(oferta).data,
            message='Oferta creada correctamente.',
            status=201,
        )

    def patch(self, request, producto_id):
        producto = self._producto_propio(request, producto_id)
        oferta = getattr(producto, 'oferta', None)
        if oferta is None:
            raise NotFound('El producto no tiene una oferta registrada.')
        serializer = OfertaSerializer(
            oferta, data=request.data, partial=True, context={'producto': producto}
        )
        serializer.is_valid(raise_exception=True)
        oferta = serializer.save()
        return respuesta_exito(
            data=OfertaSerializer(oferta).data,
            message='Oferta actualizada correctamente.',
        )
