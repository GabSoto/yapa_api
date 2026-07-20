"""Serializers del módulo de productos."""

from rest_framework import serializers

from apps.categorias.models import Categoria
from apps.comercios.models import Comercio
from apps.ofertas.models import Oferta

from .models import Producto


class ComercioResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comercio
        fields = ['id', 'nombre_comercio']


class CategoriaResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']


class OfertaResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Oferta
        fields = [
            'titulo',
            'tipo_descuento',
            'valor_descuento',
            'fecha_inicio',
            'fecha_fin',
        ]


class ProductoPublicoSerializer(serializers.ModelSerializer):
    """Catálogo público: incluye la oferta solo si está vigente (RF-PRO-001)."""

    comercio = ComercioResumenSerializer(read_only=True)
    categoria = CategoriaResumenSerializer(read_only=True)
    oferta = serializers.SerializerMethodField()
    precio_final = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'descripcion',
            'precio',
            'precio_final',
            'stock',
            'imagen',
            'comercio',
            'categoria',
            'oferta',
        ]

    def _oferta_vigente(self, obj):
        oferta = getattr(obj, 'oferta', None)
        return oferta if oferta and oferta.esta_vigente() else None

    def get_oferta(self, obj):
        oferta = self._oferta_vigente(obj)
        return OfertaResumenSerializer(oferta).data if oferta else None

    def get_precio_final(self, obj):
        oferta = self._oferta_vigente(obj)
        return oferta.calcular_precio_final() if oferta else obj.precio


class ProductoVendedorSerializer(serializers.ModelSerializer):
    """Productos del propio comercio: todos los estados y la oferta completa."""

    categoria = CategoriaResumenSerializer(read_only=True)
    oferta = OfertaResumenSerializer(read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'descripcion',
            'precio',
            'stock',
            'imagen',
            'estado',
            'fecha_registro',
            'fecha_actualizacion',
            'categoria',
            'oferta',
        ]


class ProductoEscrituraSerializer(serializers.ModelSerializer):
    """Registro/actualización de productos por el vendedor (RF-PRO-004/005)."""

    imagen = serializers.ImageField(required=False)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.filter(estado=Categoria.Estado.ACTIVO),
        source='categoria',
        error_messages={
            'does_not_exist': 'La categoría no existe o no está Activa.',
            'incorrect_type': 'La categoría indicada no es válida.',
        },
    )

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'precio', 'stock', 'categoria_id', 'imagen']


class EstadoProductoSerializer(serializers.Serializer):
    """Entrada para la moderación de estado (Activo/Inactivo)."""

    estado = serializers.ChoiceField(choices=Producto.Estado.choices)


class ProductoAdminSerializer(serializers.ModelSerializer):
    """Listado de moderación del administrador (RF-PRO-007)."""

    comercio = ComercioResumenSerializer(read_only=True)
    categoria = CategoriaResumenSerializer(read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id',
            'nombre',
            'descripcion',
            'precio',
            'stock',
            'imagen',
            'estado',
            'fecha_registro',
            'comercio',
            'categoria',
        ]
