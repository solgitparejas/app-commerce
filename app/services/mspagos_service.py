# Archivo mspagos_services.py con retry
import os
import logging
import requests
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from app.mapping import PagoSchema
from app.models import Pago, Producto

class ClientePagosService:
    
    def __init__(self):
        self.pago = Pago()
        self.URL = os.getenv('MSPAGOS_URL', 'http://localhost:5003/api/v1/')

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(requests.exceptions.RequestException))
    def registrar_pago(self, producto: Producto, medio_pago: str) -> None:
    # Registra un pago para un producto con un medio de pago específico, con lógica de reintentos.
        
        if not producto or not producto.id or not producto.precio:
            raise ValueError("El producto debe tener un ID y un precio válidos")
        if not medio_pago:
            raise ValueError("El medio de pago no puede estar vacío")

        self.pago.producto = producto.id
        self.pago.precio = producto.precio
        self.pago.medio_pago = medio_pago
        pago_schema = PagoSchema()

        try:
            response = requests.post(
                f"{self.URL}pagos/registrar",
                json=pago_schema.dump(self.pago),
                timeout=5  # Timeout de 5 segundos
            )

            if response.status_code == 200:
                logging.info(f"Pago registrado con éxito: {response.json()}")
                self.pago = pago_schema.load(response.json())
            else:
                logging.error(f"Error al registrar el pago, código de estado: {response.status_code}")
                raise BaseException("El registro del pago falló")
        except requests.exceptions.RequestException as e:
            logging.error(f"Excepción durante la solicitud de registro de pago: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(requests.exceptions.RequestException))
    def cancelar_pago(self) -> None:
    # Cancela un pago registrado, con lógica de reintentos.
        
        if not self.pago.id:
            raise ValueError("No se puede cancelar el pago sin un ID válido")

        try:
            response = requests.put(
                f"{self.URL}pagos/cancelar/{self.pago.id}",
                timeout=5  # Timeout de 5 segundos
            )

            if response.status_code == 200:
                logging.info(f"Pago cancelado con éxito, ID: {self.pago.id}")
            else:
                logging.error(f"Error al cancelar el pago, código de estado: {response.status_code}")
                raise BaseException("La cancelación del pago falló")
        except requests.exceptions.RequestException as e:
            logging.error(f"Excepción durante la solicitud de cancelación de pago: {e}")
            raise
