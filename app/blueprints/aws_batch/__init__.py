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
    return jsonify(response)

# TBD: The following methods are old, but used.  I'd like to phase them out in favor of the REST API
@BP.route("/get_aws_job_state/<job_name>/<jobid>/<log_lines>")
def get_aws_job_state(job_name, jobid, log_lines):
    log = ''
    try:
        response = boto3.clients['batch'].describe_jobs(jobs=[jobid])
        if response['jobs']:
            job = response['jobs'][0]
            status = job['status']
        else:
            status = 'UNKNOWN'
    except botocore.exceptions.ClientError as err:
        status = 'ERROR'
        log = err.message

    # this code is kind of funky, with the whole aws batch job id -> cloudwatch logstream name
    # https://forums.aws.amazon.com/thread.jspa?threadID=251040
    if status in ('RUNNING', 'SUCCEEDED', 'FAILED'):
        if 'logStreamName' in job['container']:
            log_stream_name = job['container']['logStreamName']
        elif 'taskArn' in job['container']:
            task_arn = job['container']['taskArn']
            task_id = task_arn[task_arn.rfind("/")+1:]
            log_stream_name = "bms-ngs-job/default/%s" % task_id
        else:
            log_stream_name = None
        if log_stream_name is not None:
            # Add status and log_stream_name to database, if not already there
            job = BatchJob.query.filter_by(id=jobid).first()
            if job:
                job.log_stream_name = log_stream_name
                db.session.commit()
#            try:
            resp = boto3.clients['logs'].get_log_events(logGroupName="/aws/batch/job",
                                                        logStreamName=log_stream_name)
            events = resp['events']
#            except:
#                response = {'status': 'Error',
#                            'log': "No log (yet) available"
#                           }
#                return jsonify(response)

            log_entries = []
            log_lines = int(log_lines)
            for i in range(0, log_lines):
                if events:
                    event = events.pop()
                    log_entries.append(event['message'])
            log_entries.reverse()
            log = '\n'.join(log_entries)

    response = {'status': status,
                'log': log
               }
    return jsonify(response)
