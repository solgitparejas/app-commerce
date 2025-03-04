# Archivo mscompras_service.py con retry
import os
import logging
import requests
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from app.mapping import CompraSchema
from app.models import Compra, Producto

class ClienteComprasService:

    def __init__(self):
        self.compra = Compra()
        self.URL = os.getenv('MSCOMPRAS_URL', 'http://localhost:5002/api/v1/')

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(requests.exceptions.RequestException))
    def comprar(self, producto: Producto, direccion_envio: str) -> None:
    # registra una compra de un cliente basado en un producto, con lógica de reintentos
    
        if not producto or not producto.id:
            raise ValueError("El producto debe tener un ID válido")
        if not direccion_envio:
            raise ValueError("La dirección de envío no puede estar vacía")

        self.compra.producto = producto.id
        self.compra.direccion_envio = direccion_envio
        compra_schema = CompraSchema()

        try:
            response = requests.post(
                f"{self.URL}compras",
                json=compra_schema.dump(self.compra),
                timeout=5  # Timeout de 5 segundos para evitar bloqueos prolongados
            )

            if response.status_code == 200:
                logging.info(f"Compra realizada con éxito: {response.json()}")
                self.compra = compra_schema.load(response.json())
            else:
                logging.error(f"Error al registrar compra, código de estado: {response.status_code}")
                raise BaseException("El registro de la compra falló")
        except requests.exceptions.RequestException as e:
            logging.error(f"Excepción durante la solicitud de compra: {e}")
            raise


    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(requests.exceptions.RequestException))
    def cancelar_compra(self) -> None:
    # cancela la compra de un cliente con lógica de reintentos
       
        if not self.compra.id:
            logging.error("No se puede cancelar una compra sin un ID válido")
            raise ValueError("El ID de la compra es requerido para cancelarla")

        try:
            response = requests.delete(
                f"{self.URL}compras/{self.compra.id}",
                timeout=5  # Timeout de 5 segundos para evitar bloqueos prolongados
            )

            if response.status_code == 200:
                logging.info(f"Compra cancelada con éxito, ID: {self.compra.id}")
            else:
                logging.error(f"Error al cancelar la compra, código de estado: {response.status_code}")
                raise BaseException("La cancelación de la compra falló")
        except requests.exceptions.RequestException as e:
            logging.error(f"Excepción durante la cancelación de compra: {e}")
            raise
