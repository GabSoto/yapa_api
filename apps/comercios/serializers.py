"""Serializers del módulo de comercios."""

from rest_framework import serializers

from apps.usuarios.models import Usuario

from .models import Comercio


class VendedorBasicoSerializer(serializers.ModelSerializer):
    """Información básica (no sensible) del vendedor asociado."""

    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'email']


class ComercioAdminSerializer(serializers.ModelSerializer):
    """RF-COM-001: comercio con la información básica de su vendedor."""

    vendedor = VendedorBasicoSerializer(source='usuario', read_only=True)

    class Meta:
        model = Comercio
        fields = [
            'id',
            'ruc',
            'nombre_comercio',
            'telefono_comercio',
            'direccion_comercio',
            'descripcion',
            'estado',
            'vendedor',
        ]
