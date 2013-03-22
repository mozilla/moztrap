"""
Tests for ElementResource api.

"""

from tests.case.api.crud import ApiCrudCases



class ElementResourceTest(ApiCrudCases):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.ElementFactory()


    @property
    def resource_name(self):
        return "element"


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
        self.category_fixture = self.F.CategoryFactory()

        return {
            u"name": u"element %s %s" % modifiers,
            u"category": unicode(
                self.get_detail_url("category", str(self.category_fixture.id))),
            }


    @property
    def read_create_fields(self):
        """category is read-only."""
        return ["category"]


    def backend_object(self, id):
        """Returns the object from the backend, so you can query it's values in
        the database for validation.
        """
        return self.model.Element.everything.get(id=id)


    def backend_data(self, backend_obj):
        """Query's the database for the object's current values. Output is a
        dictionary that should match the result of getting the object's detail
        via the API, and can be used to verify API output.

        Note: both keys and data should be in unicode
        """
        return {
            u"id": unicode(str(backend_obj.id)),
            u"name": unicode(backend_obj.name),
            u"category": unicode(
                self.get_detail_url("category", str(backend_obj.category.id))
            ),
            u"resource_uri": unicode(
                self.get_detail_url(self.resource_name, str(backend_obj.id))),
        }
