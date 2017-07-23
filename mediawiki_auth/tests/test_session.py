from mediawiki_auth.tests.utils import ChromeTestCase
from mediawiki_auth.models import DjangoUser


class TestSessionSharing(ChromeTestCase):

    def setUp(self):
        super().setUp()
        DjangoUser.objects.all().delete()

    def test_not_logged_in(self):
        self.browser.get('http://django.test.localhost/')
        self.assertEqual(self.browser.find_element_by_id('status').text, 'not logged-in')

    def test_login(self):
        self.login_into_wiki()
        self.assertEqual(DjangoUser.objects.count(), 0)
        self.browser.get('http://django.test.localhost/')
        self.assertEqual(DjangoUser.objects.count(), 1)
        self.assertEqual(self.browser.find_element_by_id('status').text, 'logged-in as Admin')

    def test_login_logout(self):
        self.login_into_wiki()
        self.browser.get('http://django.test.localhost/')
        self.assertEqual(self.browser.find_element_by_id('status').text, 'logged-in as Admin')
        self.logout_of_wiki()
        self.browser.get('http://django.test.localhost/')
        self.assertEqual(self.browser.find_element_by_id('status').text, 'not logged-in')
