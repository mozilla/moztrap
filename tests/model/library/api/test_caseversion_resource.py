"""
Tests for CaseVersionResource api.

"""

from tests import case
from tests.case.api.crud import ApiCrudCases

import logging
mozlogger = logging.getLogger('moztrap.test')


class CaseVersionResourceTest(ApiCrudCases):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.CaseVersionFactory()


    @property
    def resource_name(self):
        return "caseversion"


    @property
    def permission(self):
        """String defining the permission required for
        Create, Update, and Delete.
        """
        return "library.manage_cases"


    @property
    def new_object_data(self):
        """Generates a dictionary containing the field names and auto-generated
        values needed to create a unique object.

        The output of this method can be sent in the payload parameter of a
        POST message.
        """
        modifiers = (self.datetime, self.resource_name)
        self.productversion_fixture = self.F.ProductVersionFactory.create()
        self.case_fixture = self.F.CaseFactory.create()
        self.case_fixture.product = self.productversion_fixture.product
        self.case_fixture.save()

        fields = {
            u"case": unicode(self.get_detail_url(
                "case", self.case_fixture.id)),
            u"name": unicode("test_%s_%s" % modifiers),
            u"description": unicode("test %s %s" % modifiers),
            u"productversion": unicode(self.get_detail_url(
                "productversion", self.productversion_fixture.id)),
            u"status": unicode("draft"),
            u"environments": [],
            u"tags": [],
#            u"attachments": [],
            u"steps": [],
        }

        return fields


    def backend_object(self, id):
        """Returns the object from the backend, so you can query it's values in
        the database for validation.
        """
        return self.model.CaseVersion.everything.get(id=id)


    def backend_data(self, backend_obj):
        """Query's the database for the object's current values. Output is a
        dictionary that should match the result of getting the object's detail
        via the API, and can be used to verify API output.

        Note: both keys and data should be in unicode
        """
        actual = {}
        actual[u"id"] = unicode(str(backend_obj.id))
        actual[u"case"] = unicode(
            self.get_detail_url("case", str(backend_obj.case.id)))
        actual[u"name"] = unicode(backend_obj.name)
        actual[u"description"] = unicode(backend_obj.description)
        actual[u"productversion"] = unicode(
            self.get_detail_url("productversion",
                backend_obj.productversion.id))
        actual[u"status"] = unicode(backend_obj.status)
        actual[u"resource_uri"] = unicode(
            self.get_detail_url(self.resource_name, str(backend_obj.id)))
        actual[u"environments"] = [unicode(
            self.get_detail_url("environment", str(env.id))
                ) for env in backend_obj.environments.all()]
        actual[u"tags"] = [unicode(self.get_detail_url("tag", str(tag.id))
                                  ) for tag in backend_obj.tags.all()]
#        actual[u"attachments"] = [unicode(self.get_detail_url("attachment",
#             str(attch.id))) for attch in backend_obj.attachments.all()]
        actual[u"steps"] = [unicode(
                    self.get_detail_url("casestep", str(step.id)))
             for step in backend_obj.steps.all()]

        return actual


    def manipulate_edit_data(self, fixture, fields):
        """case and productversion are read-only"""
        fields[u'case'] = unicode(
            self.get_detail_url('case', str(fixture.case.id)))
        fields[u'productversion'] = unicode(
            self.get_detail_url(
                'productversion', str(fixture.productversion.id)))

        return fields

    # overrides from crud.py

    # additional test cases, if any

    # validation cases

    @property
    def _product_mismatch_message(self):
        return "productversion must match case's product"


    def test_create_mismatched_product(self):
        """productversion.product must match case.product"""

        mozlogger.info("test_create_mismatched_product")

        # fixtures
        pv = self.F.ProductVersionFactory()
        fields = self.new_object_data
        fields['productversion'] = unicode(
            self.get_detail_url("productversion", pv.id))

        # do put
        res = self.post(
            self.get_list_url(self.resource_name),
            params=self.credentials,
            payload=fields,
            status=400,
        )

        self.assertEqual(res.text, self._product_mismatch_message)


    def test_change_productversion_should_error(self):
        """productversion is a create-only field."""

        mozlogger.info('test_change_productversion_should_error')

        # fixtures
        fixture1 = self.factory
        pv = self.F.ProductVersionFactory()
        pv.product = fixture1.case.product
        pv.save()
        fields = self.backend_data(fixture1)
        fields[u'steps'] = self.new_object_data[u'steps']
        fields[u'productversion'] = unicode(
            self.get_detail_url("productversion", pv.id))

        # do put
        res = self.put(
            self.get_detail_url(self.resource_name, fixture1.id),
            params=self.credentials,
            data=fields,
            status=400,
        )

        self.assertEqual(res.text,
            "productversion of an existing caseversion may not be changed.")


    def test_change_case_should_error(self):
        """case is a create-only field."""

        mozlogger.info('test_change_case_should_error')

        # fixtures
        fixture1 = self.factory
        case = self.F.CaseFactory()
        case.product = fixture1.case.product
        case.save()
        fields = self.backend_data(fixture1)
        fields[u'steps'] = self.new_object_data[u'steps']
        fields[u'case'] = unicode(
            self.get_detail_url("case", case.id))

        # do put
        res = self.put(
            self.get_detail_url(self.resource_name, fixture1.id),
            params=self.credentials,
            data=fields,
            status=400,
        )

        self.assertEqual(res.text,
            "case of an existing caseversion may not be changed.")


    def test_update_without_productversion_and_case(self):
        """productversion and case cannot be changed,
        so they are not required on edit."""

        mozlogger.info('test_update_without_productversion_and_case')

        # fixtures
        fixture1 = self.factory
        fields = self.backend_data(fixture1)
        fields[u'steps'] = self.new_object_data[u'steps']
        fields.pop('case')
        fields.pop('productversion')

        # do put
        res = self.put(
            self.get_detail_url(self.resource_name, fixture1.id),
            params=self.credentials,
            data=fields,
        )



