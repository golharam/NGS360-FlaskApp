'''
Front-End tests
https://scotch.io/tutorials/test-a-flask-app-with-selenium-webdriver-part-1
'''
import urllib
from flask_testing import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import TestConfig
from app import create_app

class FrontEndTests(LiveServerTestCase):
    def create_app(self):
        # pass in test configurations
        app = create_app(TestConfig)
        return app

    def setUp(self):
        """Setup the test driver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def tearDown(self):
        self.driver.quit()

    def test_homepage_loads_correctly(self):
        ''' Make sure there are no Javascript errors when the home page loads '''
        response = urllib.request.urlopen(self.get_server_url())
        self.assertEqual(response.code, 200)
        log = self.driver.get_log("browser")
        for log_entry in log:
            if 'level' in log_entry and log_entry['level'] == "SEVERE":
                if 'message' in log_entry:
                    self.fail(log_entry['message'])
                self.fail("Unknown log entry: %s" % log_entry)
