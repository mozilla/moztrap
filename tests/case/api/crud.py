from datetime import datetime

from django.utils import unittest

from tests.case.api import ApiTestCase

class ApiCrudCases(ApiTestCase):
    """Re-usable test cases for Create, Read, Update, and Delete"""

    @property
    def is_abstract_class(self):
        """use this in tests to make sure you're not running them on an abstract class"""
        if self.__class__.__name__ == "ApiCrudCases":
            return True
        return False


    @property
    def resource_name(self):
        """string defining the resource name"""
        raise NotImplementedError

    @property
    def permission(self):
        """string defining the permission required for Create, Update, and Delete"""
        raise NotImplementedError

    @property
    def object_data(self):
        """dictionary containing the data to create an object"""
        raise NotImplementedError

    def expected_data(self, object_id):
        """dictionary containing the data expected from get detail for an object"""
        raise NotImplementedError

    def backend_get(self, **kwargs):
        """get the object from the backend"""
        raise NotImplementedError

    @property
    def datetime(self):
        """may be used to provide mostly-unique strings"""
        return datetime.utcnow().isoformat()

    def setUp(self):
        """Set-up for all CRUD test cases."""
        if self.is_abstract_class:
            return
        self.user = self.F.UserFactory.create(permissions=[self.permission])
        self.apikey = self.F.ApiKeyFactory.create(owner=self.user)
        self.credentials = {"username": self.user.username, "api_key": self.apikey.key}

    # test cases 

    def test_create(self):
        if self.is_abstract_class:
            return
        fields = self.object_data

        res = self.post(
            self.get_list_url(self.resource_name),
            params=self.credentials,
            payload=fields,
            )
        object_id = res.headers['location'].split('/')[-2]
        fields['id'] = object_id

        self.assertIsNotNone(object_id)

        created_object = self.backend_get(id=object_id)

        self.assertEqual(created_object.__dict__, fields)


    def test_create_fails_with_wrong_perms(self):
        if self.is_abstract_class:
            return
        pass

    def test_create_does_not_disturb_others(self):
        if self.is_abstract_class:
            return
        pass

    def test_read_list(self):
        if self.is_abstract_class:
            return
        res = self.get_list()

        self.assertEqual(res.status_int, 200)

        act = res.json

        act_meta = act["meta"]
        exp_meta = {
            "limit" : 20,
            "next" : None,
            "offset" : 0,
            "previous" : None,
            "total_count" : 1,
            }

        self.assertEquals(act_meta, exp_meta)

        act_objects = act["objects"]
        exp_objects = [self.expected_data(object_id)]


        self.maxDiff = None
        self.assertEqual(exp_objects, act_objects)

    def test_read_detail(self):
        if self.is_abstract_class:
            return
        pass

    def test_update_detail(self):
        if self.is_abstract_class:
            return
        pass

    def test_update_does_not_disturb_others(self):
        if self.is_abstract_class:
            return
        pass

    def test_update_list_forbidden(self):
        if self.is_abstract_class:
            return
        pass

    def test_update_fails_without_creds(self):
        if self.is_abstract_class:
            return
        pass

    def test_delete_detail(self):
        if self.is_abstract_class:
            return
        pass

    def test_delete_list_forbidden(self):
        if self.is_abstract_class:
            return
        pass

    def test_delete_fails_with_wrong_perms(self):
        if self.is_abstract_class:
            return
        pass