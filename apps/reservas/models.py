"""Modelos de Reserva y sus ítems (precio congelado al reservar)."""

from django.core.validators import MinValueValidator
from django.db import models


class Reserva(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'Pendiente', 'Pendiente'
        CONFIRMADA = 'Confirmada', 'Confirmada'
        CANCELADA = 'Cancelada', 'Cancelada'

    cliente = models.ForeignKey(
        'usuarios.Cliente', on_delete=models.PROTECT, related_name='reservas'
    )
    comercio = models.ForeignKey(
        'comercios.Comercio', on_delete=models.PROTECT, related_name='reservas'
    )
    estado = models.CharField(
        max_length=15, choices=Estado.choices, default=Estado.PENDIENTE
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reservas'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'Reserva #{self.pk} - {self.comercio.nombre_comercio} ({self.estado})'


class ReservaItem(models.Model):
    reserva = models.ForeignKey(
        Reserva, on_delete=models.CASCADE, related_name='items'
    )
    producto = models.ForeignKey(
        'productos.Producto', on_delete=models.PROTECT, related_name='items_reserva'
    )
    cantidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1, 'La cantidad debe ser mayor a 0.')]
    )
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'reserva_items'

    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre} (Reserva #{self.reserva_id})'
