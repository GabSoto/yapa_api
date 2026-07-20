"""Serializers del módulo de autenticación."""

from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.validators import UniqueValidator

from apps.comercios.models import Comercio
from apps.usuarios.models import Cliente, Usuario

MENSAJE_CREDENCIALES = 'Las credenciales son incorrectas.'
MENSAJE_SUSPENDIDO = (
    'Tu cuenta está suspendida. Contacta al administrador para restablecerla.'
)

validador_telefono = RegexValidator(
    r'^9\d{8}$', 'El teléfono debe iniciar en 9 y tener 9 dígitos.'
)


class LogoutSerializer(serializers.Serializer):
    """RF-AUT-005: refresh token a invalidar."""

    refresh = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    """RF-AUT-001: autenticación por email y contraseña."""

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        usuario = authenticate(
            request=self.context.get('request'),
            username=attrs['email'],
            password=attrs['password'],
        )
        if usuario is None:
            raise AuthenticationFailed(MENSAJE_CREDENCIALES)
        if usuario.estado == Usuario.Estado.SUSPENDIDO:
            raise AuthenticationFailed(MENSAJE_SUSPENDIDO)
        attrs['usuario'] = usuario
        return attrs


class RegistroClienteSerializer(serializers.ModelSerializer):
    """RF-AUT-002: registro público de clientes (rol fijo e inmutable)."""

    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=Usuario.objects.all(),
                message='El correo ya está registrado.',
            )
        ]
    )
    nombre = serializers.CharField(min_length=2)
    password = serializers.CharField(write_only=True, min_length=8)
    apellido = serializers.CharField(required=False, allow_blank=True, default='')
    telefono = serializers.CharField(
        required=False, allow_blank=True, default='', validators=[validador_telefono]
    )

    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'apellido', 'telefono', 'email', 'password']

    def create(self, validated_data):
        with transaction.atomic():
            usuario = Usuario.objects.create_user(
                rol=Usuario.Rol.CLIENTE, **validated_data
            )
            # Perfil de cliente asociado (los datos de entrega se completan en el perfil)
            Cliente.objects.create(usuario=usuario, direccion_entrega='')
        return usuario


class ComercioRegistroSerializer(serializers.Serializer):
    """Datos del comercio dentro del registro de vendedor (RF-AUT-003)."""

    ruc = serializers.CharField(
        validators=[
            RegexValidator(r'^\d{11}$', 'El RUC debe tener exactamente 11 dígitos numéricos.')
        ]
    )
    nombre = serializers.CharField()
    telefono_comercio = serializers.CharField(required=False, allow_blank=True, default='')
    direccion_comercio = serializers.CharField(required=False, allow_blank=True, default='')
    descripcion = serializers.CharField(required=False, allow_blank=True, default='')

    def validate_ruc(self, value):
        if Comercio.objects.filter(ruc=value).exists():
            raise serializers.ValidationError(
                'Ya existe un comercio registrado con ese RUC.', code='unique'
            )
        return value

    def validate_nombre(self, value):
        if Comercio.objects.filter(nombre_comercio=value).exists():
            raise serializers.ValidationError(
                'Ya existe un comercio registrado con ese nombre.', code='unique'
            )
        return value


class RegistroVendedorSerializer(serializers.Serializer):
    """RF-AUT-003: el Administrador da de alta un vendedor con su comercio."""

    nombre = serializers.CharField(min_length=2)
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=Usuario.objects.all(),
                message='El correo ya está registrado.',
            )
        ]
    )
    password = serializers.CharField(write_only=True, min_length=8)
    comercio = ComercioRegistroSerializer()

    def create(self, validated_data):
        datos_comercio = validated_data.pop('comercio')
        # Creación atómica: si falla el comercio se revierte el usuario
        with transaction.atomic():
            vendedor = Usuario.objects.create_user(
                email=validated_data['email'],
                password=validated_data['password'],
                nombre=validated_data['nombre'],
                rol=Usuario.Rol.VENDEDOR,
            )
            comercio = Comercio.objects.create(
                usuario=vendedor,
                ruc=datos_comercio['ruc'],
                nombre_comercio=datos_comercio['nombre'],
                telefono_comercio=datos_comercio['telefono_comercio'],
                direccion_comercio=datos_comercio['direccion_comercio'],
                descripcion=datos_comercio['descripcion'],
            )
        return {'vendedor': vendedor, 'comercio': comercio}
