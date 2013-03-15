"""
Tests for EnvironmentResource api.

"""

from tests.case.api.crud import ApiCrudCases

import logging
logger = logging.getLogger("moztrap.test")


class EnvironmentResourceTest(ApiCrudCases):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.EnvironmentFactory()


    @property
    def resource_name(self):
        return "environment"


    @property
    def permission(self):
        """The permissions needed to modify this object type."""
        return "environments.manage_environments"


    @property
    def new_object_data(self):
        """Generates a dictionary containing the field names and auto-generated
        values needed to create a unique object.

        The output of this method can be sent in the payload parameter of a
        POST message.
        """
        modifiers = (self.datetime, self.resource_name)
        self.profile_fixture = self.F.ProfileFactory()
        self.category_fixture1 = self.F.CategoryFactory()
        self.category_fixture2 = self.F.CategoryFactory()
        self.category_fixture3 = self.F.CategoryFactory()
        self.element_fixture1 = self.F.ElementFactory()
        self.element_fixture1.category = self.category_fixture1
        self.element_fixture1.save()
        self.element_fixture2 = self.F.ElementFactory()
        self.element_fixture2.category = self.category_fixture2
        self.element_fixture2.save()
        self.element_fixture3 = self.F.ElementFactory()
        self.element_fixture3.category = self.category_fixture3
        self.element_fixture3.save()
        self.element_fixture_list = [
            self.element_fixture1, self.element_fixture2, self.element_fixture3]

        return {
            u"profile": unicode(
                self.get_detail_url("profile", str(self.profile_fixture.id))),
            u"elements": [unicode(
                self.get_detail_url(
                    "element", str(elem.id))
                ) for elem in self.element_fixture_list],
            }


    def backend_object(self, id):
        """Returns the object from the backend, so you can query it's values in
        the database for validation.
        """
        return self.model.Environment.everything.get(id=id)


    def backend_data(self, backend_obj):
        """Query's the database for the object's current values. Output is a
        dictionary that should match the result of getting the object's detail
        via the API, and can be used to verify API output.

        Note: both keys and data should be in unicode
        """
        return {
            u"id": unicode(str(backend_obj.id)),
            u"profile": unicode(self.get_detail_url("profile", str(backend_obj.profile.id))),
            u"elements": [unicode(
                self.get_detail_url("element", str(elem.id))
            ) for elem in backend_obj.elements.all()],
            u"resource_uri": unicode(
                self.get_detail_url(self.resource_name, str(backend_obj.id))),
        }


    def test_update_detail(self):
        """PUT is not supported for environments."""
        pass


    def test_update_fails_without_creds(self):
        """PUT is not supported for environments."""
        pass


    def test_elements_must_be_from_different_categories(self):
        """A post with two elements from the same category should error."""
        logger.info("test_elements_must_be_from_different_categories")

        # get data for creation
        fields = self.new_object_data
        self.element_fixture2.category = self.element_fixture1.category
        self.element_fixture2.save()

        # do the create
        res = self.post(
            self.get_list_url(self.resource_name),
            params=self.credentials,
            payload=fields,
            status=400,
            )

        error_msg = "Elements must each belong to a different Category."
        self.assertEqual(res.text, error_msg)
