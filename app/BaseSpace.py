"""
BaseSpace interface to BaseSpace REST API, v1pre3

Author: Ryan Golhar <ryan.golhar@bms.com>
"""
from urllib.request import urlopen
from urllib.error import HTTPError
import json

def get_json(url):
    """ Return JSON object from URL """
    try:
        response = urlopen(url)
    except HTTPError:
        return None
    data = json.load(response)
    return data

class BaseSpace:
    ''' Interface class to BaseSpace '''
    def __init__(self,
                 api_endpoint='http://api.basespace.illumina.com',
                 api_endpoint_version='v1pre3',
                 access_token=None):
        self.api_endpoint = api_endpoint
        self.api_endpoint_version = api_endpoint_version
        self.base_url = '%s/%s' % (self.api_endpoint, self.api_endpoint_version)
        self.access_token = access_token
        self.userid = None
        self.app = None
        if access_token:
            # This is needed because other calls rely on self.userid
            self.get_user_id()

    def init_app(self, app):
        ''' Mimicks the init_app for Flask apps '''
        self.app = app
        if 'BASESPACE_TOKEN' in app.config:
            self.access_token = app.config['BASESPACE_TOKEN']
            self.get_user_id()

    def get_user_id(self):
        """ Return the current user's id """
        self.app.logger.info("Attempting to deterimine userid...")
        url = '%s/users/current?access_token=%s' % (self.base_url, self.access_token)
        data = get_json(url)
        if data and 'Response' in data:
            response = data['Response']
            self.userid = response['Id']
        else:
            self.userid = None
        self.app.logger.info("userid is %s", self.userid)
        return self.userid

    def get_runs(self):
        """ Returns a list of runs """
        retval = []
        if not self.userid:
            return retval

        offset = 0
        while True:
            url = '%s/users/%s/runs?Limit=1024&Offset=%s&access_token=%s' % (self.base_url,
                                                                             self.userid,
                                                                             offset,
                                                                             self.access_token)
            data = get_json(url)
            if not data:
                break
            response = data['Response']

            runs = response['Items']
            for run in runs:
                retval.append(run)
            if response['DisplayedCount'] + offset == response['TotalCount']:
                break
            offset += response['DisplayedCount']
        return retval

'''
    def getProjectID(self, projectName):
        """ Return a project's id based on its name """
        projects = self.getProjects()
        # find the project with the request name
        for project in projects:
            if project['Name'] == projectName:
                return project['Id']
        return None

    def getProjectSamples(self, projectid):
        """ Returns a list of samples for a BaseSpace projectid
        :param projectid: BaseSpace Project ID
        :return: JSON list of sample names and IDs
        """
        retVal = []
        url = '%s/projects/%s/samples?Limit=1024&Offset=0&access_token=%s' % \
            (self.baseUrl, projectid, self.accessToken)
        data = getJSON(url)
        if not data:
            return retVal

        response = data['Response']
        samples = response['Items']
        for sample in samples:
            logger.debug(sample)
            retVal.append({'Name': sample['Name'], 'Id': sample['Id']})
        return retVal

    def getProjects(self):
        """ Returns a list of project """
        logger.debug("Retrieving projects")
        if not self.userid:
            self.getCurrentUser()
        if not self.userid:
            return None

        offset = 0
        retVal = []
        while True:
            url = '%s/users/%s/projects?Limit=1024&Offset=%s&access_token=%s' % (self.baseUrl,
                                                                                 self.userid,
                                                                                 offset,
                                                                                 self.accessToken)
            data = getJSON(url)
            if not data:
                logger.warn("Expected JSON response but got nothing.")
                return retVal
            response = data['Response']

            projects = response['Items']
            for project in projects:
                logger.debug(project)
                retVal.append({'Name': project['Name'], 'Id': project['Id']})
            if response['DisplayedCount'] + offset == response['TotalCount']:
                break
            else:
                offset += response['DisplayedCount']
        return retVal

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
