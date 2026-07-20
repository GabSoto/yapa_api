"""Serializers del módulo de categorías."""

from rest_framework import serializers

from .models import Categoria


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'estado']
        read_only_fields = ['estado']


class CategoriaAdminSerializer(serializers.ModelSerializer):
    """Creación/actualización por el administrador (nombre único en el modelo)."""

    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'estado']
        extra_kwargs = {
            'estado': {'read_only': True},
        }


class CategoriaActualizarSerializer(serializers.ModelSerializer):
    """Actualización parcial: nombre, descripcion y estado."""

    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'estado']
        extra_kwargs = {
            'nombre': {'required': False},
            'descripcion': {'required': False},
            'estado': {'required': False},
        }
