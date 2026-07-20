"""
Configuración del proyecto YAPA API.

Los valores sensibles se leen desde variables de entorno (archivo .env en
desarrollo). Funciona con SQLite en local y PostgreSQL/Supabase en despliegue
sin cambios en el código (RNF-POR-001): basta definir DB_ENGINE=postgresql.
"""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')


def lista_env(nombre, por_defecto=''):
    """Lee una variable de entorno con valores separados por coma."""
    valor = os.environ.get(nombre, por_defecto)
    return [v.strip() for v in valor.split(',') if v.strip()]


# --- Seguridad ---
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = lista_env('ALLOWED_HOSTS', '127.0.0.1,localhost')


# --- Aplicaciones ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Terceros
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'corsheaders',
    'drf_spectacular',
    # Propias
    'core',
    'apps.usuarios',
    'apps.comercios',
    'apps.categorias',
    'apps.productos',
    'apps.ofertas',
    'apps.carrito',
    'apps.reservas',
    'apps.autenticacion',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# --- Base de datos: SQLite por defecto, PostgreSQL si DB_ENGINE=postgresql ---
if os.environ.get('DB_ENGINE') == 'postgresql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'postgres'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', ''),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'CONN_MAX_AGE': 0,
        }
    }
    # En producción con Vercel, confiar en headers HTTPS del proxy
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True') == 'True'
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# --- Hashing de contraseñas: BCrypt (RNF-SEG-001) ---
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'usuarios.Usuario'


# --- Django REST Framework ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'core.paginacion.PaginacionEstandar',
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'core.excepciones.manejador_excepciones',
    # Decimales como números JSON (15.00 -> 15.0), no como cadenas
    'COERCE_DECIMAL_TO_STRING': False,
}

# --- JWT (RF-AUT-004: rotación y lista negra de refresh tokens) ---
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

def hook_excluir_rutas_duplicadas(endpoints):
    """Excluye del esquema OpenAPI las variantes duplicadas con slash final."""
    return [
        endpoint
        for endpoint in endpoints
        if not (
            endpoint[0].endswith('/auth/login/')
            or endpoint[0].endswith('/auth/register/')
        )
    ]


# --- Documentación de la API (RNF-MAN-002) ---
SPECTACULAR_SETTINGS = {
    'TITLE': 'YAPA API',
    'DESCRIPTION': 'API REST de YAPA: reducción del desperdicio de alimentos mediante reservas de excedentes.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'PREPROCESSING_HOOKS': ['config.settings.hook_excluir_rutas_duplicadas'],
    'ENUM_NAME_OVERRIDES': {
        'EstadoUsuario': 'apps.usuarios.models.Usuario.Estado',
        'EstadoProductoEnum': 'apps.productos.models.Producto.Estado',
        'EstadoReserva': 'apps.reservas.models.Reserva.Estado',
        'EstadoComercio': 'apps.comercios.models.Comercio.Estado',
    },
    'TAGS': [
        {'name': 'Autenticación', 'description': 'Operaciones de inicio de sesión, registro y gestión de tokens.'},
        {'name': 'Usuarios', 'description': 'Gestión de perfiles y administración de cuentas de usuarios.'},
        {'name': 'Comercios', 'description': 'Administración de comercios por parte del administrador.'},
        {'name': 'Categorías', 'description': 'Categorías de productos disponibles en el catálogo.'},
        {'name': 'Productos', 'description': 'Catálogo público de productos y gestión para vendedores y administradores.'},
        {'name': 'Ofertas', 'description': 'Descuentos y ofertas aplicados a productos individuales.'},
        {'name': 'Carrito', 'description': 'Carrito de compras multi-comercio con reserva inmediata de stock.'},
        {'name': 'Reservas', 'description': 'Reservas de productos, confirmación por el vendedor y cancelación.'},
    ],
}

# --- CORS ---
_origenes = lista_env('CORS_ALLOWED_ORIGINS', 'http://localhost:3000')
if '*' in _origenes:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOWED_ORIGINS = []
else:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = _origenes


# --- Internacionalización ---
LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True


# --- Archivos estáticos y media (fallback local de imágenes en desarrollo) ---
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --- Supabase Storage (vacío en desarrollo -> se usa MEDIA local) ---
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')
SUPABASE_BUCKET = os.environ.get('SUPABASE_BUCKET', 'productos')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
