'''
Test /api/v0/runs endpoint
'''
import datetime
from io import BytesIO
import unittest
from unittest import TestCase
from moto import mock_s3, mock_batch, mock_iam
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
    def test_download_file(self):
        ''' Test GET /<sequencing_run_id>/file works '''
        run_date = datetime.date(2019, 1, 10)
        run = SequencingRun(id=1, run_date=run_date, machine_id='M00123',
                            run_number='1', flowcell_id='000000001',
                            experiment_name='PHIX3 test',
                            s3_run_folder_path='s3://somebucket/PHIX3_test')
        db.session.add(run)
        db.session.commit()

        boto3.resources['s3'].create_bucket(Bucket='somebucket')
        boto3.clients['s3'].upload_file(Filename="test_data/SampleSheet.csv",
                                        Bucket='somebucket',
                                        Key="/PHIX3_test/SampleSheet.csv")

        # Test if we don't provide a file, the response is http 400
        response = self.client.get('/api/v0/runs/1/file')
        assert response.status_code == 400

        # Test if we don't provide a valid run, the response is http 404
        response = self.client.get('/api/v0/runs/2/file?file=SampleSheet.csv')
        assert response.status_code == 404

        # Test we can download a file
        response = self.client.get('/api/v0/runs/1/file?file=SampleSheet.csv')
        # Check
        assert response.status_code == 200

        # Test if we don't provide a valid file, the response is http 404
        response = self.client.get('/api/v0/runs/1/file?file=nofile')
        assert response.status_code == 404

    @mock_s3
    def test_upload_file(self):
        ''' Test POST /<sequencing_run_id>/file works '''
        run_date = datetime.date(2019, 1, 10)
        run = SequencingRun(id=1, run_date=run_date, machine_id='M00123',
                            run_number='1', flowcell_id='000000001',
                            experiment_name='PHIX3 test',
                            s3_run_folder_path='s3://somebucket/PHIX3_test')
        db.session.add(run)
        db.session.commit()

        boto3.resources['s3'].create_bucket(Bucket='somebucket')

        files = {"file": (open("test_data/SampleSheet.csv", 'rb'), 'SampleSheet.csv'),
                 "filename": "SampleSheet.csv"
                }
        response = self.client.post('/api/v0/runs/1/file', data=files, content_type='multipart/form-data')
        assert response.json['status'] == 'File, SampleSheet.csv, uploaded'

    def test_get_runs(self):
        run_date = datetime.date(2019, 1, 10)
        run = SequencingRun(id=1, run_date=run_date, machine_id='M00123',
                            run_number='1', flowcell_id='000000001',
                            experiment_name='PHIX3 test',
                            s3_run_folder_path='s3://somebucket/PHIX3_test')
        db.session.add(run)
        run_date = datetime.date(2019, 2, 15)
        run = SequencingRun(id=2, run_date=run_date, machine_id='M00123',
                            run_number='2', flowcell_id='A',
                            experiment_name='PHIX3 test',
                            s3_run_folder_path='s3://somebucket/PHIX3_test')
        db.session.add(run)
        db.session.commit()
        # Get all runs
        response = self.client.get('/api/v0/runs')
        assert len(response.json['runs']) == 2
        # Get a specific run
        response = self.client.get('/api/v0/runs?run_barcode=190110_M00123_0001_000000001')
        assert len(response.json['runs']) == 1
        # Assert invalid barcode is caught
        response = self.client.get('/api/v0/runs?run_barcode=1')
        assert response.status_code == 400
        # Fetch an unknown run
        response = self.client.get('/api/v0/runs?run_barcode=190110_M00124_0001_000000001')
        assert response.status_code == 404

    def test_post_runs(self):
        data = {
            's3_run_folder_path': 's3://somebucket/PHIX3_test',
            'run_date': '190215',
            'machine_id': 'M00123',
            'run_number': '2',
            'flowcell_id': 'A',
            'experiment_name': 'PHIX3 test'}
        response = self.client.post('/api/v0/runs', json=data)
        self.assertEqual(response.status_code, 201)

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
        assert response.json == {"Status": "error",
                                 "Message": "s3://somebucket/PHIX3_test/Stats/Stats.json not found"}

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

    def test_get_samplesheet_norunexists(self):
        response = self.client.get('/api/v0/runs/1/sample_sheet')
        assert response.status_code == 200
        assert response.json == {'Summary': {}, 'Header': {},
                                 'Reads': {}, 'Settings': {},
                                 'DataCols': [], 'Data': []} 

    @mock_s3
    def test_get_samplesheet_runexists_nosamplesheet(self):
        run_date = datetime.date(2019, 1, 10)
        run = SequencingRun(id=1, run_date=run_date, machine_id='M00123',
                            run_number='1', flowcell_id='000000001',
                            experiment_name='PHIX3 test',
                            s3_run_folder_path='s3://somebucket/PHIX3_test')
        db.session.add(run)
        db.session.commit()
        boto3.resources['s3'].create_bucket(Bucket='somebucket')

        response = self.client.get('/api/v0/runs/1/sample_sheet')
        assert response.status_code == 404

    @mock_s3
    def test_get_samplesheet(self):
        run_date = datetime.date(2019, 1, 10)
        run = SequencingRun(id=1, run_date=run_date, machine_id='M00123',
                            run_number='1', flowcell_id='000000001',
                            experiment_name='PHIX3 test',
                            s3_run_folder_path='s3://somebucket/PHIX3_test')
        db.session.add(run)
        db.session.commit()
        boto3.resources['s3'].create_bucket(Bucket='somebucket')
        boto3.clients['s3'].upload_file(Filename="test_data/SampleSheet.csv",
                                        Bucket='somebucket',
                                        Key="/PHIX3_test/SampleSheet.csv")
        # Test
        response = self.client.get('/api/v0/runs/1/sample_sheet')
        # Check
        assert response.status_code == 200
        assert response.json == {'Summary': {'experiment_name': 'PHIX3 test',
                                             'flowcell_id': '000000001',
                                             'id': 1,
                                             'machine_id': 'M00123',
                                             'run_date': '2019-01-10',
                                             'run_number': '1',
                                             's3_run_folder_path': 's3://somebucket/PHIX3_test'},
                                 'Header': {'Application': 'FASTQ Only',
                                            'Assay': 'someassay',
                                            'Chemistry': 'Amplicon',
                                            'Date': '1/8/2018',
                                            'Description': 'PHIX3 test',
                                            'Experiment Name': 'PHIX3 test',
                                            'IEMFileVersion': '4',
                                            'Investigator Name': 'John',
                                            'Workflow': 'GenerateFASTQ'},
                                 'Reads': [151, 151],
                                 'Settings': {'Adapter': 'CTGTCTCTTATACACATCT',
                                              'ReverseComplement': '0'},
                                 'DataCols': ['Sample_ID', 'Sample_Name', 'Sample_Plate',
                                              'Sample_Well', 'I7_Index_ID', 'index', 'I5_Index_ID',
                                              'index2', 'Sample_Project', 'Description'],
                                 'Data': [{'Description': '',
                                           'I5_Index_ID': 'S502-A',
                                           'I7_Index_ID': 'N701-A',
                                           'Sample_ID': 'sample1',
                                           'Sample_Name': 'sample1',
                                           'Sample_Plate': '',
                                           'Sample_Project': 'P-00000000-0001',
                                           'Sample_Well': '',
                                           'index': 'TAAGGCGA',
                                           'index2': 'CTCTCTAT'}]
                                }

    def test_post_demultiplex_anonymous_user(self):
        ''' Test that anonymous user cannot demux run '''
        # Set up test case
        # Set up supporting mocks
        # Test
        response = self.client.post('/api/v0/runs/1/demultiplex')
        # Check results
        self.assertEqual(response.status_code, 404)

    def test_post_demultiplex_std_bcl2fastq_nonexistentrun(self):
        ''' Test that user can demux run '''
        # Set up test case
        # Set up supporting mocks
        # Test
        response = self.client.post('/api/v0/runs/1/demultiplex?user=testuser')
        # Check results
        self.assertEqual(response.status_code, 404)

    @mock_iam
    @mock_batch
    def test_post_demultiplex_std_bcl2fastq(self):
        ''' Test that user can demux run '''
        # Set up test case
        # Set up supporting mocks
        boto3.clients['batch'].register_job_definition(
            jobDefinitionName="job",
            type="container",
            containerProperties={
                "image": "busybox",
                "vcpus": 1,
                "memory": 128,
                "command": ["sleep", "10"],
            })
        resp = boto3.clients["iam"].create_role(
            RoleName="TestRole", AssumeRolePolicyDocument="some_policy")
        iam_arn = resp["Role"]["Arn"]
        env = boto3.clients['batch'].create_compute_environment(
            computeEnvironmentName='compute_name',
            type="UNMANAGED",
            state="ENABLED",
            serviceRole=iam_arn)
        boto3.clients['batch'].create_job_queue(
            jobQueueName="queue",
            state="ENABLED",
            priority=123,
            computeEnvironmentOrder=[{"order": 123, "computeEnvironment": env['computeEnvironmentArn']}])

        self.app.config['BCL2FASTQ_JOB'] = "job"
        self.app.config['BCL2FASTQ_QUEUE'] = "queue"
        run_date = datetime.date(2019, 1, 10)
        run = SequencingRun(id=1, run_date=run_date, machine_id='M00123',
                            run_number='1', flowcell_id='000000001',
                            experiment_name='PHIX3 test',
                            s3_run_folder_path='s3://somebucket/PHIX3_test')
        db.session.add(run)
        db.session.commit()
        # Test
        response = self.client.post('/api/v0/runs/1/demultiplex?user=testuser')
        # Check results
        self.assertEqual(response.status_code, 200)
        self.assertTrue('jobName' in response.json)
        self.assertTrue('jobId' in response.json)

if __name__ == '__main__':
    unittest.main()
