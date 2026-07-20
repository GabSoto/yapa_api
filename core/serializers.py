"""Serializers compartidos del núcleo."""

from rest_framework import serializers


class CambiarEstadoSerializer(serializers.Serializer):
    """Entrada para los endpoints de cambio de estado (Activo/Suspendido)."""

    estado = serializers.ChoiceField(choices=['Activo', 'Suspendido'])
