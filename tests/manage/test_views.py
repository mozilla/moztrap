from mock import patch

from ..products.builders import products
from ..testcases.builders import (
    testsuites, testsuiteincludedtestcases, testcases, testcaseversions,
    testcasesteps)
from ..testexecution.builders import testcycles, testruns
from ..responses import response
from ..users.builders import users
from ..utils import ViewTestCase, Url, COMMON_RESPONSES



@patch("ccui.core.api.userAgent")
class DefaultManageViewTest(ViewTestCase):
    @property
    def view(self):
        from ccui.manage.views import home
        return home


    def test_redirect(self, http):
        self.setup_responses(http)
        res = self.app.get("/manage/")

        self.assertEqual(res.status_int, 302)
        self.assertEqual(
            res.headers["location"],
            "http://localhost:80/manage/testcycles/?openfinder=1")



class EditViewTests(object):
    builder = None
    edit_form_id = None


    @property
    def url(self):
        return "/manage/%s/1/" % self.builder.name


    @property
    def api_url(self):
        return "%s/1" % self.builder.plural_name


    def responses(self):
        responses = {
            "http://fake.base/rest/%s?_type=json" % self.api_url:
                response(self.builder.one(_id=1, _url=self.api_url)),
            # finder
            "http://fake.base/rest/products?sortfield=name&sortdirection=asc&_type=json&companyId=1":
                response(products.searchresult({})),
            }
        responses.update(self.extra_responses())
        return responses


    def edit_responses(self):
        responses = self.responses()
        responses.update(self.extra_edit_responses())
        return responses


    def extra_responses(self):
        return {}


    def extra_edit_responses(self):
        return {}


    def edit_data(self):
        return {
            "name": "New name",
            "description": "Newdesc"
            }


    def test_no_cache(self, http):
        self.setup_responses(http, self.responses())
        res = self.app.get(self.url)

        self.assertEqual(res.headers["cache-control"], "max-age=0")



    def test_all_api_endpoints_hit(self, http):
        self.setup_responses(http, self.responses())
        self.app.get(self.url)

        self.assertEqual(
            set([Url(k) for k in self.responses().iterkeys()]),
            set(Url(args[1]["uri"])
                for args in http.request.call_args_list).difference(
                # not concerned about common responses
                set([Url(k) for k in COMMON_RESPONSES.iterkeys()])))


    def test_edit(self, http):
        res = self._submit_edit_form(http)

        self.assertEqual(
            res.status_int, 302, res.html.findAll("ul", "errorlist"))


    def test_all_edit_api_endpoints_hit(self, http):
        self._submit_edit_form(http)

        self.assertEqual(
            set([Url(k) for k in self.edit_responses().iterkeys()]),
            set(Url(args[1]["uri"])
                for args in http.request.call_args_list).difference(
                # not concerned about common responses
                set([Url(k) for k in COMMON_RESPONSES.iterkeys()])))


    def _submit_edit_form(self, http):
        self.setup_responses(http, self.edit_responses())
        res = self.app.get(self.url)
        form = res.forms[self.edit_form_id]
        response_data = {"id": 1, "url": self.api_url}
        for k, v in self.edit_data().items():
            form[k] = v
            response_data[k] = v
        http.request.return_value = response(self.builder.one(**response_data))
        return form.submit()



@patch("ccui.core.api.userAgent")
class ProductEditViewTest(ViewTestCase, EditViewTests):
    builder = products
    edit_form_id = "product-edit-form"


    def extra_responses(self):
        return {
            "http://fake.base/rest/users?_type=json&companyId=1":
                response(users.searchresult({})),
            "http://fake.base/rest/%s/team/members?_type=json" % self.api_url:
                response(users.array({})),
            }


@patch("ccui.core.api.userAgent")
class TestCycleEditViewTest(ViewTestCase, EditViewTests):
    builder = testcycles
    edit_form_id = "cycle-form"


    def extra_responses(self):
        return {
            "http://fake.base/rest/testruns?_type=json&testCycleId=1&companyId=1":
                response(testruns.searchresult({})),
            "http://fake.base/rest/users?_type=json&companyId=1":
                response(users.searchresult({})),
            "http://fake.base/rest/%s/team/members?_type=json" % self.api_url:
                response(users.array({})),
            }



@patch("ccui.core.api.userAgent")
class TestRunEditViewTest(ViewTestCase, EditViewTests):
    builder = testruns

    edit_form_id = "run-form"


    def extra_responses(self):
        return {
            "http://fake.base/rest/testsuites/?_type=json&testSuiteStatusId=2&productId=1":
                response(testsuites.searchresult({})),
            "http://fake.base/rest/testcycles/1?_type=json":
                response(testcycles.one()),
            "http://fake.base/rest/testruns/1/testsuites?_type=json":
                response(testsuites.array({})),
            "http://fake.base/rest/users?_type=json&companyId=1":
                response(users.searchresult({})),
            "http://fake.base/rest/%s/team/members?_type=json" % self.api_url:
                response(users.array({})),
            }



@patch("ccui.core.api.userAgent")
class TestSuiteEditViewTest(ViewTestCase, EditViewTests):
    builder = testsuites

    edit_form_id = "suite-form"


    def extra_responses(self):
        return {
            "http://fake.base/rest/testsuites/1/includedtestcases?sortfield=runOrder&sortdirection=asc&_type=json":
                response(testsuiteincludedtestcases.array({})),
            "http://fake.base/rest/testcases/latestversions/?_type=json&testCaseStatusId=2&productId=1":
                response(testcaseversions.searchresult({})),
            }


    def extra_edit_responses(self):
        return {
            "http://fake.base/rest/testsuites/1/includedtestcases?_type=json":
                response(testsuiteincludedtestcases.array({}))
            }



@patch("ccui.core.api.userAgent")
class TestCaseEditViewTest(ViewTestCase, EditViewTests):
    builder = testcaseversions

    edit_form_id = "single-case-form"

    url = "/manage/testcase/1/"

    api_url = "testcases/versions/1"


    def extra_responses(self):
        return {
            "http://fake.base/rest/testcases/versions/1/steps?_type=json":
                response(testcasesteps.array({})),
            "http://fake.base/rest/testcases/1/versions?_type=json":
                response(testcaseversions.array({}))
            }


    def extra_edit_responses(self):
        return {
            "http://fake.base/rest/testcasesteps/1?_type=json":
                response(testcasesteps.one()),
            # separate call to update the name
            "http://fake.base/rest/testcases/1?_type=json":
                response(testcases.one(_id=1, _url="testcases/1")),
            }


    def edit_data(self):
        return {
            "name": "New name",
            "description": "Some description",
            }


    def test_edit_name(self, http):
        self._submit_edit_form(http)

        # find the dedicated PUT call for setting the name
        put = [
            ca[1] for ca in http.request.call_args_list
            if ca[1]["method"] == "PUT" and
            ca[1]["uri"] == "http://fake.base/rest/testcases/1?_type=json"
            ][0]

        self.assertEqual(put["body"], "name=New+name&companyId=1&maxAttachmentSizeInMbytes=0&originalVersionId=0&maxNumberOfAttachments=0&productId=1")

        self.assertEqual(put["headers"]["cookie"], "USERTOKEN: authcookie")
