from django.contrib import admin

from apps.productos.models import Producto


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'comercio', 'categoria', 'precio', 'stock', 'estado', 'fecha_registro')
    list_filter = ('estado', 'categoria', 'comercio')
    search_fields = ('nombre', 'descripcion', 'comercio__nombre_comercio', 'categoria__nombre')
    ordering = ('-fecha_registro',)
    readonly_fields = ('fecha_registro', 'fecha_actualizacion')
    raw_id_fields = ('comercio', 'categoria')
