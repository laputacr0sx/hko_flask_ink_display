from flask import Flask
from flask_cors import CORS
from flask_restful import Api

from controller.WeatherController import WeatherController
from service.DrawService import DrawService
from service.HKOService import HKOService

app = Flask(__name__)
CORS(app)
api = Api(app)

draw_service = DrawService()
hko_service = HKOService()

api.add_resource(WeatherController, '/weather', resource_class_kwargs={
    'draw_service': draw_service,
    'hko_service': hko_service
})

if __name__ == '__main__':
    app.run(debug=True)
