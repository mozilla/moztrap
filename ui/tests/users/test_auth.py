from mock import patch

from ..core.test_auth import CredentialsTest
from ..responses import response, make_array, make_list
from ..utils import ResourceTestCase
from .builders import users



class UserCredentialsTest(CredentialsTest, ResourceTestCase):
    def get_resource_class(self):
        from tcmui.users.models import User
        return User


    def get_resource_list_class(self):
        from tcmui.users.models import UserList
        return UserList


    def get_creds(self, *args, **kwargs):
        from tcmui.users.auth import UserCredentials
        return UserCredentials(*args, **kwargs)


    def test_user(self):
        with patch("tcmui.core.api.userAgent", spec=["request"]) as http:
            auth = self.get_creds("test@example.com", password="testpw")

            self.assertEqual(http.request.call_count, 0)

            http.request.return_value = response(
                users.one(email="test@example.com"))

            user = auth.user

            self.assertEqual(http.request.call_count, 1)
            self.assertEqual(user.email, "test@example.com")
            self.assertIs(user.auth, auth)

            # subsequent accesses don't require HTTP access
            user = auth.user

            self.assertEqual(http.request.call_count, 1)


    def test_permission_codes(self):
        with patch("tcmui.core.api.userAgent", spec=["request"]) as http:
            auth = self.get_creds("test@example.com", password="testpw")

            http.request.return_value = response(
                users.one(email="test@example.com"))

            self.assertEqual(auth.user.email, "test@example.com")
            self.assertEqual(http.request.call_count, 1)

            http.request.return_value = response(
                make_array(
                    "permission", "Permission",
                    *make_list(
                        "permission",
                        "permissions",
                        {
                            "assignable": True,
                            "name": "",
                            "permissionCode": "PERMISSION_COMPANY_INFO_VIEW"}
                        )))

            perms = auth.permission_codes

            self.assertEqual(http.request.call_count, 2)
            self.assertEqual(len(perms), 1)
            self.assertEqual(perms[0], "PERMISSION_COMPANY_INFO_VIEW")

            # subsequent accesses don't require HTTP access
            perms = auth.permission_codes

            self.assertEqual(http.request.call_count, 2)
