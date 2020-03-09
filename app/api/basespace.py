from flask_restplus import Namespace, Resource
from app import BASESPACE as base_space

NS = Namespace('basespace', description='BaseSpace related operations')

@NS.route('/<basespace_project>/samples')
class BaseSpaceProjectSamples(Resource):
    def get(self, basespace_project):
        return base_space.get_project_samples(basespace_project)

