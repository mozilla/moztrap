"""
Tests for SuiteCaseResource api.

"""
from tests import case
from tests.case.api.crud import ApiCrudCases

import logging
mozlogger = logging.getLogger('moztrap.test')


class SuiteCaseResourceTest(ApiCrudCases):
    """Please see the test cases implemented in tests.case.api.ApiCrudCases.

    The following abstract methods must be implemented:
      - factory(self)                           (property)
      - resource_name(self)                     (property)
      - permission(self)                        (property)
      - new_object_data(self)                   (property)
      - backend_object(self, id)                (method)
      - backend_data(self, backend_object)      (method)
      - backend_meta_data(self, backend_object) (method)

    """

    # implementations for abstract methods and properties

    @property
    def factory(self):
        """The factory to use to create fixtures of the object under test.
        """
        return self.F.SuiteCaseFactory()


    @property
    def resource_name(self):
        """String defining the resource name.
        """
        return "suitecase"


    @property
    def permission(self):
        """String defining the permission required for
        Create, Update, and Delete.
        """
        return "library.manage_suite_cases"


    def order_generator(self):
        """give an incrementing number for order."""
        self.__dict__.setdefault("order", 0)
        self.order = self.order + 1
        return self.order


    @property
    def new_object_data(self):
        """Generates a dictionary containing the field names and auto-generated
        values needed to create a unique object.

        The output of this method can be sent in the payload parameter of a
        POST message.
        """
        self.product_fixture = self.F.ProductFactory.create()
        self.case_fixture = self.F.CaseFactory.create(
            product=self.product_fixture)
        self.suite_fixture = self.F.SuiteFactory.create(
            product=self.product_fixture)

        fields = {
            u"case": unicode(
                self.get_detail_url("case", str(self.case_fixture.id))),
            u"suite": unicode(
                self.get_detail_url("suite", str(self.suite_fixture.id))
            ),
            u"order": self.order_generator(),
        }
        return fields


    def backend_object(self, id):
        """Returns the object from the backend, so you can query it's values in
        the database for validation.
        """
        return self.model.SuiteCase.everything.get(id=id)


    def backend_data(self, backend_obj):
        """Query's the database for the object's current values. Output is a
        dictionary that should match the result of getting the object's detail
        via the API, and can be used to verify API output.

        Note: both keys and data should be in unicode
        """
        return {
            u"id": unicode(str(backend_obj.id)),
            u"resource_uri": unicode(
                self.get_detail_url(self.resource_name, str(backend_obj.id))),
            u"case": unicode(
                self.get_detail_url("case", str(backend_obj.case.id))),
            u"suite": unicode(
                self.get_detail_url("suite", str(backend_obj.suite.id))),
            u"order": backend_obj.order,
        }


    @property
    def read_create_fields(self):
        """List of fields that are required for create but read-only for update."""
        return ["suite", "case"]

    # overrides from crud.py

    # additional test cases, if any

    # validation cases

    def test_create_mismatched_product_error(self):
        """error if suite.product does not match case.product"""

        mozlogger.info("test_create_mismatched_product_error")

        fields = self.new_object_data
        product = self.F.ProductFactory()
        self.case_fixture.product = product
        self.case_fixture.save()

        # do post
        res = self.post(
            self.get_list_url(self.resource_name),
            params=self.credentials,
            payload=fields,
            status=400,
        )

        error_message = str(
            "case's product must match suite's product."
        )
        self.assertEqual(res.text, error_message)
