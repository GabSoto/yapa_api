"""
Manejo uniforme de errores de la API (RNF-USA-002, RNF-USA-003, RNF-DIS-002).

- Errores controlados: estructura {"detail": "..."}; los errores de validación
  agregan además {"errors": {"campo": ["mensaje", ...]}}.
- Errores no controlados: código 500 con mensaje genérico, sin exponer trazas.
"""

import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def manejador_excepciones(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        # Error no controlado: log interno y respuesta genérica
        logger.exception("Error no controlado", exc_info=exc)
        return Response(
            {'detail': 'Error interno del servidor.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    data = response.data
    if isinstance(data, dict) and 'detail' not in data:
        # Errores de validación de serializers: {"campo": ["mensaje"]}
        response.data = {
            'detail': 'Los datos enviados no son válidos.',
            'errors': data,
        }

    return response
