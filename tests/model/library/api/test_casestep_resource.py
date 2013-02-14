"""
Tests for CaseStepResource api.

"""

from tests.case.api.crud import ApiCrudCases

import logging
mozlogger = logging.getLogger('moztrap.test')


class CaseStepResourceTest(ApiCrudCases):

    @property
    def factory(self):
        """The model factory for this object."""
        return self.F.CaseStepFactory()


    @property
    def resource_name(self):
        return "casestep"


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
        self.caseversion_fixture = self.F.CaseVersionFactory.create()

        fields = {
            u"caseversion": unicode(
                self.get_detail_url("caseversion", str(self.caseversion_fixture.id))),
            u"number": 1,
            u"instruction": u"instruction 1 %s" % self.datetime,
            u"expected": u"expected 1 %s" % self.datetime,
        }

        return fields


    def backend_object(self, id):
        """Returns the object from the backend, so you can query it's values in
        the database for validation.
        """
        return self.model.CaseStep.everything.get(id=id)


    def backend_data(self, backend_obj):
        """Query's the database for the object's current values. Output is a
        dictionary that should match the result of getting the object's detail
        via the API, and can be used to verify API output.

        Note: both keys and data should be in unicode
        """
        actual = {
            u"id": unicode(str(backend_obj.id)),
            u"caseversion": unicode(
                self.get_detail_url("caseversion",
                    str(backend_obj.caseversion.id))),
            u"instruction": unicode(backend_obj.instruction),
            u"expected": unicode(backend_obj.expected),
            u"number": backend_obj.number,
            u"resource_uri": unicode(
                self.get_detail_url(self.resource_name, str(backend_obj.id)))
        }
        return actual


    def manipulate_edit_data(self, fixture, fields):
        """caseversion is read-only"""
        fields[u'caseversion'] = unicode(
            self.get_detail_url('caseversion', str(fixture.caseversion.id)))

        return fields

    # overrides from crud.py

    # additional test cases, if any

    # validation cases

    def test_change_caseversion_should_error(self):
        """caseversion is a create-only field."""

        mozlogger.info('test_change_caseversion_should_error')

        # fixtures
        fixture1 = self.factory
        cv = self.F.CaseVersionFactory()
        fields = self.backend_data(fixture1)
        fields[u'caseversion'] = unicode(
            self.get_detail_url("caseversion", cv.id))

        # do put
        res = self.put(
            self.get_detail_url(self.resource_name, fixture1.id),
            params=self.credentials,
            data=fields,
            status=400,
        )

        self.assertEqual(res.text,
            "caseversion of an existing casestep may not be changed.")


    def test_update_without_caseversion(self):
        """caseversion cannot be changed,
        so it is not required on edit."""

        mozlogger.info('test_update_without_caseversion')

        # fixtures
        fixture1 = self.factory
        fields = self.backend_data(fixture1)
        fields.pop('caseversion')

        # do put
        res = self.put(
            self.get_detail_url(self.resource_name, fixture1.id),
            params=self.credentials,
            data=fields,
        )
