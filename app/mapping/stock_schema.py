from marshmallow import validate, fields, Schema, post_load
from app.models import Stock

class StockSchema(Schema):
    id = fields.Integer(required=False)
    producto = fields.Integer(required=True)
    fecha_transaccion = fields.DateTime(required=False, allow_none=True)
    cantidad = fields.Float(required=True, validate=validate.Range(min=0))
    entrada_salida = fields.Integer(required=True, validate=validate.OneOf([1, 2]))


    # Post load es un decorador de marshmallow
    # el cual indica que esta funcion se ejecutará despues de que
    # los datos sean deserializados. Sirve para convertir los datos validados
    # en un bojeto de python.
    @post_load
    def make_stock(self, data, **kwargs):
        stock = Stock()
        for key, value in data.items():
            setattr(stock, key, value)
        return stock