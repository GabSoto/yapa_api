"""Serializers del módulo de ofertas."""

from rest_framework import serializers

from .models import Oferta


class OfertaSerializer(serializers.ModelSerializer):
    """Creación/actualización de la oferta de un producto (RF-DES-001)."""

    class Meta:
        model = Oferta
        fields = [
            'id',
            'titulo',
            'descripcion',
            'tipo_descuento',
            'valor_descuento',
            'fecha_inicio',
            'fecha_fin',
            'estado',
        ]
        extra_kwargs = {
            'descripcion': {'required': False, 'allow_blank': True},
            'estado': {'required': False},
        }

    def validate(self, attrs):
        instancia = self.instance

        def valor_actual(campo):
            return attrs.get(campo, getattr(instancia, campo, None) if instancia else None)

        inicio = valor_actual('fecha_inicio')
        fin = valor_actual('fecha_fin')
        if inicio and fin and fin <= inicio:
            raise serializers.ValidationError(
                {'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'}
            )

        tipo = valor_actual('tipo_descuento')
        valor = valor_actual('valor_descuento')
        producto = self.context['producto']
        if valor is not None:
            if tipo == Oferta.TipoDescuento.PORCENTAJE and not (1 <= valor <= 100):
                raise serializers.ValidationError(
                    {'valor_descuento': 'Para Porcentaje, el valor debe estar entre 1 y 100.'}
                )
            if tipo == Oferta.TipoDescuento.MONTO_FIJO and valor >= producto.precio:
                raise serializers.ValidationError(
                    {'valor_descuento': 'Para Monto fijo, el valor debe ser menor que el precio del producto.'}
                )
        return attrs
