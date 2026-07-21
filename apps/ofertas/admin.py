from django.contrib import admin

from apps.ofertas.models import Oferta


@admin.register(Oferta)
class OfertaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'producto', 'tipo_descuento', 'valor_descuento', 'fecha_inicio', 'fecha_fin', 'estado')
    list_filter = ('estado', 'tipo_descuento', 'fecha_inicio')
    search_fields = ('titulo', 'producto__nombre')
    ordering = ('-fecha_inicio',)
    raw_id_fields = ('producto',)
