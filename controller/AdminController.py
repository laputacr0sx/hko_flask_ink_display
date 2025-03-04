from flask_restful import Resource, marshal_with, reqparse

class AdminController(Resource):
    def __init__(self, **kwargs):
        self.draw_service = kwargs['draw_service']

    def get(self):
        gg = self.draw_service.test_draw()

        return gg
