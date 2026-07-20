"""Serializers compartidos del núcleo."""

from rest_framework import serializers


class CambiarEstadoSerializer(serializers.Serializer):
    """Entrada para los endpoints de cambio de estado (Activo/Suspendido)."""

    estado = serializers.ChoiceField(choices=['Activo', 'Suspendido'])


class EmptySerializer(serializers.Serializer):
    """Marcador para endpoints sin cuerpo de solicitud (documentación OpenAPI)."""

    pass


class ErrorDetailSerializer(serializers.Serializer):
    """Respuesta de error con un mensaje descriptivo (401, 403, 404, 409, 500)."""

    detail = serializers.CharField()


class ErrorValidationSerializer(serializers.Serializer):
    """Error de validación (400): mensaje general + errores por campo."""

    detail = serializers.CharField(default='Los datos enviados no son válidos.')
    errors = serializers.DictField(
        child=serializers.ListField(child=serializers.CharField()),
        required=False,
    )
