'''
Test server-side endpoints in app.blueprints.api.v0.notifications
'''
import json
from unittest import TestCase
from app import create_app, DB as db
from app.models import Notification
from config import TestConfig

class BlueprintNotificationsTests(TestCase):
    ''' Test cases for notifications endpoint '''
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.client = None
        self.app_context.pop()

    def test_get_user_notifications(self):
        ''' Test when no user is specified '''
        notification1 = Notification(user='testuser', batchjob_id=1, seen=True)
        notification2 = Notification(user='testuser', batchjob_id=2, seen=True)
        notification3 = Notification(user='testuser', batchjob_id=3, seen=False)
        db.session.add_all([notification1, notification2, notification3])
        db.session.commit()
        response = self.client.get('/api/v0/users/testuser/notifications')
        assert len(response.json) == 3

    def test_get_user_notifications_seen(self):
        ''' Test when no user is specified '''
        notification1 = Notification(user='testuser', batchjob_id=1, seen=True)
        notification2 = Notification(user='testuser', batchjob_id=2, seen=True)
        notification3 = Notification(user='testuser', batchjob_id=3, seen=False)
        notification4 = Notification(user='anotheruser', batchjob_id=1, seen=False)
        db.session.add_all([notification1, notification2, notification3, notification4])
        db.session.commit()
        response = self.client.get('/api/v0/users/testuser/notifications?seen=True')
        assert len(response.json) == 2

    def test_get_user_notifications_notseen(self):
        ''' Test when no user is specified '''
        notification1 = Notification(user='testuser', batchjob_id=1, seen=True)
        notification2 = Notification(user='testuser', batchjob_id=2, seen=True)
        notification3 = Notification(user='testuser', batchjob_id=3, seen=False)
        notification4 = Notification(user='anotheruser', batchjob_id=1, seen=False)
        db.session.add_all([notification1, notification2, notification3, notification4])
        db.session.commit()
        response = self.client.get('/api/v0/users/testuser/notifications?seen=False')
        assert len(response.json) == 1

    def test_get_user_notifications_none(self):
        ''' Test when no user is specified '''
        response = self.client.get('/api/v0/users/testuser/notifications')
        assert len(response.json) == 0

    def test_clear_user_notifications(self):
        ''' Test a users notifications seen to 0 '''
        # Set up
        notification1 = Notification(user='testuser', batchjob_id=1, seen=True)
        notification2 = Notification(user='testuser', batchjob_id=2, seen=True)
        notification3 = Notification(user='testuser', batchjob_id=3, seen=False)
        notification4 = Notification(user='anotheruser', batchjob_id=1, seen=False)
        db.session.add_all([notification1, notification2, notification3, notification4])
        db.session.commit()
        # Test
        self.client.get('/api/v0/users/testuser/notifications/clear')
        # Check
        notifications = Notification.query.filter_by(user='testuser').filter_by(seen=True)
        count = 0
        for _ in notifications:
            count += 1
        assert count == 3

    def test_update_notification(self):
        ''' Test that we can set the seen state of a notification '''
        # Set up
        notification1 = Notification(id=1, user='testuser', batchjob_id=1, seen=True)
        notification = Notification(id=2, user='testuser', batchjob_id=3, seen=False)
        db.session.add_all([notification1, notification])
        db.session.commit()
        # Test
        response = self.client.put('/api/v0/notifications/%s' % notification.id,
                                   data=json.dumps({"seen": True}),
                                   content_type='application/json')

        # Check
        assert response.status_code == 200
        notifications = Notification.query.filter_by(user='testuser').filter_by(seen=True)
        count = 0
        for _ in notifications:
            count += 1
        assert count == 2

    def test_update_notification_nojson(self):
        ''' Test that we can handle no JSON being passed '''
        response = self.client.put('/api/v0/notifications/1')
        assert response.status_code == 400

    def test_update_notification_incorrectjson(self):
        ''' Test that we can handle no JSON being passed '''
        response = self.client.put('/api/v0/notifications/1',
                                   data=json.dumps({"anothervar": "x"}),
                                   content_type='application/json')
        assert response.status_code == 400

    def test_update_notification_notfound(self):
        notification = Notification(id=1, user='testuser', batchjob_id=1, seen=False)
        db.session.add(notification)
        db.session.commit()
        response = self.client.put('/api/v0/notifications/2',
                                   data=json.dumps({"seen": True}),
                                   content_type='application/json')
        assert response.status_code == 404
