"""
Samples
-------
HTTP    URI                             Action                                  Implemented
----    ---                             ------                                  -----------
GET     /api/v0/samples                Retrieve a list of samples              SampleList.get()
DELETE  /api/v0/samples                Delete a set of samples                 SampleList.delete()
GET     /api/v0/samples/[id]           Retrieve a single sample                Sample.get()
POST    /api/v0/samples                Create/Add a sample                     SampleList.post()
PUT     /api/v0/samples/[id]           Edit a sample                           Sample.put()
"""

from flask_restplus import Namespace, Resource
from flask import request
from app import DB as db
from app.models import ProjectSample

NS = Namespace('samples', description='Samples related operations')

@NS.route("/samples")
class SampleList(Resource):

    def delete(self):
        """
        Delete a list of samples provided by either:
        1. Providing a project_id query string parameter to delete
           all samples associated with the project, or
        2. (TBD) Provide a list of sample (db) ids, or
        3. (TBD) Provide a list of project_id + sample_id

        TBD: Protect this functionality with authorization
        TBD: Can this also handle the route of DELETE /api/v0/projects/<projectid>/samples
        """
        if 'project_id' in request.args:
            # TBD: Make sure the project ID is valid BEFORE deleting samples
            samples = ProjectSample.query.filter(
                ProjectSample.project_id == request.args['project_id'])
            for sample in samples:
                db.session.delete(sample)
            db.session.commit()
        else:
            # Check for list of samples in POST body
            return {
                "Status": "Internal Server Error",
                "Message": "Functionality not yet implemented"
            }, 500

    def get(self):
        """
        Returns a list of samples.  If project_id is provided as a request argument, only samples
        associated with project will be returned.

        TBD: Can this also handle the route of GET /api/v0/projects/<projectid>/samples
        """
        if 'project_id' in request.args:
            samples = ProjectSample.query.filter(
                ProjectSample.project_id == request.args['project_id'])

            if samples.count():
                samples_to_return = [sample.to_dict() for sample in samples]
                return {'samples': samples_to_return}
            else:
                return {'samples': []}
        else:
            samples = ProjectSample.query.all()
            return {'samples': [sample.to_dict() for sample in samples]}

    def post(self):
        """
        Adds new sample(s) to the database.  Samples are provided in JSON POST body in the format:

            {'samples': [{"sample_id": "sampleA", "project_id": "P-00000000-0001"},
                         {"sample_id": "sampleB", "project_id": "P-00000000-0001"},
                         ...
                        ]
            }
        """
        if not request.json:
            return ('{"Status": "Bad Request", "Message": "No json data included in the '
                    'request, or json data is empty"}', 400)
        samples = []
        for sample in request.json['samples']:
            sample = ProjectSample(sample_id=sample['sample_id'],
                                   project_id=sample['project_id'])
            db.session.add(sample)
            samples.append(sample)
        try:
            db.session.commit()
            samples_to_return = [sample.to_dict() for sample in samples]
            return {'samples': samples_to_return}, 201
        except:
            db.session.rollback()
            return {
                "Status": "Internal Server Error",
                "Message": "Sample(s) could not be created"
            }, 500

@NS.route("/samples/<int:sample_pk>")
class Sample(Resource):

    def get(self, sample_pk):
        """
        Displays a sample's details given the ProjectSample primary key
        """
        sample = ProjectSample.query.get(sample_pk)
        if sample:
            return sample.to_dict()
        return {}

    def put(self, sample_pk):
        """
        Edits a selected sample
        """
        sample = ProjectSample.query.get(sample_pk)

        if not request.json:
            return ('{"Status": "Bad Request", "Message": "No json data included in the '
                    'request, or json data is empty"}', 400)
        sample.sample_id = request.json['sample_id']
        sample.project_id = request.json['project_id']
        db.session.add(sample)

        try:
            db.session.commit()
            return sample.to_dict(), 200
        except:
            db.session.rollback()
            return {
                "Status": "Internal Server Error",
                "Message": "Sample could not be updated"
            }, 500
