from unittest import TestCase
import datetime

from config import TestConfig
from app import create_app, DB as db
from app.models import Project, SequencingRun, RunToSamples

class ProjectsTests(TestCase):
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

    def test_get_project_noprojectexists(self):
        # Test
        response = self.client.get('/api/v0/projects/P-00000000-0001')
        # Check
        assert response.status_code == 200
        assert response.json == {}

    def test_get_project(self):
        # Set up test case
        # Set up supporting mocks
        project = Project(id='P-00000000-0001', xpress_project_id=12345)
        db.session.add(project)

        run_date = datetime.date(2019, 1, 10)
        run = SequencingRun(id=1, run_date=run_date, machine_id='M00123',
                            run_number='1', flowcell_id='000000001',
                            experiment_name='PHIX3 test',
                            s3_run_folder_path='s3://somebucket/PHIX3_test')
        db.session.add(run)

        run_to_samples = RunToSamples(id=1, sequencing_run_id=1, sample_id='sample_a', project_id='P-00000000-0001')
        db.session.add(run_to_samples)

        db.session.commit()
        # Test
        response = self.client.get('/api/v0/projects/P-00000000-0001')
        # Check
        assert response.status_code == 200
        assert response.json == {'id': 'P-00000000-0001',
                                 'rnaseq_qc_report': None,
                                 'sequencing_runs': [{'experiment_name': 'PHIX3 test',
                                                      'flowcell_id': '000000001',
                                                      'id': 1,
                                                      'machine_id': 'M00123',
                                                      'run_date': '2019-01-10',
                                                      'run_number': '1',
                                                      's3_run_folder_path': 's3://somebucket/PHIX3_test'}],
                                 'wes_qc_report': None,
                                 'xpress_project_id': 12345}

    def test_put_project_no_json(self):
        # Test
        response = self.client.put('/api/v0/projects/P-00000000-0001')
        # Check
        assert response.status_code == 404

    def test_put_project_unknown_json(self):
        json_data = {'some': 'tag'}
        # Test
        response = self.client.put('/api/v0/projects/P-00000000-0001', json=json_data)
        # Check
        assert response.status_code == 404

    def test_put_project(self):
        # Set up test case
        projectid = 'P-00000000-0001'
        json_data = {'xpress_project_id': 12345}
        # Set up supporting mocks
        # Test
        response = self.client.put('/api/v0/projects/%s' % projectid, json=json_data)
        # Check
        assert response.status_code == 201
        db_project = Project.query.filter_by(id=projectid).first()
        assert db_project.xpress_project_id == 12345

    def test_put_project_updatexpress(self):
        # Set up test case
        projectid = 'P-00000000-0001'
        json_data = {'xpress_project_id': 12345}
        # Set up supporting mocks
        project = Project(id=projectid, xpress_project_id=11111)
        db.session.add(project)
        db.session.commit()
        # Test
        response = self.client.put('/api/v0/projects/%s' % projectid, json=json_data)
        # Check
        assert response.status_code == 201
        db_project = Project.query.filter_by(id=projectid).first()
        assert db_project.xpress_project_id == 12345