class CaseVersionSelectionResourceTest(case.api.ApiTestCase):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.CaseVersionFactory


    @property
    def resource_name(self):
        return "caseversionselection"

    @property
    def included_param(self):
        return "tags"


    @property
    def available_param(self):
        return "{0}__ne".format(self.included_param)


    def get_exp_obj(self, cv, tags=[]):
        """Return an expected caseselection object with fields filled."""

        exp_tags = []
        for t in tags:
            exp_tag = {
                u"id": unicode(t.id),
                u"name": unicode(t.name),
                u"description": unicode(t.description),
                u"resource_uri": unicode(self.get_detail_url("tag", t.id)),
                u"product": None,
                }
            if t.product:
                exp_tag[u"product"] = unicode(
                    self.get_detail_url("product", str(t.product.id)))
            exp_tags.append(exp_tag)

        return {
            u"case": unicode(
                self.get_detail_url("case", cv.case.id)),
            u"case_id": unicode(cv.case.id),
            u"created_by": None,
            u"id": unicode(cv.id),
            u"latest": True,
            u"name": unicode(cv.name),
            u"product": {
                u"id": unicode(cv.productversion.product_id)
            },
            u"product_id": unicode(cv.productversion.product_id),
            u"productversion": {
                u"codename": u"",
                u"id": unicode(cv.productversion.id),
                u"product": unicode(self.get_detail_url(
                    "product",
                    cv.productversion.product_id)),
                u"resource_uri": unicode(self.get_detail_url(
                    "productversion",
                    cv.productversion.id)),
                u"version": u"1.0"},
            u"productversion_name": unicode(cv.productversion.name),
            u"resource_uri": unicode(
                self.get_detail_url("caseversionselection", cv.id)),
            u"tags": exp_tags,
            }


    def get_exp_meta(self, count=0):
        """Return an expected meta object with count field filled"""
        return {
            "limit": 20,
            "next": None,
            "offset": 0,
            "previous": None,
            "total_count": count,
            }


    def _do_test(self, for_id, filter_param, exp_objects):
        params = {filter_param: for_id}

        res = self.get_list(params=params)
        self.assertEqual(res.status_int, 200)

        act = res.json

        self.maxDiff = None
        self.assertEquals(act["meta"], self.get_exp_meta(len(exp_objects)))
        self.assertEqual(exp_objects, act["objects"])


    def test_available_for_none_included(self):
        """Get a list of available cases, none included"""

        cv1 = self.factory.create(name="Case1")
        cv2 = self.factory.create(name="Case2")

        self._do_test(
            -1,
            self.available_param,
            [self.get_exp_obj(cv) for cv in [cv1, cv2]],
            )


    def _setup_two_included(self):
        cv1 = self.factory.create(name="Case1", description="ab")
        cv2 = self.factory.create(name="Case2", description="cd")
        tag = self.F.TagFactory.create()
        cv1.tags.add(tag)
        cv2.tags.add(tag)

        return {
            "cv1": cv1,
            "cv2": cv2,
            "t": tag,
            }


    def test_available_for_two_included(self):
        """Get a list of available cases, both included"""

        data = self._setup_two_included()
        self._do_test(
            data["t"].id,
            self.available_param,
            [],
            )


    def test_included_for_two_included(self):
        """Get a list of available cases, both included"""

        data = self._setup_two_included()

        exp_objects = [self.get_exp_obj(cv, tags=[data["t"]]) for cv in [
            data["cv1"], data["cv2"]]]

        self._do_test(
            data["t"].id,
            self.included_param,
            exp_objects=exp_objects,
            )


    def _setup_for_one_included_one_not(self):
        cv1 = self.factory.create(name="Case1", description="ab")
        cv2 = self.factory.create(name="Case2", description="cd")
        tag = self.F.TagFactory.create()
        cv1.tags.add(tag)

        return {
            "cv1": cv1,
            "cv2": cv2,
            "t": tag,
            }


    def test_available_for_one_included_one_not(self):
        """Get a list of available cases, one included"""

        data = self._setup_for_one_included_one_not()
        exp_objects = [self.get_exp_obj(data["cv2"])]

        self._do_test(
            data["t"].id,
            self.available_param,
            exp_objects=exp_objects,
            )


    def test_included_for_one_included_one_not(self):
        """Get a list of included cases, one included"""

        data = self._setup_for_one_included_one_not()
        exp_objects = [self.get_exp_obj(data["cv1"], tags=[data["t"]])]

        self._do_test(
            data["t"].id,
            self.included_param,
            exp_objects=exp_objects,
            )
