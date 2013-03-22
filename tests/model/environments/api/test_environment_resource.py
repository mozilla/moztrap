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

        self.profile_fixture = self.F.ProfileFactory()
        self.category_fixture1 = self.F.CategoryFactory(name="A")
        self.category_fixture2 = self.F.CategoryFactory(name="B")
        self.category_fixture3 = self.F.CategoryFactory(name="C")
        self.element_fixture1 = self.F.ElementFactory(category=self.category_fixture1, name="A 2")
        self.element_fixture2 = self.F.ElementFactory(category=self.category_fixture2, name="B 2")
        self.element_fixture3 = self.F.ElementFactory(category=self.category_fixture3, name="C 2")
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


    def test_elements_must_be_from_different_categories(self):
        """A post with two elements from the same category should error."""
        logger.info("test_elements_must_be_from_different_categories")

        # get data for creation & munge it
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


    def test_basic_combinatorics_patch(self):
        """A Patch request with profile and categories should do combinatorics
        on the categories and create environments."""
        logger.info("test_basic_combinatorics_patch")

        fields = self.new_object_data

        # create more elements for each category
        for x in range(2):
            self.F.ElementFactory(category=self.category_fixture1, name="A %s" % x)
            self.F.ElementFactory(category=self.category_fixture2, name="B %s" % x)
            self.F.ElementFactory(category=self.category_fixture3, name="C %s" % x)

        # modify fields to send categories rather than elements
        fields.pop('elements')
        fields['categories'] = [
            unicode(self.get_detail_url(
                "category", str(self.category_fixture1.id))),
            unicode(self.get_detail_url(
                "category", str(self.category_fixture2.id))),
            unicode(self.get_detail_url(
                "category", str(self.category_fixture3.id))),
        ]

        # do the create
        res = self.patch(
            self.get_list_url(self.resource_name),
            params=self.credentials,
            payload=fields,
            )

        # check that it made the right number of environments
        self._test_filter_list_by(u'profile', self.profile_fixture.id, 27)


    def test_patch_without_categories_error(self):
        """'categories' must be provided in PATCH."""
        logger.info("test_patch_without_categories_error")

        fields = self.new_object_data

        # do the create
        res = self.patch(
            self.get_list_url(self.resource_name),
            params=self.credentials,
            payload=fields,
            status=400,
            )

        error_msg = "PATCH request must contain categories list."
        self.assertEqual(res.text, error_msg)


    def test_patch_categories_not_list_error(self):
        """'categories' must be a list in PATCH."""
        logger.info("test_patch_categories_not_list_error")

        fields = self.new_object_data
        fields.pop("elements")
        fields[u'categories'] = unicode(
            self.get_detail_url("category", str(self.category_fixture1.id)))

        # do the create
        res = self.patch(
            self.get_list_url(self.resource_name),
            params=self.credentials,
            payload=fields,
            status=400,
            )

        error_msg = "PATCH request must contain categories list."
        self.assertEqual(res.text, error_msg)


    def test_patch_categories_list_not_string_or_hash_error(self):
        """'categories' must be a list in PATCH."""
        logger.info("test_patch_categories_list_not_string_or_hash_error")

        fields = self.new_object_data
        fields.pop("elements")
        fields[u'categories'] = [1, 2, 3]

        # do the create
        res = self.patch(
            self.get_list_url(self.resource_name),
            params=self.credentials,
            payload=fields,
            status=400,
            )

        error_msg = "categories list must contain resource uris or hashes."
        self.assertEqual(res.text, error_msg)


    def test_patch_with_exclude(self):
        """Combinatorics excluding some elements."""
        logger.info("test_patch_with_exclude")

        fields = self.new_object_data

        # create more elements for each category
        for x in range(2):
            self.F.ElementFactory(category=self.category_fixture1, name="A %s" % x)
            self.F.ElementFactory(category=self.category_fixture2, name="B %s" % x)
            self.F.ElementFactory(category=self.category_fixture3, name="C %s" % x)

        # modify fields to send categories rather than elements
        fields.pop('elements')
        fields['categories'] = [
            {
                u'category': unicode(self.get_detail_url(
                    "category", str(self.category_fixture1.id))),
                u'exclude': [unicode(self.get_detail_url(
                    "element", str(self.element_fixture1.id))), ],
            },
            {
                u'category': unicode(self.get_detail_url(
                    "category", str(self.category_fixture2.id))),
                u'exclude': [unicode(self.get_detail_url(
                    "element", str(self.element_fixture2.id))), ],
            },
            {
                u'category': unicode(self.get_detail_url(
                    "category", str(self.category_fixture3.id))),
                u'exclude': [unicode(self.get_detail_url(
                    "element", str(self.element_fixture3.id))), ],
            }, ]

        # do the create
        res = self.patch(
            self.get_list_url(self.resource_name),
            params=self.credentials,
            payload=fields,
            )

        # check that it made the right number of environments
        self._test_filter_list_by(u'profile', self.profile_fixture.id, 8)


    def test_patch_with_include(self):
        """Combinatorics including some elements."""
        logger.info("test_patch_with_include")

        fields = self.new_object_data

        # create more elements for each category
        for x in range(2):
            self.F.ElementFactory(category=self.category_fixture1, name="A %s" % x)
            self.F.ElementFactory(category=self.category_fixture2, name="B %s" % x)
            self.F.ElementFactory(category=self.category_fixture3, name="C %s" % x)

        # modify fields to send categories rather than elements
        fields.pop('elements')
        fields['categories'] = [
            {
                u'category': unicode(self.get_detail_url(
                    "category", str(self.category_fixture1.id))),
                u'include': [unicode(self.get_detail_url(
                    "element", str(self.element_fixture1.id))), ],
                },
            {
                u'category': unicode(self.get_detail_url(
                    "category", str(self.category_fixture2.id))),
                u'include': [unicode(self.get_detail_url(
                    "element", str(self.element_fixture2.id))), ],
                },
            {
                u'category': unicode(self.get_detail_url(
                    "category", str(self.category_fixture3.id))),
                u'include': [unicode(self.get_detail_url(
                    "element", str(self.element_fixture3.id))), ],
                }, ]

        # do the create
        res = self.patch(
            self.get_list_url(self.resource_name),
            params=self.credentials,
            payload=fields,
            )

        # check that it made the right number of environments
        self._test_filter_list_by(u'profile', self.profile_fixture.id, 1)


    def test_patch_no_include_no_exclude(self):
        """Sending hashes without include or exclude should do the same as
        sending regular uri strings."""
        logger.info("test_patch_no_include_no_exclude")

        fields = self.new_object_data

        # create more elements for each category
        for x in range(2):
            self.F.ElementFactory(category=self.category_fixture1, name="A %s" % x)
            self.F.ElementFactory(category=self.category_fixture2, name="B %s" % x)
            self.F.ElementFactory(category=self.category_fixture3, name="C %s" % x)

        # modify fields to send categories rather than elements
        fields.pop('elements')
        fields['categories'] = [
            {
                u'category': unicode(self.get_detail_url(
                    "category", str(self.category_fixture1.id))),
                },
            {
                u'category': unicode(self.get_detail_url(
                    "category", str(self.category_fixture2.id))),
                },
            {
                u'category': unicode(self.get_detail_url(
                    "category", str(self.category_fixture3.id))),
                }, ]

        # do the create
        res = self.patch(
            self.get_list_url(self.resource_name),
            params=self.credentials,
            payload=fields,
            )

        # check that it made the right number of environments
        self._test_filter_list_by(u'profile', self.profile_fixture.id, 27)
