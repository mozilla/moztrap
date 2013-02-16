"""
Tests for ProductVersionResource api.

"""

from tests.case.api.crud import ApiCrudCases



class ProductVersionResourceTest(ApiCrudCases):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.ProductVersionFactory()


    @property
    def resource_name(self):
        return "productversion"


    @property
    def permission(self):
        """String defining the permission required for
        Create, Update, and Delete."""
        return "core.manage_products"


    @property
    def wrong_permissions(self):
        """String defining permissions that will NOT work for this object."""
        return "library.manage_suites"


    @property
    def new_object_data(self):
        """Generates a dictionary containing the field names and auto-generated
        values needed to create a unique object.

        The output of this method can be sent in the payload parameter of a
        POST message.
        """
        self.product_fixture = self.F.ProductFactory.create()
        fields = {
            u"product": unicode(
                self.get_detail_url('product', str(self.product_fixture.id))),
            u"version": unicode(self.datetime),
            u"codename": unicode(
                "amazing test %s %s" % (self.datetime, self.resource_name)),
        }
        return fields


    def backend_object(self, id):
        """Returns the object from the backend, so you can query it's values in
        the database for validation.
        """
        return self.model.ProductVersion.everything.get(id=id)


    def backend_data(self, backend_obj):
        """Query's the database for the object's current values. Output is a
        dictionary that should match the result of getting the object's detail
        via the API, and can be used to verify API output.

        Note: both keys and data should be in unicode
        """
        return {
            u"id": unicode(backend_obj.id),
            u"product": unicode(
                self.get_detail_url('product', str(backend_obj.product.id))),
            u"version": unicode(backend_obj.version),
            u"codename": unicode(backend_obj.codename),
            u"resource_uri": unicode(
                self.get_detail_url(self.resource_name, str(backend_obj.id))),
            }


    # additional test cases, if any
