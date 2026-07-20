"""Serializers del módulo de usuarios."""

from django.db import transaction
from rest_framework import serializers

from apps.autenticacion.serializers import validador_telefono
from apps.comercios.models import Comercio
from apps.usuarios.models import Cliente, Usuario


class ClientePerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['direccion_entrega', 'referencia']


class ComercioPerfilSerializer(serializers.ModelSerializer):
    """Datos del comercio en la respuesta del perfil (ruc y estado protegidos)."""

    class Meta:
        model = Comercio
        fields = [
            'ruc',
            'nombre_comercio',
            'telefono_comercio',
            'direccion_comercio',
            'descripcion',
            'estado',
        ]


class ComercioActualizarSerializer(serializers.ModelSerializer):
    """Campos editables del comercio por el propio vendedor (sin RUC ni estado)."""

    class Meta:
        model = Comercio
        fields = [
            'nombre_comercio',
            'telefono_comercio',
            'direccion_comercio',
            'descripcion',
        ]


class PerfilUsuarioSerializer(serializers.ModelSerializer):
    """RF-USU-001: estructura de respuesta según el rol del usuario."""

    cliente = ClientePerfilSerializer(read_only=True)
    comercio = ComercioPerfilSerializer(read_only=True)

    class Meta:
        model = Usuario
        fields = [
            'id',
            'email',
            'rol',
            'nombre',
            'apellido',
            'telefono',
            'estado',
            'cliente',
            'comercio',
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.rol != Usuario.Rol.CLIENTE:
            data.pop('cliente', None)
        if instance.rol != Usuario.Rol.VENDEDOR:
            data.pop('comercio', None)
        return data


class ActualizarPerfilSerializer(serializers.Serializer):
    """RF-USU-002: actualización del perfil propio (campos protegidos excluidos)."""

    nombre = serializers.CharField(min_length=2, required=False)
    apellido = serializers.CharField(required=False, allow_blank=True)
    telefono = serializers.CharField(
        required=False, allow_blank=True, validators=[validador_telefono]
    )
    cliente = ClientePerfilSerializer(required=False)
    comercio = ComercioActualizarSerializer(required=False)

    def update(self, instance, validated_data):
        datos_cliente = validated_data.pop('cliente', None)
        datos_comercio = validated_data.pop('comercio', None)

        # Actualización atómica: si algo falla no se guarda ningún cambio parcial
        with transaction.atomic():
            for atributo, valor in validated_data.items():
                setattr(instance, atributo, valor)
            instance.save()

            if datos_cliente is not None and hasattr(instance, 'cliente'):
                for atributo, valor in datos_cliente.items():
                    setattr(instance.cliente, atributo, valor)
                instance.cliente.save()

            if datos_comercio is not None and hasattr(instance, 'comercio'):
                for atributo, valor in datos_comercio.items():
                    setattr(instance.comercio, atributo, valor)
                instance.comercio.save()

        return instance


class UsuarioAdminSerializer(serializers.ModelSerializer):
    """RF-USU-003: información básica de usuarios para el administrador."""

    class Meta:
        model = Usuario
        fields = [
            'id',
            'email',
            'nombre',
            'apellido',
            'telefono',
            'rol',
            'estado',
            'fecha_registro',
        ]
