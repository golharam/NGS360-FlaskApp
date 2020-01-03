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
