'''
Notifications Endpoint
'''
import datetime
from flask import Blueprint, request, jsonify, abort
from app import DB as db
from app.models import BatchJob, Notification, SequencingRun

BP = Blueprint('api', __name__)

@BP.route("/api/v0/users/<string:userid>/notifications", methods=["GET"])
def get_user_notifications(userid):
    '''
    Returns a list of notification for a user.  Query string can contain options:

    :param seen: True/False - This option restricts what notifications are returned
    '''
    if 'seen' in request.args:
        seen = bool(request.args.get('seen').lower().startswith('t'))
        notifications = Notification.query.filter_by(user=userid).filter_by(seen=seen).all()
    else:
        notifications = Notification.query.filter_by(user=userid).all()
    if not notifications:
        return jsonify([])
    return jsonify([notification.to_dict() for notification in notifications])

@BP.route("/api/v0/users/<string:userid>/notifications/clear", methods=["GET"])
def clear_user_notifications(userid):
    '''
    Clear/Reset the user's notifications
    '''
    Notification.query.filter_by(user=userid).filter_by(seen=False).update(dict(seen=True))
    db.session.commit()
    return '{"Status": "Notifications cleared"}', 200

@BP.route("/api/v0/users/<string:userid>/notification_joblist", methods=["GET"])
def get_user_notification_jobs(userid):
    '''
    Return a list of jobs based on occurred_on notification datetime, e.g.,
    SELECT batch_job.name, notification.batchjob_id, notification.occurred_on, batch_job.viewed
           FROM notification, batch_job
           WHERE notification.user='testuser' AND notification.batchjob_id=batch_job.id
           ORDER BY notification.occurred_on DESC
           LIMIT 10

    Query string can contain the following arguments:
    :param limit: Limit the number of records returned
    :param order: Order the records by occurred_on
    '''
    # https://www.reddit.com/r/flask/comments/50zk7p/sql_alchemy_join_the_tables/
    notified_job_list = db.session.query(Notification.batchjob_id, BatchJob.viewed, 
                                         Notification.occurred_on, BatchJob.name) \
                          .join(BatchJob, Notification.batchjob_id == BatchJob.id) \
                          .filter_by(user=userid)

    # https://stackoverflow.com/questions/27900018/flask-sqlalchemy-query-join-relational-tables
    #notified_job_list = Notification.query.
    #                      .join(BatchJob, Notification.batchjob_id==BatchJob.id)
    #                      .select(Notification.batchjob_id, BatchJob.viewed)
    #                      .filter_by(user=userid)

    if 'order' in request.args:
        if request.args['order'] == 'desc':
            notified_job_list = notified_job_list.order_by(Notification.occurred_on.desc())
        else:
            notified_job_list = notified_job_list.order_by(Notification.occurred_on.asc())

    if 'limit' in request.args:
        notified_job_list = notified_job_list.limit(request.args['limit'])

    notified_job_list = notified_job_list.all()
    json_response = []
    for notified_job in notified_job_list:
        jnj = {'batchjob_id': notified_job[0],
               'viewed': notified_job[1],
               'occurred_on': notified_job[2].isoformat() + 'Z',
               'name': notified_job[3]}
        json_response.append(jnj)
    return jsonify(json_response), 200

@BP.route("/api/v0/notifications/<int:notificationid>", methods=["PUT"])
def update_notification(notificationid):
    ''' Update notification seen state '''
    # TODO: Secure with auth_tokens
    if not request.json:
        return '{"Status": "JSON not found"}', 400
    if not 'seen' in request.json:
        return '{"Status": "JSON not found"}', 400
    notification = Notification.query.filter_by(id=notificationid).first()
    if not notification:
        return '{"Status": "Notification not found"}', 404
    notification.seen = request.json['seen']
    db.session.add(notification)
    db.session.commit()
    return jsonify(notification.to_dict()), 200

@BP.route("/api/v0/runs", methods=["GET"])
def get_runs():
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
        else:
            abort(404)
    else:
        runs = SequencingRun.query.all()
    return jsonify({'runs': [run.to_dict() for run in runs]}), 200

@BP.route("/api/v0/runs", methods=["POST"])
def create_run():
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
