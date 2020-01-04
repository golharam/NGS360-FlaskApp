'''
Sequencing Runs
--------
    HTTP    URI           Action                              Implemented
    ----    ---           ------                              -----------
    GET     /api/v0/runs  Retrieve a list of sequencing runs  Runs.get()
    POST    /api/v0/runs  Create/Add a sequencing run         Runs.post()

Sequencing Runs
--------
HTTP URI                                                       Action                                  Implemented
---- ---                                                       ------                                  -----------
GET    /api/v0/runs/[id]                                       Retrieve info about a specific run      get_run(id)
GET    /api/v0/runs/[id]/sample_sheet                          Retrieve the sample sheet for the run   get_run_sample_sheet(id)
GET    /api/v0/runs/[id]/download_file?file=<file_to_download> Download a file                         download_file(id, file)
POST   /api/v0/runs/[id]/upload_features_file                                                          upload_features_file(sequencing_run_id)
POST   /api/v0/runs/[id]/upload_sample_sheet                                                           upload_sample_sheet(sequencing_run_id)
PUT    /api/v0/runs/[id]/samples                               Map samples to an existing run          put_samples(id)
DELETE /api/v0/runs/[id]/samples                               Delete samples associated with run      delete_samples(id)
POST   /api/v0/runs/[id]/demultiplex                                                                   demultiplex(id)
GET    /api/v0/runs/[id]/metrics                               Retrieve demux metrics from Stat.json   get_metrics(id)

'''
import datetime
import json
from io import BytesIO

from flask import abort, jsonify, request, send_file, flash, current_app
from flask_login import current_user
from flask_restplus import Namespace, Resource

from sample_sheet import SampleSheet

from app import BOTO3 as boto3
from app.models import SequencingRun
from app.blueprints.aws_batch import submit_job

NS = Namespace('runs', description='Runs related operations')

def access(bucket, key):
    '''
    This function mimick os.access to check for a file
    key is full s3 path to file eg s3://mybucket/myfile.txt
    '''
    paginator = s3.get_paginator('list_objects')
    iterator = paginator.paginate(Bucket=bucket,
                                  Prefix=key, Delimiter='/')
    for responseData in iterator:
        #common_prefixes = responseData.get('CommonPrefixes', [])
        contents = responseData.get('Contents', [])
        #if not contents: # and not common_prefixes:
            #self._empty_result = True
        #    return
        #for common_prefix in common_prefixes:
            # is Dir, should never occur
        for content in contents:
            return key == content['Key']
    return False

def find_bucket_key(s3path):
    """
    This is a helper function that given an s3 path such that the path is of
    the form: bucket/key
    It will return the bucket and the key represented by the s3 path, eg
    if s3path == s3://bmsrd-ngs-data/P-234
    """
    if s3path.startswith('s3://'):
        s3path = s3path[5:]
    s3components = s3path.split('/')
    bucket = s3components[0]
    s3key = ""
    if len(s3components) > 1:
        s3key = '/'.join(s3components[1:])
    return bucket, s3key

@NS.route("")
class Runs(Resource):
    def get():
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
            if runs.count():
                return jsonify({'run': runs[0].to_dict()}), 200
            abort(404)
        else:
            runs = SequencingRun.query.all()
        return jsonify({'runs': [run.to_dict() for run in runs]}), 200

    def post():
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
        return jsonify({'run': run.to_dict()}), 201

@NS.route("/<sequencing_run_id>")
class Run(Resource):
    def get(sequencing_run_id):
        run = SequencingRun.query.get(sequencing_run_id)
        if run:
            return jsonify(run.to_dict())
        return jsonify({})

@NS.route("/<sequencing_run_id>/demultiplex")
class DemultiplexRun(Resource):
    def post(sequencing_run_id):
        # user is required for _submitJob
        if request.json and 'user' in request.json:
            user = request.json['user']
        else:
            user = current_user.username

        run = SequencingRun.query.get(sequencing_run_id)
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
            data = {"user": request.json['user'],
                    "s3_runfolder_path": run.s3_run_folder_path,
                    "reference": request.json['reference']}
            response = boto3.clients['lambda'].invoke(
                FunctionName=current_app.config['SCRNASEQ_LAMBDA_FN'],
                InvocationType='RequestResponse',
                LogType='None',
                Payload=json.dumps(data))
            payload = response['Payload'].read()
            return payload
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

# /api/v0/runs/<sequencing_run_id>/download_sample_sheet should redirect to here
@NS.route("/<sequencing_run_id>/download_file")
class DownloadFile(Resource):
    def get(sequencing_run_id):
        run = SequencingRun.query.get(sequencing_run_id)
        if not run:
            abort(404)

        s3_file_path = "%s/%s" % (run.s3_run_folder_path, request.args.get('file'))
        bucket, key = find_bucket_key(s3_file_path)
        if access(bucket, key):
            data = boto3.clients['s3'].get_object(Bucket=bucket, Key=key)
            content = data['Body'].read()
            content_io = ByteIO(content)
            return send_file(content_io, mimetype="text/plain", as_attachment=True,
                             attachment_filename=request.args.get('file'))
        abort(404)

