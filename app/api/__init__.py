'''
Base of REST API
'''
import pkg_resources
import os
from datetime import timedelta
from flask import Blueprint, current_app, request, session
from flask_restplus import Api

from .jobs import NS as jobs_ns
from .notifications import NS as notifications_ns
from .projects import NS as projects_ns
from .runs import NS as runs_ns
from .samples import NS as samples_ns
from .users import NS as users_ns
from .xpress import NS as xpress_ns

BLUEPRINT = Blueprint('rest_api', __name__, url_prefix='/api/v0')

@BLUEPRINT.route("/test")
def apiTest():
    data = {
        'Package Versions': {},
        'Session Variables': {},
        'Cookie Variables': {},
        'Request Headers': {},
        'Environment Variables': {},
        'Application Settings': {}
    }

    # Package Versions
    dists = [str(d).replace(" ",":") for d in pkg_resources.working_set]
    for dist in dists:
        pkgName, pkgVersion = dist.split(':')
        data['Package Versions'][pkgName] = pkgVersion

    # Session Variables
    for s in session:
        data['Session Variables'][s] = session[s]

    # Cookie Variables
    for c in request.cookies:
        data['Cookie Variables'][c] = request.cookies.get(c)

    # Request Headers
    for h in request.headers.keys():
        data['Request Headers'][h] = request.headers.get(h)

    # Environment Variables
    for k,v in sorted(os.environ.items()):
        data['Environment Variables'][k] = v

    # Application Settings
    for k in current_app.config:
        if isinstance(current_app.config[k], (timedelta)):
            data['Application Settings'][k] = str(current_app.config[k])
        else:
            data['Application Settings'][k] = current_app.config[k]
    #data['Application Settings']['debug'] = current_app.debug
    #data['Application Settings']['testing'] = current_app.testing
    
    return data

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
