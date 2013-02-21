"""
Tests for ProfileResource api.

"""

from tests.case.api.crud import ApiCrudCases

import logging
mozlogger = logging.getLogger('moztrap.test')


class ProfileResourceTest(ApiCrudCases):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.ProfileFactory()


    @property
    def resource_name(self):
        """The resource name for this object."""
        return "profile"


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

        return {
            u"name": u"profile %s %s" % modifiers,
        }


    def backend_object(self, id):
        """Returns the object from the backend, so you can query it's values in
        the database for validation.
        """
        return self.model.Profile.everything.get(id=id)


    def backend_data(self, backend_obj):
        """Query's the database for the object's current values. Output is a
        dictionary that should match the result of getting the object's detail
        via the API, and can be used to verify API output.

        Note: both keys and data should be in unicode
        """
        return {
            u"id": unicode(str(backend_obj.id)),
            u"name": unicode(backend_obj.name),
            u"resource_uri": unicode(
                self.get_detail_url(self.resource_name, str(backend_obj.id))),
            }
