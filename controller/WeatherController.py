from flask_restful import Resource, marshal_with, reqparse

from models.EnvDataModel import env_fields, EnvironmentDao

parser = reqparse.RequestParser()
parser.add_argument('temperature', type=float, required=True, help='Temperature is required', location="json")
parser.add_argument('humidity', type=float, required=True, help='Humidity is required', location='json')
parser.add_argument('pressure', type=float, required=True, help='Pressure is required', location='json')


class WeatherController(Resource):
    def __init__(self, **kwargs):
        self.draw_service = kwargs['draw_service']
        self.hko_service = kwargs['hko_service']

    @marshal_with(env_fields)
    def get(self):
        args = parser.parse_args()
        return EnvironmentDao(temperature=args['temperature'], humidity=args['humidity'], pressure=args['pressure'])

    def get(self):
        gg = self.draw_service.test_draw()

        return gg

    def get(self):
        color_image = self.draw_service.render_color_image()

        return color_image
