"""
Tests for TagResource api.

"""

from tests.case.api.crud import ApiCrudCases



class TagResourceTest(ApiCrudCases):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.TagFactory()


    @property
    def resource_name(self):
        return "tag"


    @property
    def permission(self):
        """String defining the permission required for Create, Update, and Delete."""
        return "tags.manage_tags"


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
            # u"product": unicode(self.get_detail_url('product', str(self.product_fixture.id))),
        }
        return fields


    def backend_object(self, id):
        """Returns the object from the backend, so you can query it's values in
        the database for validation.
        """
        return self.model.Tag.everything.get(id=id)

 
    def backend_data(self, backend_obj):
        """Query's the database for the object's current values. Output is a 
        dictionary that should match the result of getting the object's detail 
        via the API, and can be used to verify API output.

        Note: both keys and data should be in unicode
        """
        actual = {}
        actual[u"id"] = unicode(str(backend_obj.id))
        actual[u"name"] = unicode(backend_obj.name)
        actual[u"description"] = unicode(backend_obj.description)
        actual[u"resource_uri"] = unicode(self.get_detail_url(self.resource_name, str(backend_obj.id)))
        # actual[u"product"] = unicode(self.get_detail_url("product", str(backend_obj.product.id)))

        return actual


    # additional test cases, if any

    def test_create_tag_no_product(self):
        """Creates an object using the API.
        Tags can also be created without product.
        Verifies that the fields sent in the message have been set in the database.
        """
        if self.is_abstract_class:
            return

        # get data for creation
        fields = self.new_object_data
        # fields.pop("product")

        # do the create
        res = self.post(
            self.get_list_url(self.resource_name),
            params=self.credentials,
            payload=fields,
            )

        # make sure response included detail uri
        object_id = res.headers["location"].split('/')[-2] # pull id out of uri
        self.assertIsNotNone(object_id)

        # get data from backend
        backend_obj = self.backend_object(object_id)
        created_object_data = self.clean_backend_data(backend_obj)

        # compare backend data to desired data
        self.maxDiff = None
        # fields["product"] = None
        self.assertEqual(created_object_data, fields)

    def test_create_with_product_and_caseversions(self):
        assert NotImplementedError

    def test_create_with_caseversions_no_product_error(self):
        assert NotImplementedError

    def test_create_with_caseversions_mismatch_product_error(self):
        assert NotImplementedError
