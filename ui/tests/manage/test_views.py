from mock import patch

from ..environments.builders import (
    environmentgroups, environmenttypes, environments)
from ..products.builders import products
from ..testcases.builders import (
    testsuites, testsuiteincludedtestcases, testcaseversions, testcasesteps)
from ..testexecution.builders import testcycles, testruns
from ..responses import response, make_identity
from ..users.builders import users
from ..utils import ViewTestCase, Url, COMMON_RESPONSES



@patch("tcmui.core.api.userAgent")
class DefaultManageViewTest(ViewTestCase):
    @property
    def view(self):
        from tcmui.manage.views import home
        return home


    def test_redirect(self, http):
        self.setup_responses(http)
        res = self.app.get("/manage/")

        self.assertEqual(res.status_int, 302)
        self.assertEqual(
            res.headers["location"],
            "http://localhost:80/manage/testcycles/")



class EditViewTests(object):
    builder = None


    @property
    def url(self):
        return "/manage/%s/1/" % self.builder.name


    @property
    def api_url(self):
        return "%s/1" % self.builder.plural_name


    def responses(self):
        responses = {
            "http://fake.base/rest/%s?_type=json" % self.api_url:
                response(self.builder.one(
                    resourceIdentity=make_identity(
                        id=1, url=self.api_url))),
            "http://fake.base/rest/environmentgroups/1/environments?_type=json":
                response(environments.array({})),
            "http://fake.base/rest/environmenttypes/1?_type=json":
                response(environmenttypes.one()),
            "http://fake.base/rest/%s/environmentgroups?_type=json" % self.api_url:
                response(environmentgroups.array({})),
            }
        responses.update(self.extra_responses())
        return responses


    def extra_responses(self):
        return {}


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



@patch("tcmui.core.api.userAgent")
class TestCycleEditViewTest(ViewTestCase, EditViewTests):
    builder = testcycles


    def extra_responses(self):
        return {
            "http://fake.base/rest/products/1?_type=json":
                response(products.one()),
            "http://fake.base/rest/products/1/environmentgroups?_type=json":
                response(environmentgroups.array({})),
            "http://fake.base/rest/testruns?_type=json&testCycleId=1&companyId=1":
                response(testruns.searchresult({})),
            "http://fake.base/rest/users?_type=json&companyId=1":
                response(users.searchresult({})),
            "http://fake.base/rest/%s/team/members?_type=json" % self.api_url:
                response(users.array({})),
            }



@patch("tcmui.core.api.userAgent")
class TestRunEditViewTest(ViewTestCase, EditViewTests):
    builder = testruns


    def extra_responses(self):
        return {
            "http://fake.base/rest/testsuites/?_type=json&productId=1":
                response(testsuites.searchresult({})),
            "http://fake.base/rest/testcycles/1/environmentgroups?_type=json":
                response(environmentgroups.array({})),
            "http://fake.base/rest/testcycles/1?_type=json":
                response(testcycles.one()),
            "http://fake.base/rest/testruns/1/testsuites?_type=json":
                response(testsuites.array({})),
            "http://fake.base/rest/users?_type=json&companyId=1":
                response(users.searchresult({})),
            "http://fake.base/rest/%s/team/members?_type=json" % self.api_url:
                response(users.array({})),
            }



@patch("tcmui.core.api.userAgent")
class TestSuiteEditViewTest(ViewTestCase, EditViewTests):
    builder = testsuites


    def extra_responses(self):
        return {
            "http://fake.base/rest/testsuites/1/includedtestcases?sortfield=runOrder&sortdirection=asc&_type=json":
                response(testsuiteincludedtestcases.array({})),
            "http://fake.base/rest/testcases/latestversions/?_type=json&testCaseStatusId=2&productId=1":
                response(testcaseversions.searchresult({})),
            "http://fake.base/rest/products/1?_type=json":
                response(products.one()),
            "http://fake.base/rest/products/1/environmentgroups?_type=json":
                response(environmentgroups.array({})),
            }



@patch("tcmui.core.api.userAgent")
class TestCaseEditViewTest(ViewTestCase, EditViewTests):
    builder = testcaseversions

    url = "/manage/testcase/1/"

    api_url = "testcases/versions/1"


    def extra_responses(self):
        return {
            "http://fake.base/rest/products/1?_type=json":
                response(products.one()),
            "http://fake.base/rest/products/1/environmentgroups?_type=json":
                response(environmentgroups.array({})),
            "http://fake.base/rest/testcases/versions/1/steps?_type=json":
                response(testcasesteps.array({})),
            }
