from flask import Flask, request
from flask_caching import Cache
from flask_marshmallow import Marshmallow
import os
from app.config import config
from app.config.cache_config import cache_config
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis


ma = Marshmallow() # creamos una instancia de la extension marshmallow
"""
 es útil para convertir datos en formatos como JSON. También permite validar y estructurar datos fácilmente.
"""

cache = Cache() # creamos una instancia de la extension flask_caching
"""
 Flask-Caching es una extensión para implementar un sistema de cacheo, lo que puede acelerar las respuestas de la API y reducir la carga en recursos externos como bases de datos.
"""
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = os.getenv("REDIS_PORT", "6379")
redis_password = os.getenv("REDIS_PASSWORD", "Qvv3r7y")

# Configurar Flask-Limiter con Redis y autenticación
limiter = Limiter(
    key_func=lambda: request.headers.get("X-Forwarded-For", request.remote_addr),
    storage_uri=f"redis://:{redis_password}@{redis_host}:{redis_port}/0",
    default_limits=["3600 per minute"]
)


def create_app() -> Flask: # Se crea una funcion la cual devuelve un objeto de tipo flask
    """
     en lugar de crear una instancia de flask directamente en el archivo principal
     se encapsula la creacion y configuracion de la aplicacion dentro de uan función. 
     Esto permite un mayor control sobre el proceso de configuracion y facilita la creación
     de multiples instancias de la aplicacion con diferentes configuraciones.
    """
    
    app_context = os.getenv('FLASK_CONTEXT') # Indicamos en que contexto se está ejecutando la aplicación
    app = Flask(__name__) # Creamos una instancia de flask
    """
     a través de esta instancia se configuran rutas, extensiones y middleware.
    """
    f = config.factory(app_context if app_context else 'development') # se crea una variable para obtener el contexto de la aplicacion
    app.config.from_object(f) # carga la configuracion de la variable f (el contexto) en la aplicacion de flask.
    
    print(f"Running in {cache_config} mode") # Imprime un mensaje en la consola indicando el modo de configuracion del sistema de caché.
    ma.init_app(app) # Inicializa marshmallow con la instancia de la aplicacion de flask
    cache.init_app(app, config=cache_config) # Inicializa flask-chaching con la instancia de la aplicacion de flask y configura el cache segun cache_config
    limiter.init_app(app)  # Inicializa el limitador en la aplicación
    
    from app.resources import home # Llamamos a todas las rutas
    """
     Tener las rutas en diferentes modulos, mejora la legibilidad y mantenibilidad del código.
    """
    
    app.register_blueprint(home, url_prefix='/api/v1') #registramos un blueprint llamado home, bajo el prefijo de URL /api/v1
    """
     Al definir un prefijo /api/v1 significa que todas las rutas definidas en home estarán disponibles con el prefijo /api/v1.
     Los blueprints son útiles para modularizar la aplicación, especialmente en aplicaciones grandes con muchas rutas.
    """
    
    @app.shell_context_processor # declara un decorador para definir el contexto adicional para el shell interactivo de flask.
    def ctx(): # esta funcion devuelve un diccionario que contiene la instancia de la aplcicación.
        return {"app": app}
    """
     este patron facilita el acceso a objetos como app directamente desde la shell de flask para depuracion o pruebas.
     Permite trabaajar con la aplicacion desde el shell interactivo sin tener q importarla manualmente.
    """
    return app
