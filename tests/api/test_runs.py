'''
Test /api/v0/runs endpoint
'''
import datetime
from unittest import TestCase
from app import create_app, DB as db
from app.models import SequencingRun
from config import TestConfig

class RunsTests(TestCase):
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

    def test_get_run_metrics(self):
        run_date = datetime.date(2019, 1, 10)
        run = SequencingRun(id=1, run_date=run_date, machine_id='M00123',
                            run_number='1', flowcell_id='000000001',
                            experiment_name='PHIX3 test',
                            s3_run_folder_path='s3://somebucket/PHIX3_test')
        db.session.add(run)
        db.session.commit()

        response = self.client.get('/api/v0/runs/1/metrics')
        assert response.status_code == 404
