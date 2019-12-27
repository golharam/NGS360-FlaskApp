'''
Notifications Endpoint
'''
from flask import Blueprint, request, jsonify
from app import DB as db
from app.models import Notification

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
