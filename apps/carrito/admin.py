from django.contrib import admin

from apps.carrito.models import Carrito, CarritoItem


class CarritoItemInline(admin.TabularInline):
    model = CarritoItem
    extra = 0
    raw_id_fields = ('producto',)


@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'fecha_creacion')
    search_fields = ('cliente__usuario__email',)
    ordering = ('-fecha_creacion',)
    readonly_fields = ('fecha_creacion',)
    raw_id_fields = ('cliente',)
    inlines = (CarritoItemInline,)


@admin.register(CarritoItem)
class CarritoItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'carrito', 'producto', 'cantidad')
    search_fields = ('carrito__cliente__usuario__email', 'producto__nombre')
    raw_id_fields = ('carrito', 'producto')
