"""Serializers del módulo de carrito de reservas."""

from rest_framework import serializers

from apps.productos.models import Producto

from .models import CarritoItem


def precio_vigente(producto):
    """Precio final del producto considerando su oferta vigente (si aplica)."""
    oferta = getattr(producto, 'oferta', None)
    if oferta and oferta.esta_vigente():
        return oferta.calcular_precio_final()
    return producto.precio


class ProductoCarritoSerializer(serializers.ModelSerializer):
    precio_final = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'imagen', 'precio', 'precio_final']

    def get_precio_final(self, obj):
        return precio_vigente(obj)


class ItemCarritoSerializer(serializers.ModelSerializer):
    producto = ProductoCarritoSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CarritoItem
        fields = ['id', 'producto', 'cantidad', 'subtotal']

    def get_subtotal(self, obj):
        return precio_vigente(obj.producto) * obj.cantidad


class AgregarItemSerializer(serializers.Serializer):
    """Entrada para agregar un ítem al carrito (RF-CAR-001)."""

    producto_id = serializers.IntegerField()
    cantidad = serializers.IntegerField(
        min_value=1, error_messages={'min_value': 'La cantidad debe ser mayor a 0.'}
    )


class ActualizarItemSerializer(serializers.Serializer):
    """Entrada para modificar la cantidad de un ítem del carrito."""

    cantidad = serializers.IntegerField(
        min_value=1, error_messages={'min_value': 'La cantidad debe ser mayor a 0.'}
    )
