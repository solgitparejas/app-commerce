from dotenv import load_dotenv
from pathlib import Path
import os

basedir = os.path.abspath(Path(__file__).parents[2]) # define la ubicacion base del proyecto ( dos directorios arriba del archivo actual)
"""
 este basedir nos sirve para acceder al archivo .env y cargarlo
"""
load_dotenv(os.path.join(basedir, '.env')) # carga las variables de entorno desde el a rchivo .env ubicado en basedir
cache_config= { 'CACHE_TYPE': 'RedisCache', 'CACHE_DEFAULT_TIMEOUT': 300, 'CACHE_REDIS_HOST': os.environ.get('REDIS_HOST'),    'CACHE_REDIS_PORT': os.environ.get('REDIS_PORT'), 'CACHE_REDIS_DB': os.environ.get('REDIS_DB'), 'CACHE_REDIS_PASSWORD': os.environ.get('REDIS_PASSWORD'),     'CACHE_KEY_PREFIX': 'flask_' }
# cache_config es un diccionario que contiene la configuración para el sistema de caché.
"""
CACHE_TYPE: Especifica el tipo de caché, en este caso RedisCache.
CACHE_DEFAULT_TIMEOUT: El tiempo (en segundos) que un elemento permanece en caché (300 = 5 minutos).
CACHE_REDIS_*: Detalles de conexión al servidor Redis, como el host, puerto, base de datos y contraseña.
CACHE_KEY_PREFIX: Prefijo para las claves de los datos almacenados en Redis, útil para evitar colisiones con otros sistemas.
"""