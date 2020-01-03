'''
NGS 360 Projects
----------------
    HTTP    URI                             Action
    ----    ---                             ------
    GET     /api/v0/projects                Retrieve a list of projects
    GET     /api/v0/projects/[project_id]   Retrieve a project
    POST    /api/v0/projects                Create a new project
    PUT     /api/v0/projects/[project_id]   Update an existing project
    DELETE  /api/v0/projects/[project_id]   Delete a project (this will always return not authorized)
'''
from flask import request, abort, current_app, jsonify
from flask_login import current_user
from flask_restplus import Namespace, Resource
from app.models import Project, RunToSamples, SequencingRun
from app.biojira import getJira, getTBioPMJiraIssues, addCommentToIssues
from app.blueprints.aws_batch import submit_job
from app import SEVENBRIDGES as sbg

NS = Namespace('projects', description='Project related operations')

@NS.route("/<projectid>")
class ProjectList(Resource):
    def get(projectid):
        project = Project.query.get(projectid)
        if not project:
            result = {}
        else:
            run_to_samples = RunToSamples.query.filter(RunToSamples.project_id == projectid)

            associated_runs = []
            for run_to_samples in run_to_samples:
                run = SequencingRun.query.get(run_to_samples.sequencing_run_id)
                run_dict = run.to_dict()
                associated_runs.append(run_dict)

            result = {
                'id': project.id,
                'rnaseq_qc_report': project.rnaseq_qc_report,
                'wes_qc_report': project.wes_qc_report,
                'xpress_project_id': project.xpress_project_id,
                'sequencing_runs': associated_runs
            }
        return jsonify(result), 200

    def put(projectid):
        ''' REST API to update project '''
        # TODO: Secure with auth_tokens
        if not request.json:
            return '{"error": "No json included"}', 404

        if 'rnaseq_qc_report' in request.json:
            rnaseq_qc_report = request.json['rnaseq_qc_report']
            project = Project.query.get(projectid)
            if project is None:
                project = Project(id=projectid, rnaseq_qc_report=rnaseq_qc_report)
                db.session.add(project)
            else:
                project.rnaseq_qc_report = rnaseq_qc_report
            db.session.commit()
            result, _ = super.get(projectid)
            return result, 201

        if 'wes_qc_report' in request.json:
            wes_qc_report = request.json['wes_qc_report']
            project = Project.query.get(projectid)
            if project is None:
                project = Project(id=projectid, wes_qc_report=wes_qc_report)
                db.session.add(project)
            else:
                project.wes_qc_report = wes_qc_report
            db.session.commit()
            result, _ = super.get(projectid)
            return result, 201

        if 'xpress_project_id' in request.json:
            xpress_project_id = int(request.json['xpress_project_id'])
            project = Project.query.get(projectid)
            if project is None:
                project = Project(id=projectid, xpress_project_id=xpress_project_id)
                db.session.add(project)
            else:
                project.xpress_project_id = xpress_project_id
            db.session.commit()

            # Comment on TBIOPM ticket that project about Xpress project status
            if xpress_project_id == -1:
                comment = "Project submitted to Xpress for loading."
            else:
                comment = "Xpress project loaded, http://xpress.pri.bms.com/CGI/project_summary.cgi?project=%s" % xpress_project_id
            biojira = getJira()
            issues = getTBioPMJiraIssues(biojira, projectid)
            if issues:
                addCommentToIssues(biojira, comment, issues)
            result, _ = super.get(projectid)
            return result, 201
        abort(404)

