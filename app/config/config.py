from asyncio.log import logger
from dotenv import load_dotenv
from pathlib import Path
import os


# Mismos conceptos que en cache_config, los utilizamos par cargar
# las variables del .env
basedir = os.path.abspath(Path(__file__).parents[2])
load_dotenv(os.path.join(basedir, '.env'))

class Config(object): # Clase base que define configuraciones comunes para todos los entornos
    TESTING = False
    
    @staticmethod
    def init_app(app):
        pass

class TestConfig(Config): # define configuraciones especificas para el contexto de test.
    TESTING = True
    DEBUG = True
    CACHE_REDIS_HOST = os.environ.get('REDIS_HOST')
    CACHE_REDIS_PORT = os.environ.get('REDIS_PORT')
    CACHE_REDIS_DB = os.environ.get('REDIS_DB')
    CACHE_REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')

class DevelopmentConfig(Config): # Define configuraciones especificas para el contexto de development
    TESTING = True
    DEBUG = True

class ProductionConfig(Config): # define configuraciones especificas para el contexto de produccion
    DEBUG = False
    TESTING = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

def factory(app): # devuelve la configuracion adecuada segun el contexto de la aplicación.
    configuration = {
        'testing': TestConfig,
        'development': DevelopmentConfig,
        'production': ProductionConfig
    }
    
    return configuration[app];