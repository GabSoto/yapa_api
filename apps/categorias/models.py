"""Modelo de Categoría para clasificar productos."""

from django.db import models


class Categoria(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = 'Activo', 'Activo'
        INACTIVO = 'Inactivo', 'Inactivo'

    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=255, blank=True, default='')
    estado = models.CharField(
        max_length=10, choices=Estado.choices, default=Estado.ACTIVO
    )

    class Meta:
        db_table = 'categorias'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre
