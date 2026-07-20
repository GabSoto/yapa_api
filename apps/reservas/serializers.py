"""Serializers del módulo de reservas."""

from rest_framework import serializers

from apps.carrito.serializers import ProductoCarritoSerializer
from apps.comercios.models import Comercio
from apps.usuarios.models import Usuario

from .models import Reserva, ReservaItem


class ReservaItemSerializer(serializers.ModelSerializer):
    producto = ProductoCarritoSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = ReservaItem
        fields = ['id', 'producto', 'cantidad', 'precio_unitario', 'subtotal']

    def get_subtotal(self, obj):
        return obj.precio_unitario * obj.cantidad


class ComercioReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comercio
        fields = ['id', 'nombre_comercio', 'direccion_comercio']


class ClienteReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'email']


class ReservaSerializer(serializers.ModelSerializer):
    items = ReservaItemSerializer(many=True, read_only=True)
    comercio = ComercioReservaSerializer(read_only=True)
    cliente = ClienteReservaSerializer(source='cliente.usuario', read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Reserva
        fields = [
            'id',
            'estado',
            'fecha_creacion',
            'fecha_actualizacion',
            'comercio',
            'cliente',
            'items',
            'total',
        ]

    def get_total(self, obj):
        return sum(item.precio_unitario * item.cantidad for item in obj.items.all())


class ConfirmarReservaSerializer(serializers.Serializer):
    """Entrada para confirmar una reserva (única transición permitida)."""

    estado = serializers.ChoiceField(choices=[Reserva.Estado.CONFIRMADA])
