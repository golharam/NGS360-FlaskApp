'''
AWS Batch interface
'''
import json
from flask import current_app, jsonify, Blueprint
import botocore

from app import DB as db, BOTO3 as boto3
from app.models import BatchJob

BP = Blueprint("aws_batch", __name__)

def submit_job(job_name, job_cmd, job_def, job_q, user):
    '''
    Submit a job to AWS Batch, and return the job id.
    '''
    try:
        response = boto3.clients['batch'].submit_job(
            jobName=job_name,
            jobQueue=job_q,
            jobDefinition=job_def,
            containerOverrides=job_cmd
        )
    except botocore.exceptions.ParamValidationError as err:
        current_app.logger.error("There was ParamValidationError submitting a job: %s", err)
        return {"status": "ERROR",
                "log": "There was an error submitting your job."}
    job_id = response['jobId']
    job = BatchJob(id=job_id, name=job_name, command=json.dumps(job_cmd),
                   user=user, status='SUBMITTED')
    db.session.add(job)
    db.session.commit()
