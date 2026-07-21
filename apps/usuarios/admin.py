from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.usuarios.models import Cliente, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('email', 'nombre', 'apellido', 'rol', 'estado', 'is_staff', 'fecha_registro')
    list_filter = ('rol', 'estado', 'is_staff', 'is_superuser')
    search_fields = ('email', 'nombre', 'apellido')
    ordering = ('-fecha_registro',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('nombre', 'apellido', 'telefono')}),
        ('Roles y permisos', {'fields': ('rol', 'estado', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas', {'fields': ('fecha_registro',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'apellido', 'password1', 'password2'),
        }),
    )
    readonly_fields = ('fecha_registro',)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'direccion_entrega', 'referencia')
    search_fields = ('usuario__email', 'usuario__nombre', 'direccion_entrega')
    raw_id_fields = ('usuario',)
