"""Vistas del módulo de comercios (Administrador)."""

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

from core.permisos import EsAdministrador
from core.respuestas import respuesta_exito
from core.serializers import CambiarEstadoSerializer

from .models import Comercio
from .serializers import ComercioAdminSerializer


class ListaComerciosView(ListAPIView):
    """RF-COM-001: GET /api/v1/admin/comercios/ (filtro: estado)."""

    permission_classes = [EsAdministrador]
    serializer_class = ComercioAdminSerializer
    queryset = Comercio.objects.select_related('usuario').all().order_by('id')
    filterset_fields = ['estado']


class CambiarEstadoComercioView(APIView):
    """RF-COM-002: PATCH /api/v1/admin/comercios/{id}/estado/"""

    permission_classes = [EsAdministrador]

    def patch(self, request, pk):
        comercio = get_object_or_404(Comercio, pk=pk)
        serializer = CambiarEstadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        estado = serializer.validated_data['estado']

        # Sincronización con la cuenta del vendedor asociado
        with transaction.atomic():
            comercio.estado = estado
            comercio.save(update_fields=['estado'])
            comercio.usuario.estado = estado
            comercio.usuario.save(update_fields=['estado'])

        return respuesta_exito(
            data={'id': comercio.id, 'estado': comercio.estado},
            message='Estado del comercio actualizado correctamente.',
        )
