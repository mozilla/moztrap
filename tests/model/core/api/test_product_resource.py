"""
Tests for ProductResource api.

"""

from tests.case.api.crud import ApiCrudCases



class ProductResourceTest(ApiCrudCases):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.ProductFactory()


    @property
    def resource_name(self):
        return "product"


    @property
    def permission(self):
        """String defining the permission required for Create, Update, and Delete."""
        return "core.manage_products"


    @property
    def wrong_permissions(self):
        """String defining permissions that will NOT work for this object."""
        return "library.manage_suites"


    @property
    def new_object_data(self):
        """Generates a dictionary containing the field names and auto-generated
        values needed to create a unique object.

        The output of this method can be sent in the payload parameter of a POST message.
        """
        self.product_fixture = self.F.ProductFactory.create()
        fields = {
            u"name": unicode("test_%s_%s" % (self.datetime, self.resource_name)),
            u"description": unicode("test %s %s" % (self.datetime, self.resource_name)),
            u"productversions": {
                u"version": unicode(self.datetime),
                u"codename": unicode("test version %s" % self.datetime),
                u"description": unicode("test version %s" % self.datetime)
            }
        }
        return fields


    def backend_object(self, id):
        """Returns the object from the backend, so you can query it's values in
        the database for validation.
        """
        return self.model.Product.everything.get(id=id)

 
    def backend_data(self, backend_obj):
        """Query's the database for the object's current values. Output is a 
        dictionary that should match the result of getting the object's detail 
        via the API, and can be used to verify API output.

        Note: both keys and data should be in unicode
        """
        product_uri = self.get_detail_url(self.resource_name, str(backend_obj.id))
        actual = {}
        actual[u"id"] = unicode(str(backend_obj.id))
        actual[u"name"] = unicode(backend_obj.name)
        actual[u"description"] = unicode(backend_obj.description)
        actual[u"resource_uri"] = unicode(product_uri)
        actual[u"productversions"] = []
        # actual[u"productversions"] = [{
        #         u"id": unicode(pv.id),
        #         u"product": unicode(product_uri),
        #         u"version": unicode(pv.version),
        #         u"codename": unicode(pv.codename),
        #         u"resource_uri": unicode(self.get_detail_url('productversion', str(pv.id))),
        #     } for pv in backend_obj.versions.all()]

        return actual



    # additional test cases, if any
