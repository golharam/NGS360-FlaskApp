'''
Sequencing Runs
---------------
HTTP   URI                                                     Action                                  Implemented
----   ---                                                     ------                                  -----------
GET    /api/v0/runs                                            Retrieve a list of sequencing runs      Runs.get()
POST   /api/v0/runs                                            Create/Add a sequencing run             Runs.post()
GET    /api/v0/runs/[id]                                       Retrieve info about a specific run      get_run(id)
GET    /api/v0/runs/[id]/sample_sheet                          Retrieve the sample sheet for the run   get_run_sample_sheet(id)
PUT    /api/v0/runs/[id]/samples                               Map samples to an existing run          put_samples(id)
DELETE /api/v0/runs/[id]/samples                               Delete samples associated with run      delete_samples(id)
POST   /api/v0/runs/[id]/demultiplex                                                                   demultiplex(id)
GET    /api/v0/runs/[id]/metrics                               Retrieve demux metrics from Stat.json   SequencingRunMetrics::get

'''
import datetime
import json
from io import BytesIO

import botocore

from flask import abort, jsonify, request, send_file, flash, current_app
from flask_login import current_user
from flask_restplus import Namespace, Resource

# We need to do this rename or else SampleSheet inferferes with the 
# REST API Resource, SampleSheet
from sample_sheet import SampleSheet as IlluminaSampleSheet

from app import BOTO3 as boto3, DB as db
from app.common import access, find_bucket_key
from app.models import SequencingRun, RunToSamples
from app.blueprints.aws_batch import submit_job

NS = Namespace('runs', description='Runs related operations')

@NS.route("")
class Runs(Resource):
    def get(self):
        if 'run_barcode' in request.args:
            barcode_items = request.args['run_barcode'].split("_")
            if len(barcode_items) != 4:
                abort(400)

            run_date = datetime.datetime.strptime(barcode_items[0], "%y%m%d").date()
            machine_id = barcode_items[1]
            # Convert run_number to an integer, as it is padded with a leading zero
            # in the run_barcode
            run_number = int(barcode_items[2])
            flowcell_id = barcode_items[3]

            runs = SequencingRun.query.filter(SequencingRun.run_date == run_date,
                                              SequencingRun.machine_id == machine_id,
                                              SequencingRun.run_number == run_number,
                                              SequencingRun.flowcell_id == flowcell_id)
            if runs.count() == 0:
                abort(404)
        else:
            runs = SequencingRun.query.all()
        return {'runs': [run.to_dict() for run in runs]}

    def post(self):
        # TODO: Secure with auth_tokens
        if not request.json:
            abort(400)
        if not SequencingRun.is_data_valid(request.json):
            abort(403)

        # 1.  Make sure the run doesn't exist in ngs360
        s3_run_folder_path = request.json['s3_run_folder_path']
        run = SequencingRun.query.filter_by(s3_run_folder_path=s3_run_folder_path).first()
        if run is None:
            if len(request.json['run_date']) == 6:
                # assume format is YYMMDD
                run_date = datetime.datetime.strptime(request.json['run_date'], '%y%m%d')
            else:
                # assume format is m/d/y h:m:s eg 2/2/2018 2:06:49 PM
                run_date = datetime.datetime.strptime(request.json['run_date'], '%m/%d/%Y %I:%M:%S %p')
            machine_id = request.json['machine_id']
            run_number = request.json['run_number']
            flowcell_id = request.json['flowcell_id']
            experiment_name = request.json['experiment_name']

            run = SequencingRun(run_date=run_date, machine_id=machine_id, run_number=run_number,
                                flowcell_id=flowcell_id, experiment_name=experiment_name,
                                s3_run_folder_path=s3_run_folder_path)
            db.session.add(run)
            db.session.commit()
        else:
            abort(409)
        run = SequencingRun.query.filter_by(s3_run_folder_path=s3_run_folder_path).first()
        return {'run': run.to_dict()}, 201

@NS.route("/<sequencing_run_id>")
class Run(Resource):
    def get(self, sequencing_run_id):
        run = SequencingRun.query.get(sequencing_run_id)
        if run:
            return jsonify(run.to_dict())
        return jsonify({})

