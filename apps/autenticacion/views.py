"""Vistas del módulo de autenticación."""

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from drf_spectacular.utils import extend_schema, extend_schema_view

from core.jwt import TokenConRolSerializer
from core.permisos import EsAdministrador
from core.serializers import ErrorDetailSerializer, ErrorValidationSerializer

from .serializers import (
    LoginSerializer,
    LogoutSerializer,
    RegistroClienteSerializer,
    RegistroVendedorSerializer,
)


def _error_de_unicidad(exc, campo, anidado=None):
    """Detecta si un ValidationError proviene de una regla de unicidad."""
    errores = exc.detail
    if anidado is not None:
        errores = errores.get(anidado, {})
        if not isinstance(errores, dict):
            return False
    mensajes = errores.get(campo, [])
    return any(getattr(m, 'code', '') == 'unique' for m in mensajes)


def _tokens_de_usuario(usuario):
    refresh = TokenConRolSerializer.get_token(usuario)
    return str(refresh.access_token), str(refresh)


def _datos_user(usuario):
    return {
        'id': usuario.id,
        'email': usuario.email,
        'nombre': usuario.nombre,
        'rol': usuario.rol,
    }


@extend_schema_view(
    post=extend_schema(
        responses={
            200: LoginSerializer,
            400: ErrorValidationSerializer,
            401: ErrorDetailSerializer,
        }
    ),
)
@extend_schema(tags=['Autenticación'])
class LoginView(APIView):
    """RF-AUT-001: POST /api/v1/auth/login"""

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        usuario = serializer.validated_data['usuario']
        access, refresh = _tokens_de_usuario(usuario)
        return Response(
            {'access': access, 'refresh': refresh, 'user': _datos_user(usuario)},
            status=status.HTTP_200_OK,
        )


@extend_schema_view(
    post=extend_schema(
        responses={
            201: RegistroClienteSerializer,
            400: ErrorValidationSerializer,
            409: ErrorDetailSerializer,
        }
    ),
)
@extend_schema(tags=['Autenticación'])
class RegistroClienteView(APIView):
    """RF-AUT-002: POST /api/v1/auth/register"""

    permission_classes = [AllowAny]
    serializer_class = RegistroClienteSerializer

    def post(self, request):
        serializer = RegistroClienteSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exc:
            if _error_de_unicidad(exc, 'email'):
                return Response(
                    {'detail': 'El correo ya está registrado.'},
                    status=status.HTTP_409_CONFLICT,
                )
            raise
        usuario = serializer.save()
        access, refresh = _tokens_de_usuario(usuario)
        return Response(
            {'access': access, 'refresh': refresh, 'user': _datos_user(usuario)},
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    post=extend_schema(
        responses={
            201: RegistroVendedorSerializer,
            400: ErrorValidationSerializer,
            403: ErrorDetailSerializer,
            409: ErrorDetailSerializer,
        }
    ),
)
@extend_schema(tags=['Autenticación'])
class RegistroVendedorView(APIView):
    """RF-AUT-003: POST /api/v1/admin/vendedores/ (solo Administrador)."""

    permission_classes = [EsAdministrador]
    serializer_class = RegistroVendedorSerializer

    def post(self, request):
        serializer = RegistroVendedorSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as exc:
            if _error_de_unicidad(exc, 'email'):
                return Response(
                    {'detail': 'El correo ya está registrado.'},
                    status=status.HTTP_409_CONFLICT,
                )
            if _error_de_unicidad(exc, 'ruc', anidado='comercio'):
                return Response(
                    {'detail': 'Ya existe un comercio registrado con ese RUC.'},
                    status=status.HTTP_409_CONFLICT,
                )
            raise
        resultado = serializer.save()
        vendedor, comercio = resultado['vendedor'], resultado['comercio']
        return Response(
            {
                'vendedor': {
                    'id': vendedor.id,
                    'email': vendedor.email,
                    'rol': vendedor.rol,
                },
                'comercio': {
                    'id': comercio.id,
                    'ruc': comercio.ruc,
                    'vendedor_id': vendedor.id,
                },
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    post=extend_schema(
        responses={
            200: None,
            401: ErrorDetailSerializer,
        }
    ),
)
@extend_schema(tags=['Autenticación'])
class RenovacionTokenView(TokenRefreshView):
    """RF-AUT-004: POST /api/v1/auth/refresh/ (mensajes de error en español)."""

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except (TokenError, InvalidToken):
            return Response(
                {'detail': 'El token de actualización es inválido, ya expiró o ya fue utilizado.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )


@extend_schema_view(
    post=extend_schema(
        responses={
            200: ErrorDetailSerializer,
            400: ErrorValidationSerializer,
            401: ErrorDetailSerializer,
        }
    ),
)
@extend_schema(tags=['Autenticación'])
class LogoutView(APIView):
    """RF-AUT-005: POST /api/v1/auth/logout/ (invalida el refresh token)."""

    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            RefreshToken(serializer.validated_data['refresh']).blacklist()
        except TokenError:
            return Response(
                {'detail': 'El token es inválido, ya expiró o ya fue utilizado.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(
            {'detail': 'Cierre de sesión exitoso. El token ha sido invalidado.'},
            status=status.HTTP_200_OK,
        )
