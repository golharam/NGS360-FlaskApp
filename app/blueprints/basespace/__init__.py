'''
BaseSpace Blueprint
'''
from flask import Blueprint, jsonify, current_app
from flask_login import login_required, current_user
from app import BASESPACE as Basespace
from app.blueprints.aws_batch import submit_job

BP = Blueprint('basespace', __name__)

@BP.route("/archiveRun/<run_name>", methods=['GET'])
@login_required
def archive_basespace_run(run_name):
    ''' Copy run folder from BaseSpace to S3 '''
    job_name = 'archiveRun-%s' % run_name
    job_cmd = {
        'command' : ['basespace', 'archiveRun', '-r', run_name]
    }
    return submit_job(job_name, job_cmd, current_app.config['JOB_DEFINITION'],
                      current_app.config['JOB_QUEUE'], current_user.username)

@BP.route("/basespace_runs")
def get_basespace_runs():
    ''' Get a list of runs from BaseSpace '''
    return jsonify(Basespace.get_runs())
