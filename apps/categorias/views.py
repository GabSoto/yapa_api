"""Vistas del módulo de categorías."""

from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema, extend_schema_view

from core.permisos import EsAdministrador
from core.respuestas import respuesta_exito
from core.serializers import ErrorDetailSerializer, ErrorValidationSerializer

from .models import Categoria
from .serializers import (
    CategoriaActualizarSerializer,
    CategoriaAdminSerializer,
    CategoriaSerializer,
)


@extend_schema(tags=['Categorías'])
class ListaCategoriasView(APIView):
    """RF-CAT-001: GET /api/v1/categorias/ (público; el admin ve todas)."""

    permission_classes = [AllowAny]
    serializer_class = CategoriaSerializer

    def get(self, request):
        usuario = request.user
        es_admin = bool(
            usuario
            and usuario.is_authenticated
            and usuario.rol == usuario.Rol.ADMINISTRADOR
        )
        categorias = Categoria.objects.all().order_by('nombre')
        if not es_admin:
            categorias = categorias.filter(estado=Categoria.Estado.ACTIVO)
        return Response(CategoriaSerializer(categorias, many=True).data)


@extend_schema_view(
    post=extend_schema(
        responses={
            400: ErrorValidationSerializer,
            403: ErrorDetailSerializer,
        }
    ),
)
@extend_schema(tags=['Categorías'])
class CrearCategoriaView(APIView):
    """RF-CAT-002: POST /api/v1/admin/categorias/ (Administrador)."""

    permission_classes = [EsAdministrador]
    serializer_class = CategoriaAdminSerializer

    def post(self, request):
        serializer = CategoriaAdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        categoria = serializer.save()  # estado Activo por defecto
        return respuesta_exito(
            data=CategoriaSerializer(categoria).data,
            message='Categoría registrada correctamente.',
            status=201,
        )


@extend_schema_view(
    patch=extend_schema(
        responses={
            400: ErrorValidationSerializer,
            403: ErrorDetailSerializer,
            404: ErrorDetailSerializer,
        }
    ),
)
@extend_schema(tags=['Categorías'])
class ActualizarCategoriaView(APIView):
    """RF-CAT-003: PATCH /api/v1/admin/categorias/{id}/ (Administrador)."""

    permission_classes = [EsAdministrador]
    serializer_class = CategoriaActualizarSerializer

    def patch(self, request, pk):
        categoria = get_object_or_404(Categoria, pk=pk)
        serializer = CategoriaActualizarSerializer(
            categoria, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        categoria = serializer.save()
        return respuesta_exito(
            data=CategoriaSerializer(categoria).data,
            message='Categoría actualizada correctamente.',
        )
