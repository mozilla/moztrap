from mock import patch

from ..core.test_auth import CredentialsTest
from ..responses import response
from .test_models import UserTestCase


class UserCredentialsTest(CredentialsTest, UserTestCase):
    def get_creds(self, *args, **kwargs):
        from tcmui.users.auth import UserCredentials
        return UserCredentials(*args, **kwargs)


    def test_user(self):
        with patch("tcmui.core.api.userAgent", spec=["request"]) as http:
            auth = self.get_creds("test@example.com", password="testpw")

            self.assertEqual(http.request.call_count, 0)

            http.request.return_value = response(
                self.make_one(email="test@example.com"))

            user = auth.user

            self.assertEqual(http.request.call_count, 1)
            self.assertEqual(user.email, "test@example.com")
            self.assertIs(user.auth, auth)

            # subsequent accesses don't require HTTP access
            user = auth.user

            self.assertEqual(http.request.call_count, 1)
