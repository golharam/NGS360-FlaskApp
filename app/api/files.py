'''
NGS 360 Files
----------------
HTTP    URI                     Action
----    ---                     ------
GET     /api/v0/files           Retrieve a list of directories and files from S3 associated with a Project or Illumina Run
'''
import logging
from flask import request, abort, current_app, jsonify, redirect
from flask_login import current_user
from flask_restplus import Namespace, Resource
from app import BOTO3 as boto3
from app.models import Project, RunToSamples, SequencingRun

from botocore.exceptions import ClientError

NS = Namespace('files', description='File related operations')

@NS.route("")
class Files(Resource):
    def get(self):
        """
        Rest API to retrieve and return list of files associated with
        a Project or Illumina Run. This is gathered from an S3 endpoint
        using the BMS Project ID or Run ID.

        :param bucket: S3 Bucket
        :param prefix: Root path in bucket

        :return associated_files: JSON object with the files associated
        with this desired project or run
        """
        paginator = boto3.clients['s3'].get_paginator('list_objects')
        iterator = paginator.paginate(Bucket=request.args['bucket'],
                                    Prefix=request.args['prefix'], Delimiter='/')
        dirList = {"folders": [],
                   "files": []}
        for result in iterator:
            if "CommonPrefixes" in result:
                for o in result.get('CommonPrefixes'):
                    dirList['folders'].append({'name': o.get('Prefix'),
                                               'date': '-'})
            if "Contents" in result:
                for o in result.get('Contents'):
                    #tmp['key'] = o.get('Key')
                    #tmp['LastModified'] = str(o.get('LastModified'))
                    #objectList.append(tmp)
                    dirList['files'].append({'name': o.get('Key'),
                                             'date': str(o.get('LastModified')),
                                             'size': o.get('Size')
                    })
        return dirList

@NS.route("/download")
class DownloadFile(Resource):
    def get(self):
        """
        Rest API to download a file

        :param bucket: Bucket
        :param key: Key

        :return: redirect to pre-signed URL to download file
        """
        try:
            response = boto3.clients['s3'].generate_presigned_url('get_object',
                                                                  Params={'Bucket': request.args.get['bucket'],
                                                                          'Key': request.args.get['key']},
                                                                  ExpiresIn=10)
        except ClientError as e:
            logging.error(e)
            return None

        # The response contains the presigned URL
        return redirect(response, code=302)

