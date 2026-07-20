"""Helpers para respuestas uniformes de la API (RNF-USA-003)."""

from rest_framework.response import Response


def respuesta_exito(data=None, message=None, status=200):
    """Construye una respuesta de éxito con estructura consistente."""
    payload = {}
    if message is not None:
        payload['message'] = message
    if data is not None:
        payload['data'] = data
    return Response(payload, status=status)