@NS.route("/<sequencing_run_id>/metrics")
class SequencingRunMetrics(Resource):
    def get(sequencing_run_id):
        run = SequencingRun.query.get(sequencing_run_id)
        if not run:
            return '{"Status": "error", "Message": "Run not found"}', 404
        s3StatsJsonFile = "%s/Stats/Stats.json" % run.s3_run_folder_path
        bucket, key = find_bucket_key(s3StatsJsonFile)
        if access(bucket, key) == False:
            return '{"Status": "error", "Message": "%s not found"}' % s3StatsJsonFile, 404
        data = s3.get_object(Bucket=bucket, Key=key)
        json_stats = json.loads(data['Body'].read())
        return jsonify(json_stats)

@NS.route("/<sequencing_run_id>/sample_sheet")
class SampleSheet(Resource):
    def get(sequencing_run_id):
        ss_json = {'Summary': {}, 'Header': {},
                   'Reads': {}, 'Settings': {},
                   'DataCols': [], 'Data': []}
        run = SequencingRun.query.get(sequencing_run_id)
        if run:
            ss_json['Summary'] = run.to_dict()
            sample_sheet_path = "%s/SampleSheet.csv" % run.s3_run_folder_path
            bucket, key = find_bucket_key(sample_sheet_path)
            if access(bucket, key):
                ss = SampleSheet(sample_sheet_path)
                ss = json.loads(ss.to_json())
                ss_json['Header'] = ss['Header']
                ss_json['Reads'] = ss['Reads']
                ss_json['Settings'] = ss['Settings']
                ss_json['DataCols'] = list(ss['Data'][0].keys())
                ss_json['Data'] = ss['Data']
        return jsonify(ss_json)

@NS.route("/<sequencing_run_id>/samples")
class Samples(Resource):
    def delete(sequencing_run_id):
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

    def put(sequencing_run_id):
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
            return '{"Status": "Not Found", "Message": "Run not found"}', 404

        if not request.json:
            return ('{"Status": "Bad Request", "Message": "No json data included in the '
                'request, or json data is empty"}', 400)

        new_runtosamples_objs = []

        # Do this in case there is only one mapping sent, and it is not formatted as a list
        if type(request.json) != list:
            request.json = [request.json]

        for mapping in request.json:
            run_to_samples_mapping = RunToSamples(sequencing_run_id=sequencing_run_id)

            if 'sampleid' in mapping:
                run_to_samples_mapping.sample_id = mapping['sampleid']
            else:
                return ('{"Status": "Bad Request", "Message": "All mappings in '
                        'request must include Samples to map to Sequencing Run"}', 400)

            if 'projectid' in mapping:
                projectid = mapping['projectid']
            else:
                projectid = None
            run_to_samples_mapping.project_id = projectid
            new_runtosamples_objs.append(run_to_samples_mapping)

        db.session.add_all(new_runtosamples_objs)

        try:
            db.session.commit()
            return jsonify({"Status": "OK", "Successful mappings": request.json}), 200
        except:
            db.session.rollback()
            return jsonify({"Status": "Internal Server Error",
                            "Message": "Run to Samples mappings could not be saved"}), 500

@NS.route("/<sequencing_run_id>/upload_features_file")
class UploadFeaturesFile(Resource):
    def post(sequencing_run_id):
        # Code from http://flask.pocoo.org/docs/1.0/patterns/fileuploads/
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file provided', 'danger')
            return 'OK', 200

        file = request.files['file']
        # if user does not select file, browser also submit an empty part without filename
        if file.filename == '':
            flash('No selected file', 'danger')
            return 'OK', 200

        run = SequencingRun.query.get(sequencing_run_id)
        if not run:
            abort(404)
        features_file = "%s/features.csv" % run.s3_run_folder_path
        bucket, key = find_bucket_key(features_file)
        boto3.clients['s3'].put_object(Body=file, Bucket=bucket, Key=key,
                                       ServerSideEncryption='AES256')
        flash('File uploaded', 'success')
        return 'OK', 200

@NS.route("/<sequencing_run_id>/upload_sample_sheet")
class UploadSampleSheet(Resource):
    def post(sequencing_run_id):
        # Code from http://flask.pocoo.org/docs/1.0/patterns/fileuploads/
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file provided', 'danger')
            return 'OK', 200

        file = request.files['file']
        # if user does not select file, browser also submit an empty part without filename
        if file.filename == '':
            flash('No selected file', 'danger')
            return 'OK', 200

        # Make sure samplesheet is a valid samplesheet
        # TODO: Simpilfy this code to use sample-sheet package.  If sample-sheet can read/parse
        # the sample sheet, then consider it valid.   Need to upgrade to Python3 for sample-sheet.
        (header, reads, settings, data) = (False, False, False, False)
        for line in file:
            if line.startswith('[Header]'):
                header = True
            if line.startswith('[Reads]'):
                reads = True
            if line.startswith('[Settings]'):
                settings = True
            if line.startswith('[Data]'):
                data = True
        file.seek(0)

        if header and reads and settings and data:
            run = SequencingRun.query.get(sequencing_run_id)
            if not run:
                abort(404)
            sample_sheet = "%s/SampleSheet.csv" % run.s3_run_folder_path
            bucket, key = find_bucket_key(sample_sheet)
            boto3.clients['s3'].put_object(Body=file, Bucket=bucket, Key=key,
                                           ServerSideEncryption='AES256')
            flash('Sample sheet uploaded', 'success')
        else:
            error_msg = "Invalid sample sheet. Header, Reads, Settings and/or Data section " + \
                        "is missing."
            flash(error_msg, 'danger')
        return 'OK', 200
