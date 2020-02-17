'''
Main application endpoints
'''
from flask import Blueprint, render_template, request, session, jsonify, current_app, abort
from flask_login import login_required
from app import project_registry, BASESPACE as base_space, DB as db
from app.models import Project, RunToSamples, SequencingRun

BP = Blueprint('main', __name__)

@BP.route('/')
@login_required
def index():
    '''
    Home Page URL: /
    '''
    return render_template('main/index.html')

@BP.route("/basespace")
@login_required
def show_basespace():
    ''' Show Basespace page '''
    return render_template('main/basespace.html')

@BP.route("/jobs")
@login_required
def show_batch_jobs():
    ''' Show user jobs '''
    if 'username' in request.args:
        username = request.args.get('username')
    elif 'username' in session:
        username = session['username']
    else:
        username = None
    return render_template('main/jobs.html', username=username)

@BP.route("/illumina_runs")
@login_required
def show_illumina_runs():
    ''' Show Illumina Runs page '''
    return render_template('main/illumina_runs.html')

@BP.route("/illumina_run")
@login_required
def show_illumina_run():
    ''' Show an Illumina run '''
    runid = request.args.get('runid')
    if not runid:
        return "Run ID not specified", 404

    run = SequencingRun.query.get(runid)
    if run:
        run_barcode = "%s_%s_%s_%s" % (run.run_date.strftime("%y%m%d"), run.machine_id,
                                       run.run_number.zfill(4), run.flowcell_id)
        return render_template('main/illumina_run.html', runid=runid, run_barcode=run_barcode,
                               experiment_name=run.experiment_name, flowcell=run.flowcell_id)
    return abort(404)

@BP.route("/projects")
@login_required
def show_projects():
    ''' Show Projects page '''
    return render_template('main/projects.html')

@BP.route("/projects/<projectid>")
@login_required
def show_project(projectid):
    ''' Show Project page '''
    basespace_project = base_space.get_project_id(projectid)
    project = Project.query.get(projectid)

    if project:
        xpress_project_id = project.xpress_project_id
    else:
        xpress_project_id = 0

    runs = db.session.query(SequencingRun).join(RunToSamples).filter(
        RunToSamples.project_id == projectid).distinct(RunToSamples.sequencing_run_id)
    associated_runs = []
    for run in runs:
        if run.experiment_name:
            barcode = run.experiment_name
        else:
            barcode = "%s_%s_%s_%s" % (run.run_date.strftime("%y%m%d"), run.machine_id,
                                       run.run_number.zfill(4), run.flowcell_id)
        associated_runs.append({'id': run.id, 'barcode': barcode})
    return render_template('main/project.html', projectid=projectid,
                           basespace_project=basespace_project,
                           xpress_project_id=xpress_project_id,
                           runs=associated_runs)


@BP.route("/illumina_run/<runid>/files")
@login_required
def browse_sequencing_run_files(runid):
    ''' Show File Browser page '''

    # sample_filesystem based on sample filesystem at:
    # https://realpython.com/working-with-files-in-python/
    # Any filesystem should be able to be converted to this type
    # of data structure
    sample_filesystem = {
        'directories': [
            {'name': 'sub_dir_a', 'files': [{'name': 'bar.py', 'date': '', 'size': '76KB'}, {'name': 'foo.py', 'date': '', 'size': '76KB'}]},
            {'name': 'sub_dir_b', 'files': [{'name': 'file4.txt', 'date': '', 'size': '76KB'}]},
            {'name': 'sub_dir_c', 'subdirectories': [{'name': 'sub_dir_c1', 'files': [{'name': 'file6.txt', 'date': '', 'size': '76KB'}, {'name': 'file7.csv', 'date': '', 'size': '76KB'}]}], 'files': [{'name': 'config.py', 'date': '', 'size': '76KB'}, {'name': 'file5.txt', 'date': '', 'size': '76KB'}]},
        ],
        'files': [{'name': 'file1.py', 'date': '', 'size': '76KB'}, {'name': 'file2.csv', 'date': '', 'size': '76KB'}, {'name': 'file3.txt', 'date': '', 'size': '76KB'}]
    }

    return render_template('main/file_browser.html', filesystem_dict=sample_filesystem)


@BP.route("/projects/<projectid>/files")
@login_required
def browse_project_files():
    ''' Show File Browser page '''
    return render_template('main/file_browser.html')

