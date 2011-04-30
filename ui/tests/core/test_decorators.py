from unittest2 import TestCase



class AsAdminTest(TestCase):
    @property
    def cls(self):
        from tcmui.core.decorators import as_admin

        class TestObject(object):
            def __init__(self):
                self.auth = ["original auth"]
                self.call_args_list = []
                self.auth_list = []

            @as_admin
            def a_method(self, *args, **kwargs):
                self.call_args_list.append((args, kwargs))
                self.auth_list.append(self.auth)

        return TestObject


    def test_uses_admin_auth(self):
        from tcmui.core.auth import admin

        obj = self.cls()
        obj.a_method()

        self.assertIs(obj.auth_list[-1], admin)


    def test_restores_previous_auth(self):
        obj = self.cls()

        prev = obj.auth

        obj.a_method()

        self.assertIs(obj.auth, prev)


    def test_passes_on_all_args(self):
        obj = self.cls()

        obj.a_method(1, 2, a=1, b=2)

        self.assertEqual(obj.call_args_list[-1], ((1, 2), {"a": 1, "b": 2}))
