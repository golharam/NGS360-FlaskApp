'''
REST Endpoint for /api/v0/notifications
'''
from flask import request
from flask_restplus import Namespace, Resource
from app import DB as db
from app.models import Notification

NS = Namespace('notifications', description='Notification related operations')

@NS.route("/<int:notification_id>")
class UserNotification(Resource):
    def put(self, notification_id):
        ''' Update notification seen state '''
        # TODO: Secure with auth_tokens
        if not request.json:
            return '{"Status": "JSON not found"}', 400
        if not 'seen' in request.json:
            return '{"Status": "JSON not found"}', 400
        notification = Notification.query.filter_by(id=notification_id).first()
        if not notification:
            return '{"Status": "Notification not found"}', 404
        notification.seen = request.json['seen']
        db.session.add(notification)
        db.session.commit()
        return notification.to_dict()
