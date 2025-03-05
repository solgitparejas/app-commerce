from flask import jsonify, Blueprint, request

from app.mapping import CarritoSchema, ProductoSchema
from app.services import CommerceService

from flask_limiter import Limiter
from app.__init__ import limiter
from flask_limiter.util import get_remote_address

home = Blueprint('home', __name__)
carrito_schema = CarritoSchema()
producto_schema = ProductoSchema()


@home.route('/commerce/comprar', methods=['POST'])
@limiter.limit(limit_value="60 per second", key_func=get_remote_address)
def index():
    commerce = CommerceService()
    carrito = carrito_schema.load(request.get_json())
    commerce.comprar(carrito)
    resp = jsonify({"microservicio": "Orquestador", "status": "ok"})
    resp.status_code = 200
    return resp

@home.route('/commerce/consultar/catalogo/<int:id>', methods=['GET'])
def consultar_catalogo(id:int):
    commerce = CommerceService()
    try:
        producto = commerce.consultar_catalogo(id)
        result = {"message": "No se encontró el producto"}
        status_code = 404
        if producto:
            result = producto_schema.dump(producto)
            status_code = 200
        return result, status_code
    except:
        return "No anduvo papi", 404