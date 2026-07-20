"""Modelo de Comercio (relación 1 a 1 con el usuario Vendedor)."""

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


class Comercio(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = 'Activo', 'Activo'
        SUSPENDIDO = 'Suspendido', 'Suspendido'

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comercio'
    )
    ruc = models.CharField(
        max_length=11,
        unique=True,
        validators=[
            RegexValidator(r'^\d{11}$', 'El RUC debe tener exactamente 11 dígitos numéricos.')
        ],
    )
    nombre_comercio = models.CharField(max_length=150, unique=True)
    telefono_comercio = models.CharField(max_length=15, blank=True, default='')
    direccion_comercio = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, default='')
    estado = models.CharField(
        max_length=15, choices=Estado.choices, default=Estado.ACTIVO
    )

    class Meta:
        db_table = 'comercios'

    def __str__(self):
        return f'{self.nombre_comercio} (RUC {self.ruc})'
