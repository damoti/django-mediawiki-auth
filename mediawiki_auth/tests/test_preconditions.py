from mediawiki_auth.tests.utils import ChromeTestCase
from mediawiki_auth import mediawiki


class TestPreconditions(ChromeTestCase):

    def test_no_cookies_set_by_default(self):
        self.browser.get('http://wiki.test.localhost/')
        self.browser.find_element_by_link_text('Recent changes').click()
        self.assertFalse(self.browser.get_cookies())

    def test_login_token_set_by_login_page(self):
        self.browser.get('http://wiki.test.localhost/index.php?title=Special:UserLogin')
        cookie = self.browser.get_cookie('mediawiki_session')
        session = mediawiki.get_session(cookie['value'])
        self.assertEqual(set(session.keys()), {b'wsExpiresUnix', b'wsLoginToken'})

    def test_logged_in(self):
        self.login_into_wiki()

        cookie = self.browser.get_cookie('mediawiki_session')

        session = mediawiki.get_session(cookie['value'])
        self.assertEqual(session[b'wsUserName'], b'Admin')
        self.assertEqual(session[b'wsUserID'], 1)

        user = mediawiki.get_user(session[b'wsUserID'])
        self.assertEqual(user.id, 1)
        self.assertEqual(user.name, b'Admin')

        user_id = self.browser.get_cookie('mediawikiUserID')['value']
        self.assertEqual(user_id, '1')
        user_name = self.browser.get_cookie('mediawikiUserName')['value']
        self.assertEqual(user_name, 'Admin')

        self.assertTrue(user.verify_session_and_cookie_values(session, user_id, user_name))
