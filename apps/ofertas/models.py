"""Modelo de Oferta (descuento 1 a 1 sobre un producto)."""

from django.db import models


class Oferta(models.Model):
    class TipoDescuento(models.TextChoices):
        PORCENTAJE = 'Porcentaje', 'Porcentaje'
        MONTO_FIJO = 'Monto fijo', 'Monto fijo'

    class Estado(models.TextChoices):
        ACTIVO = 'Activo', 'Activo'
        INACTIVO = 'Inactivo', 'Inactivo'

    producto = models.OneToOneField(
        'productos.Producto', on_delete=models.CASCADE, related_name='oferta'
    )
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, default='')
    tipo_descuento = models.CharField(max_length=15, choices=TipoDescuento.choices)
    valor_descuento = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(
        max_length=10, choices=Estado.choices, default=Estado.ACTIVO
    )

    class Meta:
        db_table = 'ofertas'

    def __str__(self):
        return f'Oferta de {self.producto.nombre}: {self.titulo}'

    def esta_vigente(self, hoy=None):
        """Una oferta es vigente si está Activa y hoy está dentro del rango."""
        from django.utils import timezone

        hoy = hoy or timezone.localdate()
        return (
            self.estado == self.Estado.ACTIVO
            and self.fecha_inicio <= hoy <= self.fecha_fin
        )

    def calcular_precio_final(self):
        """Precio final calculado al momento de servir el producto (no se persiste)."""
        from decimal import ROUND_HALF_UP, Decimal

        precio = self.producto.precio
        if self.tipo_descuento == self.TipoDescuento.PORCENTAJE:
            final = precio - (precio * self.valor_descuento / 100)
        else:
            final = precio - self.valor_descuento
        return final.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
