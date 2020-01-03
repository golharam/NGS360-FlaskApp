from flask import request, jsonify
from flask_restplus import Namespace, Resource
from app import DB as db
from app.models import Notification

NS = Namespace('notifications', description='Notification related operations')

@NS.route("/<int:notificationid>")
class UserNotification(Resource):
    def put(notificationid):
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
