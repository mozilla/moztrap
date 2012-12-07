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
    def wrong_permissions(self):
        """string defining permissions that will NOT work for this object"""
        if self.__class__.__name__ == "ProductResource":
            raise NotImplementedError
        else:
            return 'core.manage_products'

    @property
    def new_object_data(self):
        """dictionary containing the data to create an object"""
        raise NotImplementedError

    def backend_object(self, id):
        """get the object from the backend"""
        raise NotImplementedError

    def backend_data(self, backend_object):
        """dictionary containing the data expected from get detail for an object,
        using data pulled from the db. both keys and data should be in unicode"""
        raise NotImplementedError

    def backend_meta_data(self, backend_obj):
        """retrieves object meta data from backend"""
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
        # get data for creation
        fields = self.new_object_data

        # do the create
        res = self.post(
            self.get_list_url(self.resource_name),
            params=self.credentials,
            payload=fields,
            )

        # make sure response included detail uri
        object_id = res.headers['location'].split('/')[-2]
        self.assertIsNotNone(object_id)

        # update fields with autu-generated data
        fields[u'id'] = unicode(object_id)
        fields[u'resource_uri'] = self.get_detail_url(self.resource_name, object_id)

        # get data from backend
        backend_obj = self.backend_object(object_id)
        created_object_data = self.backend_data(backend_obj)

        # compare backend data to desired data
        self.maxDiff = None
        self.assertEqual(created_object_data, fields)

        # make sure meta data is correct
        created_obj_meta_data = self.backend_meta_data(backend_obj)
        self.assertEqual(created_obj_meta_data['created_by'], self.user.username)
        self.assertIsNotNone(created_obj_meta_data['created_on'])
        self.assertIsNone(created_obj_meta_data['deleted_by'])
        self.assertIsNone(created_obj_meta_data['deleted_on'])


    def test_create_fails_with_wrong_perms(self):
        if self.is_abstract_class:
            return
        pass

    def test_create_does_not_disturb_others(self):
        if self.is_abstract_class:
            return
        pass

    def test_read_list(self):
        '''credentials should not be required to get list'''
        if self.is_abstract_class:
            return

        # create fixture
        suite_fixture1 = self.F.SuiteFactory()
        suite_fixture2 = self.F.SuiteFactory()

        # fetch list
        res = self.get_list() # no creds

        # make sure response is correct
        self.assertEqual(res.status_int, 200)

        act = res.json

        act_meta = act["meta"]
        exp_meta = {
            u"limit" : 20,
            u"next" : None,
            u"offset" : 0,
            u"previous" : None,
            u"total_count" : 2,
            }

        self.assertEquals(act_meta, exp_meta)

        act_objects = act["objects"]
        exp_objects = [
            self.backend_data(suite_fixture1), 
            self.backend_data(suite_fixture2)
            ]


        self.maxDiff = None
        self.assertEqual(exp_objects, act_objects)

    def test_read_detail(self):
        '''credentials should not be required to get detail'''
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