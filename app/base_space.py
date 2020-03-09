"""
BaseSpace interface to BaseSpace REST API, v1pre3

Author: Ryan Golhar <ryan.golhar@bms.com>
"""
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
import json

def get_json(url):
    """ Return JSON object from URL """
    try:
        response = urlopen(url)
    except (HTTPError, URLError):
        return None
    data = json.load(response)
    return data

class BaseSpace:
    ''' Interface class to BaseSpace '''
    def __init__(self, api_endpoint=None, access_token=None):
        self.app = None
        self.api_endpoint = api_endpoint
        self.access_token = access_token
        self.userid = self.get_user_id()

    def init_app(self, app):
        ''' Mimicks the init_app for Flask apps '''
        self.app = app
        self.api_endpoint = app.config.get('BASESPACE_ENDPOINT')
        self.access_token = app.config.get('BASESPACE_TOKEN')
        self.userid = self.get_user_id()
        self.app.logger.debug("BaseSpace User ID: %s", self.userid)

    def get_user_id(self):
        """ Return the current user's id """
        self.userid = None
        if self.api_endpoint and self.access_token:
            url = '%s/users/current?access_token=%s' % (self.api_endpoint, self.access_token)
            self.app.logger.debug("Getting user id from %s", url)
            data = get_json(url)
            if data and 'Response' in data:
                self.userid = data['Response']['Id']
        return self.userid

    def get_paginated_results(self, url):
        retval = []
        limit = 1024
        offset = 0
        while True:
            paginated_url = '%s?Limit=%s&Offset=%s&access_token=%s' % (url, limit, offset,
                                                                       self.access_token)
            self.app.logger.debug("Calling %s", paginated_url)
            data = get_json(paginated_url)
            if not data:
                break
            response = data['Response']
            items = response['Items']
            for item in items:
                retval.append(item)
            if response['DisplayedCount'] + offset == response['TotalCount']:
                break
            offset += response['DisplayedCount']
        return retval

    def get_runs(self):
        """ Returns a list of runs """
        if self.userid:
            url = '%s/users/%s/runs' % (self.api_endpoint, self.userid)
            runs = self.get_paginated_results(url)
        else:
            runs = []
        return runs
        
    def get_projects(self):
        """
        Returns a list of project.  Assumes get_user_id was called during initialization.
        """
        if self.userid:
            url = '%s/users/%s/projects' % (self.api_endpoint, self.userid)
            self.app.logger.debug("Retrieving list of projects from %s", url)
            projects = self.get_paginated_results(url)
        else:
            projects = []
        return projects

    def get_project_id(self, project_name):
        """ Return a project's id based on its name """
        projects = self.get_projects()
        # find the project with the request name
        for project in projects:
            if project['Name'] == project_name:
                return project['Id']
        return None

    def get_project_samples(self, projectid):
        """ Returns a list of samples for a BaseSpace projectid
        :param projectid: BaseSpace Project ID
        :return: JSON list of sample names and IDs
        """
        retVal = []
        url = '%s/projects/%s/samples' % (self.api_endpoint, projectid)
        self.app.logger.debug("Getting list of samples in project from %s", url)
        data = self.get_paginated_results(url)
        if data:
            for sample in data:
                retVal.append({'Name': sample['Name'], 'Id': sample['Id']})
        return retVal

'''
    def getRun(self, runID):
        """ Return a run """
        logger.debug("Retrieving run")
        # Since I am retrieving 1 run, I don't believe I need a limit of offset
        url = '%s/runs/%s?access_token=%s' % (self.baseUrl,
                                              runID,
                                              self.accessToken)
        data = getJSON(url)
        return data['Response']

    def getSampleFastqFiles(self, sampleid):
        """ Returns the fastq files for a sample """
        logger.debug("getSampleFastqFiles")
        url = "%s/samples/%s/files?Limit=1024&Offset=0&access_token=%s" % (self.baseUrl,
                                                                           sampleid,
                                                                           self.accessToken)
        data = getJSON(url)
        files = data['Response']['Items']
        return files
'''
