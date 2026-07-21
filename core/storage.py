"""Servicio de almacenamiento de imágenes de productos (RNF-ESC-001).

- Desarrollo local (sin credenciales de Supabase): guarda en MEDIA local y
  devuelve la URL relativa servida por Django.
- Despliegue (SUPABASE_URL y SUPABASE_KEY configuradas): sube al bucket
  público de Supabase Storage y devuelve la URL pública.
"""

import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage


def _nombre_unico(nombre_original):
    extension = Path(nombre_original).suffix.lower() or '.jpg'
    return f'productos/{uuid.uuid4().hex}{extension}'


def _supabase_configurado():
    return bool(settings.SUPABASE_URL and settings.SUPABASE_KEY)


def subir_imagen(archivo):
    """Sube el archivo y devuelve la URL pública resultante."""
    nombre = _nombre_unico(archivo.name)
    if _supabase_configurado():
        from supabase import create_client

        cliente = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        bucket = cliente.storage.from_(settings.SUPABASE_BUCKET)
        bucket.upload(nombre, archivo.read(), {'content-type': archivo.content_type})
        return bucket.get_public_url(nombre)
    ruta = default_storage.save(nombre, archivo)
    return f'{settings.MEDIA_URL}{ruta}'


def eliminar_imagen(url):
    """Elimina la imagen anterior al reemplazarla."""
    if not url:
        return
    try:
        if _supabase_configurado() and settings.SUPABASE_URL in url:
            from supabase import create_client

            cliente = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            nombre = url.split(f'/{settings.SUPABASE_BUCKET}/')[-1]
            cliente.storage.from_(settings.SUPABASE_BUCKET).remove([nombre])
        elif url.startswith(settings.MEDIA_URL):
            ruta = url[len(settings.MEDIA_URL):]
            if default_storage.exists(ruta):
                default_storage.delete(ruta)
    except Exception:
        pass
