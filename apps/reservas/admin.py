from django.contrib import admin

from apps.reservas.models import Reserva, ReservaItem


class ReservaItemInline(admin.TabularInline):
    model = ReservaItem
    extra = 0
    readonly_fields = ('precio_unitario',)
    raw_id_fields = ('producto',)


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'comercio', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('cliente__usuario__email', 'comercio__nombre_comercio')
    ordering = ('-fecha_creacion',)
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    raw_id_fields = ('cliente', 'comercio')
    inlines = (ReservaItemInline,)


@admin.register(ReservaItem)
class ReservaItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'reserva', 'producto', 'cantidad', 'precio_unitario')
    search_fields = ('reserva__id', 'producto__nombre')
    raw_id_fields = ('reserva', 'producto')
