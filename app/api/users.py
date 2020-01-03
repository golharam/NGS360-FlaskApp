from flask import request, jsonify
from flask_restplus import Namespace, Resource
from app import DB as db
from app.models import BatchJob, Notification

NS = Namespace('users', description='User related operations')

@NS.route("/<string:userid>/notifications")
class UserNotifications(Resource):
    def get(userid):
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

@NS.route("/<string:userid>/notifications/clear")
class UserNotificationsClear(Resource):
    def get(userid):
        '''
        Clear/Reset the user's notifications
        '''
        Notification.query.filter_by(user=userid).filter_by(seen=False).update(dict(seen=True))
        db.session.commit()
        return '{"Status": "Notifications cleared"}', 200

@NS.route("/<string:userid>/notification_joblist")
class UserNotificationJobList(Resource):
    def get(userid):
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
