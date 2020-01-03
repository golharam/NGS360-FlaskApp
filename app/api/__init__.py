'''
Base of REST API
'''

from flask import Blueprint
from flask_restplus import Api
from .samples import NS as samples_ns
from .xpress import NS as xpress_ns
from .runs import NS as runs_ns
from .projects import NS as projects_ns

BLUEPRINT = Blueprint('rest_api', __name__, url_prefix='/api/v0')

API = Api(BLUEPRINT,
          title="NGS360 REST API",
          version="1.0",
          description="Provide REST API endpoints for NGS 360")

API.add_namespace(projects_ns)
API.add_namespace(runs_ns)
API.add_namespace(samples_ns)
API.add_namespace(xpress_ns)
