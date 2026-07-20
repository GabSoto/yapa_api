"""Modelo de Producto del catálogo."""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Producto(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = 'Activo', 'Activo'
        INACTIVO = 'Inactivo', 'Inactivo'

    comercio = models.ForeignKey(
        'comercios.Comercio', on_delete=models.CASCADE, related_name='productos'
    )
    categoria = models.ForeignKey(
        'categorias.Categoria', on_delete=models.PROTECT, related_name='productos'
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, default='')
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'), 'El precio debe ser mayor que 0.')],
    )
    stock = models.PositiveIntegerField(default=0)
    imagen = models.URLField(max_length=500, blank=True, default='')
    estado = models.CharField(
        max_length=10, choices=Estado.choices, default=Estado.ACTIVO
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'productos'

    def __str__(self):
        return f'{self.nombre} ({self.comercio.nombre_comercio})'