@NS.route("/<sequencing_run_id>/demultiplex")
class DemultiplexRun(Resource):
    def post(self, sequencing_run_id):
        # user is required for _submitJob
        if request.json and 'user' in request.json:
            user = request.json['user']
        elif 'user' in request.args:
            user = request.args['user']
        else:
            abort(404)

        run = SequencingRun.query.get(sequencing_run_id)
        if not run: abort(404)
        run_barcode = "%s_%s_%s_%s" % (run.run_date.strftime("%y%m%d"), run.machine_id,
                                       run.run_number, run.flowcell_id)

        if request.json and 'ASSAY' in request.json and request.json['ASSAY'] == "EdgeSeq":
            job_name = 'edgeseq-%s' % run_barcode
            options = "--barcode-mismatches 0"
            batch_job = current_app.config['BCL2FASTQ_JOB']
            job_q = current_app.config['BCL2FASTQ_QUEUE']
            container_overrides = {
                "environment": [
                    {"name": "RUN_FOLDER_S3_PATH", "value": run.s3_run_folder_path},
                    {"name": "OPTIONS", "value": options}
                ],
                "memory": 32000,
                "vcpus": 8
            }
        elif request.json and 'ASSAY' in request.json and request.json['ASSAY'] == "scRNASeq":
            data = {"cmd": ["run",
                            "-u", user,
                            "-r", run.s3_run_folder_path,
                            "-d"]}
            payload = json.dumps(data)
            response = boto3.clients['lambda'].invoke(
                FunctionName=current_app.config['SCRNASEQ_LAMBDA_FN'],
                InvocationType='RequestResponse',
                LogType='None',
                Payload=payload)
            payload = response['Payload'].read()
            return {}
        else:
            # Perform standard demultiplexing
            job_name = 'demultiplex-%s' % run_barcode
            options = "--no-lane-splitting"
            batch_job = current_app.config['BCL2FASTQ_JOB']
            job_q = current_app.config['BCL2FASTQ_QUEUE']
            container_overrides = {
                "environment": [
                    {"name": "RUN_FOLDER_S3_PATH", "value": run.s3_run_folder_path},
                    {"name": "OPTIONS", "value": options}
                ],
                "memory": 32000,
                "vcpus": 8
            }

        return submit_job(job_name, container_overrides, batch_job, job_q, user)

@NS.route("/<sequencing_run_id>/metrics")
class SequencingRunMetrics(Resource):
    def get(self, sequencing_run_id):
        run = SequencingRun.query.get(sequencing_run_id)
        if not run:
            return {"Status": "error", "Message": "Run not found"}, 404
        s3_stats_json_file = "%s/Stats/Stats.json" % run.s3_run_folder_path
        bucket, key = find_bucket_key(s3_stats_json_file)
        if not access(bucket, key):
            return {"Status": "error", "Message": "%s not found" % s3_stats_json_file}, 404
        data = boto3.clients['s3'].get_object(Bucket=bucket, Key=key)
        json_stats = json.loads(data['Body'].read())
        return json_stats

@NS.route("/<sequencing_run_id>/sample_sheet")
class SampleSheet(Resource):
    def get(self, sequencing_run_id):
        ss_json = {'Summary': {}, 'Header': {},
                   'Reads': {}, 'Settings': {},
                   'DataCols': [], 'Data': []}
        run = SequencingRun.query.get(sequencing_run_id)
        if run:
            ss_json['Summary'] = run.to_dict()
            sample_sheet_path = "%s/SampleSheet.csv" % run.s3_run_folder_path
            bucket, key = find_bucket_key(sample_sheet_path)
            if not access(bucket, key):
                return {"Status": "error", "Message": "%s not found" % sample_sheet_path}, 404
            try:
                ss = IlluminaSampleSheet(sample_sheet_path)
                ss = ss.to_json()
                ss = json.loads(ss)
                ss_json['Header'] = ss['Header']
                ss_json['Reads'] = ss['Reads']
                ss_json['Settings'] = ss['Settings']
                ss_json['DataCols'] = list(ss['Data'][0].keys())
                ss_json['Data'] = ss['Data']
            except ValueError:
                pass
        return ss_json

