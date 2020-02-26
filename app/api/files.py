'''
NGS 360 Files
----------------
HTTP    URI                     Action
----    ---                     ------
GET     /api/v0/files           Retrieve a list of directories and files from S3 associated with a Project or Illumina Run
'''
from flask import request, abort, current_app, jsonify
from flask_login import current_user
from flask_restplus import Namespace, Resource
from app.models import Project, RunToSamples, SequencingRun

NS = Namespace('files', description='File related operations')

@NS.route("")
class Files(Resource):
    def get(self):
        """
        Rest API to retrieve and return list of files associated with
        a Project or Illumina Run. This is gathered from an S3 endpoint
        using the BMS Project ID or Run ID.

        ***TODO: For the moment, this method just returns a sample filesystem.
        The mechanism to retrieve the related files from S3 needs to be implemented.

        :param run: Associated Illumina run
        :param project: Associated project
        :param bucket: S3 Bucket
        :param path: Root path in bucket

        :return associated_files: JSON object with the files associated
        with this desired project or run
        """
        # sample_filesystem based on sample filesystem at:
        # https://realpython.com/working-with-files-in-python/
        # Any filesystem should be able to be converted to this type
        # of data structure
        sample_filesystem = {
            'folders': [
                {'name': 'sub_dir_a', 'files': [{'name': 'bar.py', 'date': '', 'size': '76KB'}, {'name': 'foo.py', 'date': '', 'size': '76KB'}]},
                {'name': 'sub_dir_b', 'files': [{'name': 'file4.txt', 'date': '', 'size': '76KB'}]},
                {'name': 'sub_dir_c', 'folders': [{'name': 'sub_dir_c1', 'files': [{'name': 'file6.txt', 'date': '', 'size': '76KB'},
                                                                                   {'name': 'file7.csv', 'date': '', 'size': '76KB'}]}],
                                      'files': [{'name': 'config.py', 'date': '', 'size': '76KB'}, {'name': 'file5.txt', 'date': '', 'size': '76KB'}]},
            ],
            'files': [{'name': 'file1.py', 'date': '', 'size': '76KB'}, {'name': 'file2.csv', 'date': '', 'size': '76KB'}, {'name': 'file3.txt', 'date': '', 'size': '76KB'}]
        }

        return jsonify(sample_filesystem)

