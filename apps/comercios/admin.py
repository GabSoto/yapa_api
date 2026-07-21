from django.contrib import admin

from apps.comercios.models import Comercio


@admin.register(Comercio)
class ComercioAdmin(admin.ModelAdmin):
    list_display = ('nombre_comercio', 'ruc', 'usuario', 'telefono_comercio', 'estado')
    list_filter = ('estado',)
    search_fields = ('nombre_comercio', 'ruc', 'usuario__email', 'direccion_comercio')
    raw_id_fields = ('usuario',)
