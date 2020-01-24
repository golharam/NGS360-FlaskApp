'''
Interface class to SevenBridges
'''
import sevenbridges as sbg
from sevenbridges.http.error_handlers import rate_limit_sleeper, \
                                             maintenance_sleeper, \
                                             general_error_sleeper

class SevenBridges:
    ''' Interface class to SevenBridges '''
    def __init__(self,
                 api_endpoint='https://api.sbgenomics.com',
                 api_endpoint_version='v2',
                 access_token=None):
        self.api_endpoint = api_endpoint
        self.api_endpoint_version = api_endpoint_version
        self.access_token = access_token
        self._connect()

    def init_app(self, app):
        ''' Mimicks the init_app for Flask apps '''
        if 'SB_AUTH_TOKEN' in app.config:
            self.access_token = app.config['SB_AUTH_TOKEN']
            self._connect()

    def _connect(self):
        if self.api_endpoint and self.api_endpoint_version and self.access_token:
            self.base_url = '%s/%s' % (self.api_endpoint, self.api_endpoint_version)
            self.api = sbg.Api(url=self.base_url,
                               token=self.access_token,
                               advance_access=True,
                               error_handlers=[rate_limit_sleeper,
                                               maintenance_sleeper,
                                               general_error_sleeper])

    def get_project_by_name(self, name):
        """ Get a project by name """
        projects = self.api.projects.query(name=name)
        for project in projects:
            if project.name == name:
                return project
        return None
