'''
Test /api/v0/runs endpoint
'''
import datetime
import unittest
from unittest import TestCase
from mock import patch
from moto import mock_s3
from app import create_app, DB as db, BOTO3 as boto3
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

    @mock_s3
    def test_get_run_metrics_notexist(self):
        response = self.client.get('/api/v0/runs/1/metrics')
        assert response.status_code == 404
        assert response.json == {"Status": "error", "Message": "Run not found"}

    @mock_s3
    def test_get_run_metrics_notdemuxed(self):
        run_date = datetime.date(2019, 1, 10)
        run = SequencingRun(id=1, run_date=run_date, machine_id='M00123',
                            run_number='1', flowcell_id='000000001',
                            experiment_name='PHIX3 test',
                            s3_run_folder_path='s3://somebucket/PHIX3_test')
        db.session.add(run)
        db.session.commit()

        boto3.resources['s3'].create_bucket(Bucket='somebucket')

        response = self.client.get('/api/v0/runs/1/metrics')
        assert response.status_code == 404
        assert response.json == {"Status": "error", "Message": "s3://somebucket/PHIX3_test/Stats/Stats.json not found"}

    @mock_s3
    def test_get_run_metrics(self):
        run_date = datetime.date(2019, 1, 10)
        run = SequencingRun(id=1, run_date=run_date, machine_id='M00123',
                            run_number='1', flowcell_id='000000001',
                            experiment_name='PHIX3 test',
                            s3_run_folder_path='s3://somebucket/PHIX3_test')
        db.session.add(run)
        db.session.commit()

        boto3.resources['s3'].create_bucket(Bucket='somebucket')
        boto3.clients['s3'].put_object(Bucket='somebucket',
                                       Key="/PHIX3_test/Stats/Stats.json",
                                       Body='{"metrics": "test"}')

        response = self.client.get('/api/v0/runs/1/metrics')
        assert response.status_code == 200
        assert response.json == {"metrics": "test"}

if __name__ == '__main__':
    unittest.main()
