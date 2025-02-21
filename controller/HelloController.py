from flask_restful import Resource


class HelloController(Resource):

    def get(self, name):
        return {'message': f'Hello, {name}!'}
