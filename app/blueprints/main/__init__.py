'''
Main application endpoints
'''
from flask import Blueprint, render_template, request, session

BP = Blueprint('main', __name__)

@BP.route('/')
def index():
    '''
    Home Page URL: /
    '''
    return render_template('main/index.html')

@BP.route("/basespace")
def show_basespace():
    ''' Show Basespace page '''
    return render_template('main/basespace.html')

@BP.route("/jobs")
def show_batch_jobs():
    ''' Show user jobs '''
    if 'username' in request.args:
        username = request.args.get('username')
    else:
        username = session['username']
    return render_template('jobs.html', username=username)

@BP.route("/illumina_runs")
def show_illumina_runs():
    ''' Show Illumina Runs page '''
    return render_template('main/illumina_runs.html')
