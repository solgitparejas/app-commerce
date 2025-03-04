# Archivo mscatalogo_service.py con retry
import os
import logging
import requests
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from app.models import Producto
from app.mapping import ProductoSchema

producto_schema = ProductoSchema()

class ClienteCatalogoService:

    def __init__(self):
        self.URL = os.getenv('MSCATALOGO_URL', 'http://localhost:5001/api/v1/')

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(requests.exceptions.RequestException))
    # stop_after_attempt(3): Reintenta un máximo de 3 veces
    # wait_fixed(2): Espera 2 segundos entre cada intento
    # retry_if_exception_type: Solo reintenta en excepciones de red
    def obtener_producto(self, id: int) -> Producto:
        # Validación antes de la solicitud HTTP
        if not id or id <= 0:
            logging.error(f"ID inválido recibido: {id}")
            raise ValueError("El ID del producto debe ser un número positivo y válido")
    
        try:
            response = requests.get(
                f'{self.URL}catalogo/productos/{id}',
                timeout=5  # Timeout de 5 segundos
            )
            
            if response.status_code == 200:
                logging.info(f"Producto obtenido con éxito: {response.json()}")
                return producto_schema.load(response.json())
            elif response.status_code == 404:
                logging.error(f"Producto no encontrado, ID: {id}")
                raise ValueError(f"Producto con ID {id} no encontrado en el catálogo.")
            else:
                logging.error(f"Error al obtener el producto, código de estado: {response.status_code}")
                raise BaseException(f"Fallo al obtener producto con ID {id}, código: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Excepción durante la solicitud al servicio de catálogo: {e}")
            raise
