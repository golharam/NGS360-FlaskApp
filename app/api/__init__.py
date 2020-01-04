'''
Base of REST API
'''

from flask import Blueprint
from flask_restplus import Api

from .jobs import NS as jobs_ns
from .notifications import NS as notifications_ns
from .projects import NS as projects_ns
from .runs import NS as runs_ns
from .samples import NS as samples_ns
from .users import NS as users_ns
from .xpress import NS as xpress_ns

BLUEPRINT = Blueprint('rest_api', __name__, url_prefix='/api/v0')

API = Api(BLUEPRINT,
          title="NGS360 REST API",
          version="1.0",
          description="Provide REST API endpoints for NGS 360")

API.add_namespace(jobs_ns)
API.add_namespace(notifications_ns)
API.add_namespace(projects_ns)
API.add_namespace(runs_ns)
API.add_namespace(samples_ns)
API.add_namespace(users_ns)
API.add_namespace(xpress_ns)
