"""Vistas del módulo de categorías."""

from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permisos import EsAdministrador
from core.respuestas import respuesta_exito

from .models import Categoria
from .serializers import (
    CategoriaActualizarSerializer,
    CategoriaAdminSerializer,
    CategoriaSerializer,
)


class ListaCategoriasView(APIView):
    """RF-CAT-001: GET /api/v1/categorias/ (público; el admin ve todas)."""

    permission_classes = [AllowAny]

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


class CrearCategoriaView(APIView):
    """RF-CAT-002: POST /api/v1/admin/categorias/ (Administrador)."""

    permission_classes = [EsAdministrador]

    def post(self, request):
        serializer = CategoriaAdminSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        categoria = serializer.save()  # estado Activo por defecto
        return respuesta_exito(
            data=CategoriaSerializer(categoria).data,
            message='Categoría registrada correctamente.',
            status=201,
        )


class ActualizarCategoriaView(APIView):
    """RF-CAT-003: PATCH /api/v1/admin/categorias/{id}/ (Administrador)."""

    permission_classes = [EsAdministrador]

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
