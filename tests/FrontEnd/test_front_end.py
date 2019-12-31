'''
Front-End tests
https://scotch.io/tutorials/test-a-flask-app-with-selenium-webdriver-part-1
'''
import unittest
import urllib
from flask_testing import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

from config import TestConfig
from app import create_app, DB as db
from app.models import User


class FrontEndTests(LiveServerTestCase):
    def create_app(self):
        app = create_app(TestConfig)
        return app

    def setUp(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(options=options)

        db.create_all()
        user = User(username='testuser', email='testuser@noemail.com')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()

        self.login()

    def tearDown(self):
        self.driver.quit()
        db.session.remove()
        db.drop_all()

    def login(self):
        ''' Auto login test user prior to running tests '''
        loginpage = "%s/login" % self.get_server_url()
        self.driver.get(loginpage)
        elem = self.driver.find_element_by_name("username")
        elem.clear()
        elem.send_keys("testuser")
        elem = self.driver.find_element_by_name("password")
        elem.clear()
        elem.send_keys('password')
        elem.send_keys(Keys.RETURN)
        self.driver.implicitly_wait(1) # seconds

    def check_page(self, page_url):
        ''' Generic to load a page and make sure there are no errors in the console log '''
        self.driver.get(page_url)
        log = self.driver.get_log("browser")
        for log_entry in log:
            if 'level' in log_entry and log_entry['level'] == "SEVERE":
                if 'message' in log_entry:
                    self.fail(log_entry['message'])
                self.fail("Unknown log entry: %s" % log_entry)

    def test_basespace_page(self):
        ''' Make sure there are no Javascript errors when the home page loads '''
        url = "%s/basespace" % self.get_server_url()
        self.check_page(url)

    def test_basespace_archiverun_action(self):
        ''' Make sure we can archive a run '''
        self.skipTest("not yet implemented")

    def test_illuminaruns_page(self):
        ''' Make sure there are no Javascript errors when the home page loads '''
        url = "%s/illumina_runs" % self.get_server_url()
        self.check_page(url)

    def test_index_page(self):
        ''' Make sure there are no Javascript errors when the home page loads '''
        self.check_page(self.get_server_url())

    def test_jobs_page(self):
        ''' Make sure there are no Javascript errors when the home page loads '''
        url = "%s/projects" % self.get_server_url()
        self.check_page(url)

if __name__ == '__main__':
    unittest.main()
