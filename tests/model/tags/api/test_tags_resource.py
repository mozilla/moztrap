"""
Tests for TagResource api.

"""

from tests.case.api.crud import ApiCrudCases

import logging
mozlogger = logging.getLogger('moztrap.test')


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
        """String defining the permission required for
        Create, Update, and Delete."""
        return "tags.manage_tags"


    @property
    def new_object_data(self):
        """Generates a dictionary containing the field names and auto-generated
        values needed to create a unique object.

        The output of this method can be sent in the payload parameter of a
        POST message.
        """
        self.product_fixture = self.F.ProductFactory.create()
        fields = {
            u"name": unicode(
                "test_%s_%s" % (self.datetime, self.resource_name)),
            u"description": unicode(
                "test %s %s" % (self.datetime, self.resource_name)),
            u"product": None,
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
        actual[u"resource_uri"] = unicode(
            self.get_detail_url(self.resource_name, str(backend_obj.id)))
        if backend_obj.product:
            actual[u"product"] = unicode(
                self.get_detail_url("product", str(backend_obj.product.id)))
        else:
            actual[u"product"] = None

        return actual


    # additional test cases, if any

    # create cases
    # test_create handles creating a global tag

    def test_create_tag_with_product(self):
        """Create a product-specific tag."""
        mozlogger.info('test_create_tag_with_product')

        # get data for creation
        fields = self.new_object_data
        fields['product'] = unicode(
            self.get_detail_url("product", str(self.product_fixture.id)))

        # do the create
        res = self.post(
            self.get_list_url(self.resource_name),
            params=self.credentials,
            payload=fields,
            )

        # make sure response included detail uri
        object_id = self._id_from_uri(res.headers["location"])
        self.assertIsNotNone(object_id)

        # get data from backend
        backend_obj = self.backend_object(object_id)
        created_object_data = self.clean_backend_data(backend_obj)

        # compare backend data to desired data
        self.maxDiff = None
        self.assertEqual(created_object_data, fields)

    # edit cases

    @property
    def _invalid_product_msg(self):
        return str("Tag's Product may not be changed unless the tag is not " +
               "in use, the product is being set to None, or the product " +
               "matches the existing cases.")


    def test_edit_no_product(self):
        """Test that edit works even without the product."""
        mozlogger.info('test_edit_no_product')

        # create fixture
        fixture1 = self.factory
        backend_obj = self.backend_object(fixture1.id)
        obj_id = str(fixture1.id)
        fields = self.new_object_data
        product = fields.pop(u'product')

        # do put
        res = self.put(
            self.get_detail_url(self.resource_name, obj_id),
            params=self.credentials,
            data=fields
            )

        # make sure object has been updated in the database
        fields[u'product'] = product
        fixture1 = self.refresh(fixture1)
        backend_data = self.clean_backend_data(fixture1)

        self.maxDiff = None
        self.assertEqual(fields, backend_data)


    def test_edit_global_tag_in_use_change_description(self):
        """Editing the description on a global tag should not un-set it's cases."""
        mozlogger.info('test_edit_global_tag_in_use_change_description')

        # create fixtures
        tag1 = self.factory

        tc1 = self.F.CaseVersionFactory()
        tc1.tags = [tag1]
        tc2 = self.F.CaseVersionFactory()
        tc2.tags = [tag1]
        tc3 = self.F.CaseVersionFactory()

        tag1 = self.refresh(tag1)
        self.assertEqual(len(tag1.caseversions.all()), 2)

        # generate new values
        fields = self.backend_data(tag1)
        fields[u'description'] = 'an updated description'

        # do put
        res = self.put(
            self.get_detail_url(self.resource_name, str(tag1.id)),
            params=self.credentials,
            data=fields,
            )

        # make sure object has been updated in the database
        tag1 = self.refresh(tag1)

        self.maxDiff = None
        backend_data = self.backend_data(tag1)
        self.assertEqual(fields, backend_data)

        # make sure test cases still have their tags
        self.assertEqual(len(tag1.caseversions.all()), 2)
        self.assertTrue(tc1 in tag1.caseversions.all())
        self.assertTrue(tc2 in tag1.caseversions.all())


    def test_edit_global_tag_in_use_change_product_error(self):
        """If a global tag is in-use by cases of multiple products, it's product field should be read-only."""
        mozlogger.info('test_edit_global_tag_in_use_change_product_error')

        # create fixtures
        tag1 = self.factory

        tc1 = self.F.CaseVersionFactory()
        tc1.tags = [tag1]
        tc2 = self.F.CaseVersionFactory()
        tc2.tags = [tag1]
        tc3 = self.F.CaseVersionFactory()

        tag1 = self.refresh(tag1)
        self.assertEqual(len(tag1.caseversions.all()), 2)

        # generate new values
        fields = self.backend_data(tag1)
        product1 = self.F.ProductFactory()
        fields[u'product'] = unicode(
            self.get_detail_url("product", str(product1.id)))

        # do put
        res = self.put(
            self.get_detail_url(self.resource_name, str(tag1.id)),
            params=self.credentials,
            data=fields,
            status=400,
            )

        self.assertEqual(res.text, self._invalid_product_msg)


    def test_edit_global_tag_in_use_change_product_matches_caseversion(self):
        """If a global tag is in use by cases all having the same product, the product field may be changed to match."""
        mozlogger.info(
            'test_edit_global_tag_in_use_change_product_matches_caseversion')

        # create fixtures
        tag1 = self.factory

        tc1 = self.F.CaseVersionFactory()
        tc1.tags = [tag1]
        tc2 = self.F.CaseVersionFactory()
        tc2.productversion = tc1.productversion  # make it be same product
        tc2.save()
        tc2.tags = [tag1]

        tag1 = self.refresh(tag1)
        self.assertEqual(len(tag1.caseversions.all()), 2)

        # generate new values
        fields = self.backend_data(tag1)
        fields[u'product'] = unicode(
            self.get_detail_url("product", str(tc1.productversion.product.id)))

        # do put
        res = self.put(
            self.get_detail_url(self.resource_name, str(tag1.id)),
            params=self.credentials,
            data=fields,
            )

        # make sure object has been updated in the database
        tag1 = self.refresh(tag1)

        self.maxDiff = None
        backend_data = self.backend_data(tag1)
        self.assertEqual(fields, backend_data)

        # make sure test cases still have their tags
        self.assertEqual(len(tag1.caseversions.all()), 2)
        self.assertTrue(tc1 in tag1.caseversions.all())
        self.assertTrue(tc2 in tag1.caseversions.all())


    def test_edit_global_tag_not_in_use_change_product(self):
        """If a global tag is not in-use by any caseversions, the product field should be editable."""
        mozlogger.info('test_edit_global_tag_not_in_use_change_product')

        # create fixtures
        tag1 = self.factory
        self.assertEqual(len(tag1.caseversions.all()), 0)

        # generate new values
        fields = self.backend_data(tag1)
        product1 = self.F.ProductFactory()
        fields[u'product'] = unicode(
            self.get_detail_url("product", str(product1.id)))

        # do put
        res = self.put(
            self.get_detail_url(self.resource_name, str(tag1.id)),
            params=self.credentials,
            data=fields,
            )

        # make sure object has been updated in the database
        tag1 = self.refresh(tag1)

        self.maxDiff = None
        backend_data = self.backend_data(tag1)
        self.assertEqual(fields, backend_data)


    def test_edit_product_tag_in_use_change_product_error(self):
        """If a product-specific tag is in use, trying to change it's product should error."""
        mozlogger.info('test_edit_product_tag_in_use_change_product_error')

        # create fixtures
        tag1 = self.factory
        tc1 = self.F.CaseVersionFactory()
        tag1.product = tc1.productversion.product  # make tag product-specific
        tc1.tags = [tag1]  # use the tag

        self.assertEqual(len(tag1.caseversions.all()), 1)

        # generate new values
        fields = self.backend_data(tag1)
        product1 = self.F.ProductFactory()
        fields[u'product'] = unicode(
            self.get_detail_url("product", str(product1.id)))

        # do put
        res = self.put(
            self.get_detail_url(self.resource_name, str(tag1.id)),
            params=self.credentials,
            data=fields,
            status=400,
            )

        self.assertEqual(res.text, self._invalid_product_msg)


    def test_edit_product_tag_in_use_remove_product(self):
        """If a product-specific tag is in use and you reset the product to None. caseversions should stay tagged."""
        mozlogger.info("test_edit_product_tag_in_use_remove_product")

        # create fixtures
        tag1 = self.factory
        tc1 = self.F.CaseVersionFactory()
        tag1.product = tc1.productversion.product  # make tag product-specific
        tag1.save()
        tc1.tags = [tag1]  # use the tag

        self.assertEqual(len(tag1.caseversions.all()), 1)

        # generate new values
        fields = self.backend_data(tag1)
        fields[u'product'] = None

        # do put
        res = self.put(
            self.get_detail_url(self.resource_name, str(tag1.id)),
            params=self.credentials,
            data=fields,
            )

        # make sure object has been updated in the database
        tag1 = self.refresh(tag1)

        self.maxDiff = None
        backend_data = self.backend_data(tag1)
        self.assertEqual(fields, backend_data)

        # make sure caseversions are still tagged
        self.assertEqual(len(tag1.caseversions.all()), 1)

    # filtering

    def test_filter_by_name(self):
        """Filter tags by name."""
        mozlogger.info("test_filter_by_name")

        # create fixtures
        tag1 = self.factory
        tag2 = self.factory
        tag2.name = u'unique name'
        tag2.save()

        # do test
        self._test_filter_list_by(u'name', u'unique name', 1)


    def test_filter_by_product(self):
        """Filter tags by product."""
        mozlogger.info("test_filter_by_product")

        # create fixtures
        product1 = self.F.ProductFactory()
        tag1 = self.factory
        tag1.product = product1
        tag1.save()
        tag2 = self.factory
        tag2.product = product1
        tag2.save()
        tag3 = self.factory

        # do test
        self._test_filter_list_by(u'product', str(product1.id), 2)
        self._test_filter_list_by(u'product', None, 1)
