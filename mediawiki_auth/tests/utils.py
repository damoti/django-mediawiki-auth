import os; os.environ['DJANGO_SETTINGS_MODULE'] = 'mediawiki_auth.tests.settings'
import django; django.setup()
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class ChromeTestCase(StaticLiveServerTestCase):

    port = 8081

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = Options()
        options.add_argument("--headless")
        cls.browser = webdriver.Chrome(chrome_options=options)

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.browser.delete_all_cookies()

    def login_into_wiki(self):
        self.browser.get('http://wiki.test.localhost/index.php?title=Special:UserLogin')
        self.browser.find_element_by_name('wpName').send_keys('admin')
        self.browser.find_element_by_name('wpPassword').send_keys('a-very-long-password')
        self.browser.find_element_by_name('wpLoginAttempt').click()

    def logout_of_wiki(self):
        self.browser.get('http://wiki.test.localhost/index.php?title=Special:UserLogout')
