"""Modelos de usuarios: Usuario (autenticación) y Cliente (perfil)."""

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio.')
        email = self.normalize_email(email)
        usuario = self.model(email=email, **extra_fields)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('rol', Usuario.Rol.ADMINISTRADOR)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Usuario del sistema. El login se realiza con email (no username)."""

    class Rol(models.TextChoices):
        ADMINISTRADOR = 'Administrador', 'Administrador'
        VENDEDOR = 'Vendedor', 'Vendedor'
        CLIENTE = 'Cliente', 'Cliente'

    class Estado(models.TextChoices):
        ACTIVO = 'Activo', 'Activo'
        INACTIVO = 'Inactivo', 'Inactivo'
        SUSPENDIDO = 'Suspendido', 'Suspendido'

    email = models.EmailField('correo electrónico', unique=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100, blank=True, default='')
    telefono = models.CharField(max_length=9, blank=True, default='')
    rol = models.CharField(max_length=15, choices=Rol.choices)
    estado = models.CharField(
        max_length=15, choices=Estado.choices, default=Estado.ACTIVO
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre']

    class Meta:
        db_table = 'usuarios'

    def __str__(self):
        return f'{self.email} ({self.rol})'


class Cliente(models.Model):
    """Perfil complementario de los usuarios con rol Cliente (relación 1 a 1)."""

    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name='cliente'
    )
    direccion_entrega = models.CharField(max_length=255)
    referencia = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        db_table = 'clientes'

    def __str__(self):
        return f'Cliente: {self.usuario.email}'
