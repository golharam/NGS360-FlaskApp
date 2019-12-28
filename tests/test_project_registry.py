'''
Test endpoints in app.project_registry
'''
from urllib.error import HTTPError
from unittest import TestCase
from unittest.mock import patch
from config import TestConfig
from app import create_app, project_registry

class ProjectRegistryTests(TestCase):
    '''
    Test interface class to ProjectRegistry
    '''
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        self.client = None
        self.app_context.pop()

    def test_get_projects(self):
        ''' Test retrieving a full list of projects '''
        with patch('app.project_registry.urlopen') as mock_open:
            mock_open.return_value = open("test_data/test_project_registry/test_get_projects.json")
            result = project_registry.get_projects("someurl")
        self.assertEqual(len(result), 2)

    def test_get_projects_specific_fields(self):
        ''' Test retrieving a fields of a project '''
        with patch('app.project_registry.urlopen') as mock_open:
            mock_open.return_value = open("test_data/test_project_registry/test_get_projects.json")
            projects = project_registry.get_projects("someurl",
                                                     fields=['projectid', 'projectname'])
        self.assertEqual(len(projects), 2,)

    def test_get_projects_with_error(self):
        ''' Test failed to retrieve projects '''
        with patch('app.project_registry.urlopen') as mock_open:
            mock_open.side_effect = HTTPError("someurl", 404, "URL not available", {}, None)
            result = project_registry.get_projects("someurl")
            self.assertEqual(result, [])
