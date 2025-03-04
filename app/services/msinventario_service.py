# Archivo msinventario_service.py con retry
import os
import logging
import requests
from app import cache
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from app.mapping import StockSchema
from app.models import Stock
from app.models.carrito import Carrito

class ClienteInventarioService:

    def __init__(self):
        self.stock = Stock()
        self.URL = os.getenv('MSINVENTARIOS_URL', 'http://localhost:5004/api/v1/')
        # Suponiendo que el cache es Redis o alguna herramienta similar
        self.cache = cache  # Esto debe ser un objeto de caché configurado previamente

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(requests.exceptions.RequestException))
    def retirar_producto(self, carrito: Carrito) -> None:
        # Retira un producto del inventario, basado en el carrito de compras, con lógica de reintentos

        if not carrito or not carrito.producto or not carrito.producto.id or carrito.cantidad <= 0:
            raise ValueError("El carrito debe tener un producto válido y una cantidad mayor a 0")

        self.stock.producto = carrito.producto.id
        self.stock.cantidad = carrito.cantidad
        self.stock.entrada_salida = 2  # 2 indica una salida de inventario
        stock_schema = StockSchema()

        try:
            response = requests.post(
                f"{self.URL}inventarios/retirar",
                json=stock_schema.dump(self.stock),
                timeout=5  # Timeout de 5 segundos
            )

            if response.status_code == 200:
                logging.info(f"Stock actualizado con éxito: {response.json()}")
                self.stock = stock_schema.load(response.json())

                # Aquí actualizas el caché
                # Elimina el caché de este producto, ya que el stock ha cambiado
                self.cache.delete(f'stock_{carrito.producto.id}')  # Elimina el caché antiguo

                # Luego actualiza el caché con el nuevo valor de stock
                self.cache.set(f'stock_{carrito.producto.id}', self.stock, timeout=60)  # Actualiza el caché

            else:
                logging.error(f"Error al retirar producto del inventario, código de estado: {response.status_code}")
                raise BaseException("Fallo en la operación de retiro de producto en el inventario")
        
        except requests.exceptions.RequestException as e:
            logging.error(f"Excepción durante la solicitud al servicio de inventarios: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(requests.exceptions.RequestException))
    def ingresar_producto(self) -> None:
    # Ingresa un producto al inventario, con lógica de reintentos
    
        if not self.stock.id:
            raise ValueError("No se puede ingresar stock sin un ID válido")

        self.stock.entrada_salida = 1  # 1 indica una entrada de inventario
        stock_schema = StockSchema()

        try:
            response = requests.post(
                f"{self.URL}inventarios/ingresar/{self.stock.id}",
                json=stock_schema.dump(self.stock),
                timeout=5  # Timeout de 5 segundos
            )

            if response.status_code == 200:
                logging.info(f"Stock ingresado con éxito, ID: {self.stock.id}")
            else:
                logging.error(f"Error al ingresar producto al inventario, código de estado: {response.status_code}")
                raise BaseException("Fallo en la operación de ingreso de producto en el inventario")
        except requests.exceptions.RequestException as e:
            logging.error(f"Excepción durante la solicitud al servicio de inventarios: {e}")
            raise