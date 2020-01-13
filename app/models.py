'''
Database model
'''
# pylint: disable=C0116
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from app import DB as db, LOGINMANAGER as login

class BatchJob(db.Model):
    '''
    Represeents an AWS Batch Job, where id is the AWS Batch Job ID.
    If this gets updated, make sure to update in batchEventTrigger-lambda function
    '''
    id = db.Column(db.VARCHAR(45), primary_key=True)
    name = db.Column(db.VARCHAR(255))
    command = db.Column(db.VARCHAR(1024))
    user = db.Column(db.VARCHAR(12))
    submitted_on = db.Column(db.DATETIME(), default=datetime.utcnow)
    log_stream_name = db.Column(db.VARCHAR(255))
    status = db.Column(db.VARCHAR(15))
    viewed = db.Column(db.BOOLEAN(), default=True, nullable=False)

    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'command': self.command,
            'user': self.user,
            'submitted_on': self.submitted_on.isoformat() + 'Z',
            'log_stream_name': self.log_stream_name,
            'status': self.status,
            'viewed': self.viewed
        }
        return data

    def from_dict(self, data):
        for field in ['log_stream_name']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return '<BatchJob {}>'.format(self.id)

class Notification(db.Model):
    '''
    This class/table represents a notification to a user
    '''
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.VARCHAR(12))
    batchjob_id = db.Column(db.VARCHAR(45))
    seen = db.Column(db.BOOLEAN(), default=False)
    occurred_on = db.Column(db.DATETIME(), default=datetime.utcnow)

    def to_dict(self):
        data = {
            'id': self.id,
            'user': self.user,
            'batchjob_id': self.batchjob_id,
            'seen': self.seen,
            'occurred_on': self.occurred_on.isoformat() + 'Z'
        }
        return data

    def from_dict(self, data):
        for field in ['user', 'batchjob_id', 'seen', 'occurred_on']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return '<Notification {}>'.format(self.id)

class Project(db.Model):
    '''
    Represents BMS Genomics Project, where id is BMS ProjectID
    '''
    id = db.Column(db.VARCHAR(50), primary_key=True)
    rnaseq_qc_report = db.Column(db.VARCHAR(255), default=None)
    wes_qc_report = db.Column(db.VARCHAR(255), default=None)
    xpress_project_id = db.Column(db.INT, default=None)

    def to_dict(self):
        data = {
            'id': self.id,
            'rnaseq_qc_report_url': self.rnaseq_qc_report,
            'wes_qc_report_url': self.wes_qc_report,
            'xpress_project_id': self.xpress_project_id
        }
        return data

    def from_dict(self, data):
        for field in ['rnaseq_qc_report', 'wes_qc_report', 'xpress_project_id']:
            if field in data:
                setattr(self, field, data[field])

    def __repr__(self):
        return '<Project {}>'.format(self.id)

class ProjectSample(db.Model):
    """
    Model to store Sample to Project association.  Attributes, such as the read files
    (R1, and possibly R2 as well) associated with the Sample, will be in a seperate table.
    """
    id = db.Column(db.Integer, primary_key=True)
    sample_id = db.Column(db.VARCHAR(100), nullable=False)
    project_id = db.Column(db.VARCHAR(50), default=None)

    def to_dict(self):
        data = {
            'id': self.id,
            'sample_id': self.sample_id,
            'project_id': self.project_id,
            '_href': '/api/v0/samples/%s' % self.id
        }
        return data

    def __repr__(self):
        return 'ProjectSample object with Sample ID {} and Project ID {}'.format(
            self.sample_id, self.project_id)

class RunToSamples(db.Model):
    """
    Model for database table that maps SequencingRuns to Sample IDs
    and Project IDs. For now, the Project IDs and Sample IDs are stored
    as strings (VARCHAR), in case the Project associated with the Run
    does not exist in the database yet.
    """
    id = db.Column(db.Integer, primary_key=True)
    sequencing_run_id = db.Column(db.Integer, db.ForeignKey('sequencing_run.id'))
    sample_id = db.Column(db.VARCHAR(512), default=None)
    project_id = db.Column(db.VARCHAR(50), default=None)

    def to_dict(self):
        return {
            'id': self.id,
            'sequencing_run_id': self.sequencing_run_id,
            'sample_id': self.sample_id,
            'project_id': self.project_id
        }

    def from_dict(self, data):
        for field in data:
            setattr(self, field, data[field])

    def __repr__(self):
        return ('<RunToSamples mapping with SequencingRun {}, Sample ID {},'
                ' and Project ID {}>'.format(self.sequencing_run_id, self.sample_id,
                                             self.project_id))

class SequencingRun(db.Model):
    '''
    This class/table represents an Illumina sequencing run
    '''
    id = db.Column(db.Integer, primary_key=True)
    run_date = db.Column(db.DATE)
    machine_id = db.Column(db.VARCHAR(25))
    run_number = db.Column(db.VARCHAR(5))
    flowcell_id = db.Column(db.VARCHAR(25))
    experiment_name = db.Column(db.VARCHAR(255))
    s3_run_folder_path = db.Column(db.VARCHAR(255))

    @staticmethod
    def is_data_valid(data):
        for field in ['experiment_name', 's3_run_folder_path']:
            if field not in data:
                return False
        return True

    def to_dict(self):
        data = {
            'id': self.id,
            'run_date': self.run_date.strftime("%Y-%m-%d"),
            'machine_id': self.machine_id,
            'run_number': self.run_number,
            'flowcell_id': self.flowcell_id,
            'experiment_name': self.experiment_name,
            's3_run_folder_path': self.s3_run_folder_path
        }
        return data

    def from_dict(self, data):
        for field in data:
            setattr(self, field, data[field])

    def __repr__(self):
        return '<SequencingRun {}>'.format(self.id)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
