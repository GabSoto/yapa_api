"""Vistas del módulo de usuarios."""

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.permisos import EsAdministrador
from core.respuestas import respuesta_exito
from core.serializers import CambiarEstadoSerializer, ErrorDetailSerializer, ErrorValidationSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Usuario
from .serializers import (
    ActualizarPerfilSerializer,
    PerfilUsuarioSerializer,
    UsuarioAdminSerializer,
)


@extend_schema(tags=['Usuarios'])
@extend_schema_view(
    get=extend_schema(
        responses={200: PerfilUsuarioSerializer, 401: ErrorDetailSerializer}
    ),
    put=extend_schema(
        request=ActualizarPerfilSerializer,
        responses={200: PerfilUsuarioSerializer, 400: ErrorValidationSerializer, 401: ErrorDetailSerializer},
    ),
    patch=extend_schema(
        request=ActualizarPerfilSerializer,
        responses={200: PerfilUsuarioSerializer, 400: ErrorValidationSerializer, 401: ErrorDetailSerializer},
    ),
)
class PerfilView(APIView):
    """RF-USU-001 / RF-USU-002: GET, PUT y PATCH /api/v1/usuarios/perfil/"""

    permission_classes = [IsAuthenticated]
    serializer_class = PerfilUsuarioSerializer

    def get(self, request):
        return respuesta_exito(data=PerfilUsuarioSerializer(request.user).data)

    def put(self, request):
        return self._actualizar(request, partial=False)

    def patch(self, request):
        return self._actualizar(request, partial=True)

    def _actualizar(self, request, partial):
        serializer = ActualizarPerfilSerializer(
            request.user, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()
        return respuesta_exito(
            data=PerfilUsuarioSerializer(usuario).data,
            message='Perfil actualizado correctamente.',
        )


@extend_schema_view(
    get=extend_schema(responses={200: UsuarioAdminSerializer(many=True), 403: ErrorDetailSerializer}),
)
@extend_schema(tags=['Usuarios'])
class ListaUsuariosView(ListAPIView):
    """RF-USU-003: GET /api/v1/admin/usuarios/ (filtros: rol, estado)."""

    permission_classes = [EsAdministrador]
    serializer_class = UsuarioAdminSerializer
    queryset = Usuario.objects.all().order_by('id')
    filterset_fields = ['rol', 'estado']


@extend_schema_view(
    patch=extend_schema(
        request=CambiarEstadoSerializer,
        responses={200: None, 400: ErrorValidationSerializer, 403: ErrorDetailSerializer, 404: ErrorDetailSerializer},
    ),
)
@extend_schema(tags=['Usuarios'])
class CambiarEstadoUsuarioView(APIView):
    """RF-USU-004: PATCH /api/v1/admin/usuarios/{id}/estado/"""

    permission_classes = [EsAdministrador]
    serializer_class = CambiarEstadoSerializer

    def patch(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        serializer = CambiarEstadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        estado = serializer.validated_data['estado']

        # Sincronización con el comercio si el usuario es Vendedor
        with transaction.atomic():
            usuario.estado = estado
            usuario.save(update_fields=['estado'])
            comercio = getattr(usuario, 'comercio', None)
            if usuario.rol == Usuario.Rol.VENDEDOR and comercio is not None:
                comercio.estado = estado
                comercio.save(update_fields=['estado'])

        return respuesta_exito(
            data={'id': usuario.id, 'estado': usuario.estado},
            message='Estado de la cuenta actualizado correctamente.',
        )
