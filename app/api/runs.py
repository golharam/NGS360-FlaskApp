'''
Sequencing Runs
--------
    HTTP    URI           Action                              Implemented
    ----    ---           ------                              -----------
    GET     /api/v0/runs  Retrieve a list of sequencing runs  Runs.get()
    POST    /api/v0/runs  Create/Add a sequencing run         Runs.post()
'''
import datetime

from flask import abort, jsonify, request
from flask_restplus import Namespace, Resource

from app.models import SequencingRun

NS = Namespace('runs', description='Runs related operations')

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