@NS.route("/<sequencing_run_id>/samples")
class Samples(Resource):
    def delete(self, sequencing_run_id):
        """
        This function and API endpoint delete samples (RunToSamples objects
        in the database) associated with a run.
        """
        run = SequencingRun.query.get(sequencing_run_id)
        if not run:
            return '{"Status": "Not Found", "Message": "Run not found"}', 404

        if not request.json:
            # Delete all samples associated with run
            desired_samples_mappings = RunToSamples.query.filter(
                RunToSamples.sequencing_run_id == sequencing_run_id)
            desired_samples_mappings.delete()
            db.session.commit()
            return '{"Status": "OK"}', 200
        else:
            # Delete specific samples associated with run
            sample_ids = request.json['sample_ids']
            desired_samples_mappings = RunToSamples.query.filter(
                RunToSamples.sequencing_run_id == sequencing_run_id,
                RunToSamples.sample_id.in_(sample_ids))

        successful_deletions = []
        unsuccessful_deletions = []
        for mapping in desired_samples_mappings:
            try:
                db.session.delete(mapping)
                db.session.commit()
                successful_deletions.append(mapping.sample_id)
            except:
                db.session.rollback()
                unsuccessful_deletions.append(mapping.sample_id)

        # Return 200 HTTP code and samples that were successully deleted and those that
        # were unsuccessfully deleted
        return jsonify({"Status": "OK", "Successful deletions": successful_deletions,
                        "Unsuccessful deletions": unsuccessful_deletions}), 200

    def put(self, sequencing_run_id):
        """
        Create a mapping between a run, an associated project, and associated
        samples by creating new objects in the RunToSamples table.

        :param sequencing_run_id: Sequencing Run ID
        :returns: Either HTTP success code with info of mapping that was just
        created or HTTP error code if an error occurred.

        JSON post data is a list of samples and projectid:
        [{'sampleid': sampleid, 'projectid': projectid},
        ...
        ]
        """
        run = SequencingRun.query.get(sequencing_run_id)
        if not run:
            return {"Status": "Not Found", "Message": "Run not found"}, 404

        if not request.json:
            return {"Status": "Bad Request",
                    "Message": "No json data included in the request, or json data is empty"}, 400

        new_runtosamples_objs = []

        # Do this in case there is only one mapping sent, and it is not formatted as a list
        if type(request.json) != list:
            request.json = [request.json]

        for mapping in request.json:
            run_to_samples_mapping = RunToSamples(sequencing_run_id=sequencing_run_id)

            if 'sampleid' in mapping:
                run_to_samples_mapping.sample_id = mapping['sampleid']
            else:
                return {"Status": "Bad Request",
                        "Message": "All mappings in request must include Samples to map to Sequencing Run"}, 400

            if 'projectid' in mapping:
                projectid = mapping['projectid']
            else:
                projectid = None
            run_to_samples_mapping.project_id = projectid
            new_runtosamples_objs.append(run_to_samples_mapping)

        db.session.add_all(new_runtosamples_objs)

        try:
            db.session.commit()
            return {"Status": "OK", "Successful mappings": request.json}, 200
        except:
            db.session.rollback()
            return {"Status": "Internal Server Error",
                            "Message": "Run to Samples mappings could not be saved"}, 500

@NS.route("/<sequencing_run_id>/file")
class SequencingRunFile(Resource):
    def get(self, sequencing_run_id):
        ''' Download file '''
        if request.args.get('file') is None:
            current_app.logger.warning("No file requested from run %s", sequencing_run_id)
            abort(400)

        run = SequencingRun.query.get(sequencing_run_id)
        if not run:
            current_app.logger.warning("Run %d not found", sequencing_run_id)
            abort(404)

        s3_file_path = "%s/%s" % (run.s3_run_folder_path, request.args.get('file'))
        bucket, key = find_bucket_key(s3_file_path)
        if access(bucket, key):
            data = boto3.clients['s3'].get_object(Bucket=bucket, Key=key)
            content = data['Body'].read()
            content_io = BytesIO(content)
            return send_file(content_io, mimetype="text/plain", as_attachment=True,
                             attachment_filename=request.args.get('file'))
        current_app.logger.warning("Requested file, %s, not found", request.args.get('file'))
        abort(404)

    def post(self, sequencing_run_id):
        ''' Upload file '''
        # Code from http://flask.pocoo.org/docs/1.0/patterns/fileuploads/
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file provided', 'danger')
            return {"status": 'No file provided'}
        if 'filename' not in request.values:
            flash('No filename provided', 'danger')
            return {"status": 'No filename provided'}

        # if user does not select file, browser also submit an empty part without filename
        uploaded_file = request.files['file']
        if uploaded_file.filename is None or uploaded_file.filename == '':
            flash('No selected file', 'danger')
            return {"status": "No selected file"}
        content = uploaded_file.read()

        if request.values['filename'] == 'SampleSheet.csv':
            try:
                IlluminaSampleSheet(BytesIO(content))
            except:
                flash("Invalid sample sheet", 'danger')
                return {"status": "Invalid sample sheet"}

        # make sure the run exists in the database
        run = SequencingRun.query.get(sequencing_run_id)
        if not run:
            abort(404)

        bucket, key = find_bucket_key("%s/%s" % (run.s3_run_folder_path, request.values['filename']))
        boto3.clients['s3'].put_object(Body=content, Bucket=bucket, Key=key,
                                       ServerSideEncryption='AES256')
        flash("File, %s, uploaded" % uploaded_file.filename, 'info')
        return {"status": "File, %s, uploaded" % uploaded_file.filename}
