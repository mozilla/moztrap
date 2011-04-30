from unittest2 import TestCase



class CredentialsTest(TestCase):
    def get_creds(self, *args, **kwargs):
        from tcmui.core.auth import Credentials
        return Credentials(*args, **kwargs)


    def test_with_password(self):
        c = self.get_creds("user@example.com", password="blah")

        self.assertEqual(
            c.headers(),
            {
                "authorization": "Basic dXNlckBleGFtcGxlLmNvbTpibGFo"
                }
            )


    def test_with_cookie(self):
        c = self.get_creds("user@example.com", cookie="USERTOKEN: value")

        self.assertEqual(
            c.headers(),
            {
                "cookie": "USERTOKEN: value"
                }
            )


    def test_with_both(self):
        c = self.get_creds(
            "user@example.com", password="blah", cookie="USERTOKEN: value")

        self.assertEqual(
            c.headers(),
            {
                "authorization": "Basic dXNlckBleGFtcGxlLmNvbTpibGFo"
                }
            )


    def test_with_neither(self):
        c = self.get_creds("user@example.com")

        self.assertEqual(c.headers(), {})


    def test_repr(self):
        c = self.get_creds("user@example.com")

        self.assertEqual(repr(c), "<Credentials: user@example.com>")


    def test_eq(self):
        c = self.get_creds("user@example.com", password="yo")
        d = self.get_creds("user@example.com", password="yo")
        self.assertEqual(c, d)


    def test_not_eq(self):
        c = self.get_creds("user@example.com", password="yo")
        d = self.get_creds("user@example.com", cookie="yo")
        self.assertNotEqual(c, d)


    def test_not_eq_same_cred(self):
        c = self.get_creds("user@example.com", password="yo")
        d = self.get_creds("user@example.com", password="hmm")
        self.assertNotEqual(c, d)



