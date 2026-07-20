"""Modelos del carrito de reservas (multi-comercio, uno activo por cliente)."""

from django.core.validators import MinValueValidator
from django.db import models


class Carrito(models.Model):
    cliente = models.OneToOneField(
        'usuarios.Cliente', on_delete=models.CASCADE, related_name='carrito'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'carritos'

    def __str__(self):
        return f'Carrito de {self.cliente.usuario.email}'


class CarritoItem(models.Model):
    carrito = models.ForeignKey(
        Carrito, on_delete=models.CASCADE, related_name='items'
    )
    producto = models.ForeignKey(
        'productos.Producto', on_delete=models.CASCADE, related_name='items_carrito'
    )
    cantidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1, 'La cantidad debe ser mayor a 0.')]
    )

    class Meta:
        db_table = 'carrito_items'
        constraints = [
            models.UniqueConstraint(
                fields=['carrito', 'producto'], name='item_unico_por_carrito'
            )
        ]

    def __str__(self):
        return f'{self.cantidad} x {self.producto.nombre}'