@NS.route("/<projectid>/copyAnalysisResults")
class CopyAnalysisResultsAction(Resource):
    def post(projectid):
        '''
        Rest API to copy RNA-Seq or WES analysis results from SB

        :param projectid: BMS Project ID

        :param analysistype: Type of analysis results to export: CRISPR, RNA-Seq or WES
        :param reference: Reference Model used in analysis

        :return: AWS Batch Job ID
        '''
        # TODO: Secure with auth_tokens
        if not request.json:
            return '{"Status": "error", "Message": "No json included"}', 404

        if 'analysistype' not in request.json:
            return '{"Status": "error", "Message": "analysistype not found in JSON"}', 404
        analysistype = request.json['analysistype']

        if 'reference' not in request.json:
            return '{"Status": "error", "Message": "reference not found in JSON"}', 404
        reference = request.json['reference']

        # user is required for _submitJob
        if request.json and 'user' in request.json:
            user = request.json['user']
        else:
            user = current_user.username

        if analysistype == 'RNA-Seq':
            job_cmd = {
                'command': ['sbg', 'exportResults',
                            '-n', projectid,
                            '-u', user,
                            '-t', analysistype,
                            '--referenceModel', reference]
            }
        elif analysistype == 'WES':
            job_cmd = {
                'command': ['sbg', 'exportResults',
                            '-n', projectid,
                            '-u', user,
                            '-t', analysistype,
                            '--wes-reference', reference]
            }
        elif analysistype == 'CRISPR':
            job_cmd = {
                'command': ['sbg', 'exportResults',
                            '-n', projectid,
                            '-u', user,
                            '-t', analysistype]
            }
        else:
            return '{"Status": "error", "Message": "Unknown analysistype"}', 404

        job_name = 'copyAnalysisResults-%s' % projectid
        return submit_job(job_name, job_cmd, current_app.config['JOB_DEFINITION'], None, user)

@NS.route("/<projectid>/exportSevenBridgesProject/<projecttype>")
class ExportSevenBridgesProject(Resource):
    def get(projectid, projecttype):
        '''
        Rest API to export RNA-Seq or WES Project from SB

        :param projectid: BMS Project ID
        :param sbprojectid: SevenBridges Project ID
        :param projecttype: Type of Project to Export: RNA-Seq or WES
        :return: AWS Batch Job ID
        '''
        # Query the database to get the SB Project
        # If not in database, get the project by ID, else by project name-id
        sb_project = sbg.get_project_by_name(projectid)
        if sb_project is None:
            project_name = "%s-%s" % (projectid, projecttype)
            sb_project = sbg.get_project_by_name(project_name)
        if sb_project is None:
            error_msg = "Unable to determine SB Project ID from Project Name, %s" % project_name
            response = dict()
            response['status'] = 'ERROR'
            response['log'] = error_msg
            return jsonify(response)
        job_name = 'copySevenBridgesProjectResultsToS3-%s' % projectid
        job_cmd = {
            'command' : ['sbg', 'exportResults',
                         '--ngsProject', projectid,
                         '--sbprojectid', sb_project.id,
                         '--userid', request.args.get('userid'),
                         '--projectType', projecttype]
        }
        return submit_job(job_name, job_cmd, current_app.config['JOB_DEFINITION'], None,
                          current_user.username)

@NS.route("/<projectid>/exportSevenBridgesProject/<projecttype>/<reference>")
class exportSevenBridgesProjectByReference(Resource):
    def get(projectid, projecttype, reference):
        '''
        Rest API to export RNA-Seq or WES Project from SB

        :param projectid: BMS Project ID
        :param sbprojectid: SevenBridges Project ID
        :param projecttype: Type of Project to Export: RNA-Seq or WES
        :param reference: Reference Model used in analysis
        :return: AWS Batch Job ID
        '''
        # Query the database to get the SB Project
        # If not in database, get the project by ID, else by project name-id
        sb_project = sbg.get_project_by_name(projectid)
        if sb_project is None:
            project_name = "%s-%s" % (projectid, projecttype)
            sb_project = sbg.get_project_by_name(project_name)
        if sb_project is None:
            error_msg = "Unable to determine SB Project ID from Project Name, %s" % project_name
            response = dict()
            response['status'] = 'ERROR'
            response['log'] = error_msg
            return jsonify(response)
        job_name = 'copySevenBridgesProjectResultsToS3-%s' % projectid
        if projecttype == 'RNA-Seq':
            job_cmd = {
                'command' : ['sbg', 'exportResults',
                             '--ngsProject', projectid,
                             '--sbprojectid', sb_project.id,
                             '--userid', request.args.get('userid'),
                             '--projectType', projecttype,
                             '--referenceModel', reference]
            }
        elif projecttype == 'WES':
            job_cmd = {
                'command' : ['sbg', 'exportResults',
                             '--ngsProject', projectid,
                             '--sbprojectid', sb_project.id,
                             '--userid', request.args.get('userid'),
                             '--projectType', projecttype,
                             '--wes-reference', reference]
            }
        return submit_job(job_name, job_cmd, current_app.config['JOB_DEFINITION'], None,
                          current_user.username)
