from unittest import TestCase
from unittest.mock import patch
from datetime import datetime
from app import create_app, DB as db
from app.models import BatchJob
from config import TestConfig

class JobTests(TestCase):
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

    def test_get_jobs(self):
        job = BatchJob(id='1',
                       name='name',
                       command='command',
                       user='user',
                       submitted_on=datetime.utcnow(),
                       log_stream_name='asf',
                       status='qwer',
                       viewed=1)
        db.session.add(job)
        db.session.commit()

        response = self.client.get("/api/v0/jobs")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)

    def test_post_jobs(self):
        data = {
            'id': '12345',
            'name': 'ajob',
            'command': 'acommand',
            'user': 'auser',
            'status': 'some_status'
        }
        response = self.client.post("/api/v0/jobs", json=data)
        self.assertEqual(response.status_code, 201)
        self.assertTrue('job' in response.json)

    def test_get_job(self):
        response = self.client.get("/api/v0/jobs/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {})

        job = BatchJob(id='1',
                       name='name',
                       command='command',
                       user='user',
                       submitted_on=datetime.utcnow(),
                       log_stream_name='asf',
                       status='qwer',
                       viewed=1)
        db.session.add(job)
        db.session.commit()
        response = self.client.get("/api/v0/jobs/1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, job.to_dict())

    def test_put_job(self):
        job = BatchJob(id='1',
                       name='name',
                       command='command',
                       user='user',
                       submitted_on=datetime.utcnow(),
                       log_stream_name='asf',
                       status='qwer',
                       viewed=1)
        db.session.add(job)
        db.session.commit()

        data = {'log_stream_name': 'log_stream_name',
                'job_status': 'SUCCEEDED'}
        response = self.client.put("/api/v0/jobs/1", json=data)
        self.assertEqual(response.status_code, 200)

    def test_get_job_log(self):
        response = self.client.get("/api/v0/jobs/1/log")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, ["Unknown job"])

        job = BatchJob(id='1',
                       name='name',
                       command='command',
                       user='user',
                       submitted_on=datetime.utcnow(),
                       status='qwer',
                       viewed=1)
        db.session.add(job)
        db.session.commit()
        response = self.client.get("/api/v0/jobs/1/log")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, ["No log (yet) available"])

        job.log_stream_name = "asdf"
        db.session.commit()
        with patch('app.api.jobs.get_log_events') as mock_get_log_events:
            mock_get_log_events.return_value = ["event1", "event2"]
            response = self.client.get("/api/v0/jobs/1/log")
        self.assertEqual(response.status_code, 200)
