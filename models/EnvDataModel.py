from flask_restful import fields

env_fields = {
    'temperature': fields.Float,
    'humidity': fields.Float,
    'pressure': fields.Float,
}


class EnvironmentDao(object):
    def __init__(self, temperature, humidity, pressure):
        self.temperature: float = temperature
        self.humidity: float = humidity
        self.pressure: float = pressure

        # This field will not be sent in the response
        self.status = 'active'
