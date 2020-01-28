'''
NGS 360 Jobs
----------------
    HTTP    URI                             Action
    ----    ---                             ------
    GET     /api/v0/jobs                    Retrieve a list of all jobs
    POST    /api/v0/jobs                    Add a new job in the database
    GET     /api/v0/jobs/[jobid]            Retrieve a specific job
    PUT     /api/v0/jobs/[jobid]            Update a specific job
    GET     /api/v0/jobs/[jobid]/log        Retrieve job log from CloudWatch

    GET     /api/v0/users/[userid]/jobs     Retrieve list of jobs for a user
'''
import botocore
from flask import jsonify, request
from flask_restplus import Namespace, Resource
from app import DB as db, BOTO3 as boto3
from app.models import BatchJob, Notification

NS = Namespace('jobs', description='Jobs related operations')

def get_log_events(log_group, log_stream_name):
    """
    List events from CloudWatch log
    """
    kwargs = {
        'logGroupName': log_group,
        'logStreamName': log_stream_name,
        'limit': 10000,
        'startFromHead': True,
    }
    events = []
    while True:
        try:
            resp = boto3.clients['logs'].get_log_events(**kwargs)
        except botocore.exceptions.ClientError:
            return ["No log (yet) available"]
        for event in resp['events']:
            events.append(event['message'])
        if 'nextToken' in kwargs and (kwargs['nextToken'] == resp['nextForwardToken']):
            break
        kwargs['nextToken'] = resp['nextForwardToken']
    return events

@NS.route("")
class Jobs(Resource):
    def get(self):
        jobs = BatchJob.query.all()
        return jsonify([job.to_dict() for job in jobs])

    def post(self):
        # TODO: Secure with auth_tokens
        if not request.json:
            return '{"Status": "No JSON found"}', 200
        for field in ['id', 'name', 'command', 'user', 'status']:
            if field not in request.json:
                return '{"Status": "Missing %s"}' % field, 200

        job = BatchJob(id=request.json['id'],
                       name=request.json['name'],
                       command=request.json['command'],
                       user=request.json['user'],
                       status=request.json['status'])
        db.session.add(job)
        db.session.commit()
        return jsonify({'job': job.to_dict() }), 201

@NS.route("/<string:jobid>")
class Job(Resource):
    def delete(self, jobid):
        job = BatchJob.query.filter_by(id=jobid).first()
        if job:
            db.session.delete(job)
            db.session.commit()
            return '{"Status": "Deleted"}', 200
        return '{"Status": "Job does not exist"}', 200

    def get(self, jobid):
        job = BatchJob.query.filter_by(id=jobid).first()
        return jsonify(job.to_dict()), 200

    def put(self, jobid):
        '''
        Update job entry in database with new status and log_stream_name
        '''
        # TODO: Secure with auth_tokens
        if not request.json:
            return '{"Status": "JSON not found"}', 200
        job = BatchJob.query.filter_by(id=jobid).first()
        if not job:
            return '{"Status": "Job does not exist"}', 200

        if 'log_stream_name' in request.json:
            if request.json['log_stream_name'] != job.log_stream_name:
                job.log_stream_name = request.json['log_stream_name']

        if 'job_status' in request.json:
            job_status = request.json['job_status']
            if job_status != job.status:
                if job_status == 'SUCCEEDED' or job_status == 'FAILED' or job_status == 'ERROR':
                    job.viewed = False
                    # Notify the user
                    notification = Notification(user=job.user, batchjob_id=job.id, seen=False)
                    db.session.add(notification)
                job.status = job_status

        db.session.add(job)
        db.session.commit()
        return super.get(jobid)

@NS.route("<string:jobid>/log")
class JobLog(Resource):
    def get(self, jobid):
        job = BatchJob.query.filter_by(id=jobid).first()
        if not job:
            return jsonify(["Unknown job"]), 200
        if not job.log_stream_name:
            return jsonify(["No log (yet) available"]), 200

        events = get_log_events("/aws/batch/job", job.log_stream_name)
        return jsonify(events), 200
