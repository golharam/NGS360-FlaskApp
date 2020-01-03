'''
Notifications Endpoint
'''
import datetime
from flask import Blueprint, request, jsonify, abort
from app import DB as db
from app.models import BatchJob, Notification, SequencingRun

BP = Blueprint('api', __name__)

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
