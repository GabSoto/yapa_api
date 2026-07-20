"""Comando seed: puebla la base de datos con datos de prueba (RNF-DIS-003).

Uso: python manage.py seed
Es idempotente: si ya existe el administrador seed, no hace ningún cambio.
"""

from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.categorias.models import Categoria
from apps.comercios.models import Comercio
from apps.ofertas.models import Oferta
from apps.productos.models import Producto
from apps.usuarios.models import Cliente, Usuario

PASSWORD = 'password123'


class Command(BaseCommand):
    help = 'Puebla la base de datos con datos de prueba del sistema YAPA.'

    def handle(self, *args, **options):
        if Usuario.objects.filter(email='admin@yapa.com').exists():
            self.stdout.write(
                self.style.WARNING('Ya existen datos seed. No se hicieron cambios.')
            )
            return

        with transaction.atomic():
            self._crear_usuarios()
            self._crear_catalogo()

        self.stdout.write(self.style.SUCCESS('Datos seed creados correctamente.'))
        self.stdout.write('  Admin:    admin@yapa.com / admin12345')
        self.stdout.write(f'  Vendedor: vendedor1@yapa.com / {PASSWORD} (y vendedor2@yapa.com)')
        self.stdout.write(f'  Cliente:  cliente1@yapa.com / {PASSWORD} (y cliente2@yapa.com)')

    def _crear_usuarios(self):
        Usuario.objects.create_superuser(
            email='admin@yapa.com', password='admin12345', nombre='Administrador YAPA'
        )

        vendedores = [
            ('vendedor1@yapa.com', 'Rosa', 'Panadería La Espiga', '20100100100',
             'Av. Los Pinos 123, Arequipa'),
            ('vendedor2@yapa.com', 'Mario', 'Bodega El Buen Precio', '20200200200',
             'Calle Mercaderes 456, Arequipa'),
        ]
        self.comercios = []
        for email, nombre, nombre_comercio, ruc, direccion in vendedores:
            usuario = Usuario.objects.create_user(
                email=email, password=PASSWORD, nombre=nombre, rol=Usuario.Rol.VENDEDOR
            )
            self.comercios.append(
                Comercio.objects.create(
                    usuario=usuario,
                    ruc=ruc,
                    nombre_comercio=nombre_comercio,
                    direccion_comercio=direccion,
                    descripcion=f'Comercio de prueba: {nombre_comercio}',
                )
            )

        clientes = [('cliente1@yapa.com', 'Lucía'), ('cliente2@yapa.com', 'Diego')]
        for email, nombre in clientes:
            usuario = Usuario.objects.create_user(
                email=email, password=PASSWORD, nombre=nombre, rol=Usuario.Rol.CLIENTE
            )
            Cliente.objects.create(
                usuario=usuario, direccion_entrega='Urb. Demo 100, Arequipa'
            )

    def _crear_catalogo(self):
        nombres_categorias = ['Panadería', 'Bebidas', 'Lácteos', 'Comida preparada']
        categorias = {
            nombre: Categoria.objects.create(nombre=nombre, descripcion=f'Categoría {nombre}')
            for nombre in nombres_categorias
        }

        comercio1, comercio2 = self.comercios
        productos = [
            (comercio1, categorias['Panadería'], 'Pan integral del día', 'Pan fresco de esta mañana', '4.50', 12),
            (comercio1, categorias['Panadería'], 'Croissant de mantequilla', 'Horneado hoy', '3.00', 8),
            (comercio1, categorias['Comida preparada'], 'Almuerzo ejecutivo', 'Excedente del mediodía', '12.00', 5),
            (comercio1, categorias['Bebidas'], 'Jugo natural 500ml', 'Preparado hoy', '5.00', 6),
            (comercio2, categorias['Lácteos'], 'Yogurt natural 1L', 'Próximo a vencer', '8.00', 10),
            (comercio2, categorias['Lácteos'], 'Queso fresco 500g', 'Producción local', '15.00', 4),
            (comercio2, categorias['Bebidas'], 'Leche evaporada x6', 'Pack próximo a vencer', '18.00', 7),
            (comercio2, categorias['Comida preparada'], 'Porción de arroz con pollo', 'Excedente del día', '7.50', 9),
        ]
        creados = [
            Producto.objects.create(
                comercio=comercio,
                categoria=categoria,
                nombre=nombre,
                descripcion=descripcion,
                precio=precio,
                stock=stock,
            )
            for comercio, categoria, nombre, descripcion, precio, stock in productos
        ]

        hoy = date.today()
        Oferta.objects.create(
            producto=creados[0],
            titulo='Liquidación de fin de día',
            tipo_descuento=Oferta.TipoDescuento.PORCENTAJE,
            valor_descuento=30,
            fecha_inicio=hoy,
            fecha_fin=hoy + timedelta(days=2),
        )
        Oferta.objects.create(
            producto=creados[4],
            titulo='Últimas unidades',
            tipo_descuento=Oferta.TipoDescuento.MONTO_FIJO,
            valor_descuento=2,
            fecha_inicio=hoy,
            fecha_fin=hoy + timedelta(days=1),
        )
