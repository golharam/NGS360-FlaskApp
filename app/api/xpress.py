'''
Xpress Projects
----------------
    HTTP    URI                                Action                         Implemented
    ----    ---                                ------                         -----------
    GET     /api/v0/xpress                     Retrieve a list of projects
    GET     /api/v0/xpress/[xpress_project_id] Retrieve a project             XpressProject.get()
    POST    /api/v0/xpress                     Create a new project
    PUT     /api/v0/xpress/[xpress_project_id] Update an existing project
    DELETE  /api/v0/xpress/[xpress_project_id] Delete a project (this will
                                               always return not authorized)
'''

from flask import current_app
from flask_restplus import Namespace, Resource
import requests

from app import DB as db
from app.models import Project

NS = Namespace('xpress', description='Xpress related operations')

@NS.route("/<int:xpress_project_id>")
class XpressProject(Resource):
    def get(self, xpress_project_id):
        '''
        Get the latest Xpress project we know of
        '''
        xpress_rest_endpoint = current_app.config['XPRESS_RESTAPI_ENDPOINT']
        response = requests.get("%s/project/%s" % (xpress_rest_endpoint, xpress_project_id))
        xpress_project = response.json()
        next_version = xpress_project['project']['next version']

        # Get the latest Xpress project id, if the one we have isn't the latest
        while next_version:
            response = requests.get("%s/project/%s" % (xpress_rest_endpoint, next_version))
            xpress_project = response.json()
            next_version = xpress_project['project']['next version']

        current_version = xpress_project['project']['project_id']

        # if the current version isn't the version we queried for, log the current version in the db
        if int(current_version) != int(xpress_project_id):
            project = Project.query.filter_by(xpress_project_id=xpress_project_id).first()
            if project:
                project.xpress_project_id = current_version
                db.session.commit()

        return response.text
