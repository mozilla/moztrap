import json

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache

from ..core import decorators as dec
from ..core.conf import conf
from ..core.filters import KeywordFilter
from ..environments.models import (
    EnvironmentTypeList, EnvironmentType, EnvironmentGroupList, EnvironmentList,
    EnvironmentGroup)
from ..products.filters import ProductFieldFilter
from ..products.models import ProductList
from ..static import filters as status_filters
from ..static.status import TestCaseStatus, TestSuiteStatus
from ..testcases.filters import TestSuiteFieldFilter
from ..testcases.models import TestSuiteList, TestCaseList, TestCaseVersionList
from ..testexecution.filters import TestCycleFieldFilter, TestRunFieldFilter
from ..testexecution.models import TestCycleList, TestRunList
from ..users.decorators import login_redirect
from ..users.filters import TeamFieldFilter
from ..users.models import UserList

from .decorators import environment_actions
from .finder import ManageFinder
from .forms import (
    ProductForm, TestCycleForm, TestRunForm, TestSuiteForm, TestCaseForm,
    BulkTestCaseForm)



def home(request):
    return redirect(reverse("manage_testcycles") + "?openfinder=1")



@login_redirect
@dec.finder(ManageFinder)
@dec.actions(ProductList, ["delete"])
@dec.filter("products",
            ("name", KeywordFilter),
            ("user", TeamFieldFilter),
            )
@dec.paginate("products")
@dec.sort("products")
@dec.ajax("manage/product/_products_list.html")
def products(request):
    return TemplateResponse(
        request,
        "manage/product/products.html",
        {
            "products": ProductList.ours(auth=request.auth),
            }
        )



@login_redirect
@dec.finder(ManageFinder)
def add_product(request):
    form = ProductForm(
        request.POST or None,
        company=request.company,
        profile_choices=EnvironmentTypeList.get(auth=request.auth).filter(
            groupType=True),
        team_choices=UserList.ours(auth=request.auth),
        auth=request.auth)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        messages.success(
            request,
            "The product '%s' has been created."  % product.name)
        return redirect("manage_products")
    return TemplateResponse(
        request,
        "manage/product/add_product.html",
        {"form": form}
        )



@never_cache
@login_redirect
@dec.finder(ManageFinder)
def edit_product(request, product_id):
    product = ProductList.get_by_id(product_id, auth=request.auth)
    form = ProductForm(
        request.POST or None,
        instance=product,
        company=request.company,
        team_choices=UserList.ours(auth=request.auth),
        auth=request.auth)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        messages.success(
            request,
            "The product '%s' has been saved."  % product.name)
        return redirect("manage_products")

    return TemplateResponse(
        request,
        "manage/product/edit_product.html",
        {
            "form": form,
            "product": product,
            }
        )



@login_redirect
@dec.finder(ManageFinder)
@dec.actions(TestCycleList, ["activate", "deactivate", "delete", "clone"])
@dec.filter("cycles",
            ("status", status_filters.TestCycleStatusFilter),
            ("product", ProductFieldFilter),
            ("name", KeywordFilter),
            ("user", TeamFieldFilter),
            )
@dec.paginate("cycles")
@dec.sort("cycles")
@dec.ajax("manage/product/testcycle/_cycles_list.html")
def testcycles(request):
    return TemplateResponse(
        request,
        "manage/product/testcycle/cycles.html",
        {
            "cycles": TestCycleList.ours(auth=request.auth),
            }
        )



@login_redirect
@dec.finder(ManageFinder)
def add_testcycle(request):
    form = TestCycleForm(
        request.POST or None,
        product_choices=ProductList.ours(auth=request.auth),
        team_choices=UserList.ours(auth=request.auth),
        auth=request.auth)
    if request.method == "POST" and form.is_valid():
        cycle = form.save()
        messages.success(
            request,
            "The test cycle '%s' has been created."  % cycle.name)
        return redirect("manage_testcycles")
    return TemplateResponse(
        request,
        "manage/product/testcycle/add_cycle.html",
        {"form": form}
        )



@never_cache
@login_redirect
@dec.finder(ManageFinder)
@dec.actions(TestRunList, ["clone", "delete", "activate", "deactivate"],
             fall_through=True)
@dec.sort("testruns")
@dec.ajax("manage/product/testcycle/_runs_list.html")
def edit_testcycle(request, cycle_id):
    cycle = TestCycleList.get_by_id(cycle_id, auth=request.auth)
    form = TestCycleForm(
        request.POST or None,
        instance=cycle,
        product_choices=[cycle.product],
        team_choices=UserList.ours(auth=request.auth),
        auth=request.auth)
    if request.method == "POST" and form.is_valid():
        cycle = form.save()
        messages.success(
            request,
            "The test cycle '%s' has been saved."  % cycle.name)
        return redirect("manage_testcycles")

    testruns = TestRunList.ours(auth=request.auth).filter(
        testCycle=cycle.id)

    return TemplateResponse(
        request,
        "manage/product/testcycle/edit_cycle.html",
        {
            "form": form,
            "cycle": cycle,
            "testruns": testruns,
            }
        )



@login_redirect
def testcycle_details(request, cycle_id):
    cycle = TestCycleList.get_by_id(cycle_id, auth=request.auth)
    return TemplateResponse(
        request,
        "manage/product/testcycle/_cycle_details.html",
        {"cycle": cycle})



@login_redirect
@dec.finder(ManageFinder)
@dec.actions(TestRunList, ["activate", "deactivate", "delete", "clone"])
@dec.filter("runs",
            ("status", status_filters.TestRunStatusFilter),
            ("product", ProductFieldFilter),
            ("testCycle", TestCycleFieldFilter),
            ("name", KeywordFilter),
            ("user", TeamFieldFilter),
            )
@dec.paginate("runs")
@dec.sort("runs")
@dec.ajax("manage/product/testrun/_runs_list.html")
def testruns(request):
    return TemplateResponse(
        request,
        "manage/product/testrun/runs.html",
        {
            "runs": TestRunList.ours(auth=request.auth),
            }
        )



@login_redirect
@dec.finder(ManageFinder)
def add_testrun(request):
    tcid = request.GET.get("cycle")
    suites = TestSuiteList.ours(auth=request.auth)
    form = TestRunForm(
        request.POST or None,
        initial=tcid and {"test_cycle": tcid} or {},
        test_cycle_choices=TestCycleList.ours(auth=request.auth),
        suites_choices=suites,
        team_choices=UserList.ours(auth=request.auth),
        auth=request.auth)
    if request.method == "POST" and form.is_valid():
        run = form.save()
        messages.success(
            request,
            "The test run '%s' has been created."  % run.name)
        return redirect("manage_testruns")
    return TemplateResponse(
        request,
        "manage/product/testrun/add_run.html",
        {"form": form}
        )



@never_cache
@login_redirect
@dec.finder(ManageFinder)
def edit_testrun(request, run_id):
    run = TestRunList.get_by_id(run_id, auth=request.auth)
    form = TestRunForm(
        request.POST or None,
        instance=run,
        test_cycle_choices=[run.testCycle],
        suites_choices=TestSuiteList.ours(auth=request.auth).filter(
            product=run.product, status=TestSuiteStatus.ACTIVE),
        team_choices=UserList.ours(auth=request.auth),
        auth=request.auth)
    if request.method == "POST" and form.is_valid():
        run = form.save()
        messages.success(
            request,
            "The test run '%s' has been saved."  % run.name)
        return redirect("manage_testruns")

    return TemplateResponse(
        request,
        "manage/product/testrun/edit_run.html",
        {
            "form": form,
            "run": run,
            }
        )



@login_redirect
def testrun_details(request, run_id):
    run = TestRunList.get_by_id(run_id, auth=request.auth)
    return TemplateResponse(
        request,
        "manage/product/testrun/_run_details.html",
        {"run": run})



@login_redirect
@dec.finder(ManageFinder)
@dec.actions(TestSuiteList, ["activate", "deactivate", "delete", "clone"])
@dec.filter("suites",
            ("status", status_filters.TestSuiteStatusFilter),
            ("product", ProductFieldFilter),
            ("run", TestRunFieldFilter),
            ("name", KeywordFilter))
@dec.paginate("suites")
@dec.sort("suites")
@dec.ajax("manage/product/testsuite/_suites_list.html")
def testsuites(request):
    return TemplateResponse(
        request,
        "manage/product/testsuite/suites.html",
        {
            "suites": TestSuiteList.ours(auth=request.auth),
            }
        )



@login_redirect
@dec.finder(ManageFinder)
def add_testsuite(request):
    form = TestSuiteForm(
        request.POST or None,
        product_choices=ProductList.ours(auth=request.auth),
        cases_choices=TestCaseVersionList.latest(auth=request.auth).filter(
            company=conf.CC_COMPANY_ID, status=TestCaseStatus.ACTIVE),
        auth=request.auth)
    if request.method == "POST" and form.is_valid():
        suite = form.save()
        messages.success(
            request,
            "The test suite '%s' has been created."  % suite.name)
        return redirect("manage_testsuites")
    return TemplateResponse(
        request,
        "manage/product/testsuite/add_suite.html",
        {"form": form}
        )



@never_cache
@login_redirect
@dec.finder(ManageFinder)
def edit_testsuite(request, suite_id):
    suite = TestSuiteList.get_by_id(suite_id, auth=request.auth)
    form = TestSuiteForm(
        request.POST or None,
        instance=suite,
        product_choices=[suite.product],
        cases_choices=TestCaseVersionList.latest(auth=request.auth).filter(
            product=suite.product.id, status=TestCaseStatus.ACTIVE),
        auth=request.auth)
    if request.method == "POST" and form.is_valid():
        suite = form.save()
        messages.success(
            request,
            "The test suite '%s' has been saved."  % suite.name)
        return redirect("manage_testsuites")

    return TemplateResponse(
        request,
        "manage/product/testsuite/edit_suite.html",
        {
            "form": form,
            "suite": suite,
            }
        )



@login_redirect
def testsuite_details(request, suite_id):
    suite = TestSuiteList.get_by_id(suite_id, auth=request.auth)
    return TemplateResponse(
        request,
        "manage/product/testsuite/_suite_details.html",
        {"suite": suite})



@login_redirect
@dec.finder(ManageFinder)
@dec.actions(
    TestCaseVersionList,
    ["approve", "reject", "activate", "deactivate"],
    fall_through=True)
@dec.actions(
    TestCaseList,
    ["clone", "delete"])
@dec.filter("cases",
            ("status", status_filters.TestCaseStatusFilter),
            ("approval", status_filters.ApprovalStatusFilter),
            ("product", ProductFieldFilter),
            ("name", KeywordFilter),
            ("suite", TestSuiteFieldFilter),
            ("step", KeywordFilter),
            ("result", KeywordFilter),
            )
@dec.paginate("cases")
@dec.sort("cases")
@dec.ajax("manage/product/testcase/_cases_list.html")
def testcases(request):
    return TemplateResponse(
        request,
        "manage/product/testcase/cases.html",
        {
            "cases": TestCaseVersionList.ours(
                url="testcases/latestversions", auth=request.auth),
            }
        )



@login_redirect
@dec.finder(ManageFinder)
def add_testcase(request):
    open_bulk = False
    single_form = bulk_form = None

    if request.method == "POST":
        if "bulk-save" in request.POST:
            bulk_form = BulkTestCaseForm(
                request.POST,
                product_choices=ProductList.ours(auth=request.auth),
                auth=request.auth)
            if bulk_form.is_valid():
                testcases = bulk_form.save()
                messages.success(
                    request,
                    "%s test cases have been created." % len(testcases))
                return redirect("manage_testcases")
            open_bulk = True
        else:
            single_form = TestCaseForm(
                request.POST,
                product_choices=ProductList.ours(auth=request.auth),
                auth=request.auth)
            if single_form.is_valid():
                testcase = single_form.save()
                messages.success(
                    request,
                    "The test case '%s' has been created."  % testcase.name)
                return redirect("manage_testcases")

    if single_form is None:
        single_form = TestCaseForm(
            product_choices=ProductList.ours(auth=request.auth),
            auth=request.auth)
    if bulk_form is None:
        bulk_form = BulkTestCaseForm(
            product_choices=ProductList.ours(auth=request.auth),
            auth=request.auth)

    return TemplateResponse(
        request,
        "manage/product/testcase/add_case.html",
        {
            "single_form": single_form,
            "bulk_form": bulk_form,
            "open_bulk": open_bulk,
            })



@never_cache
@login_redirect
@dec.finder(ManageFinder)
def edit_testcase(request, case_id):
    case = TestCaseVersionList.get_by_id(case_id, auth=request.auth)
    form = TestCaseForm(
        request.POST or None,
        instance=case,
        product_choices=[case.product],
        auth=request.auth)
    if request.method == "POST" and form.is_valid():
        case = form.save()
        messages.success(
            request,
            "The test case '%s' has been saved."  % case.name)
        return redirect("manage_testcases")

    return TemplateResponse(
        request,
        "manage/product/testcase/edit_case.html",
        {
            "single_form": form,
            "case": case,
            }
        )



@login_redirect
def testcase_details(request, case_id):
    case = TestCaseVersionList.get_by_id(case_id, auth=request.auth)
    return TemplateResponse(
        request,
        "manage/product/testcase/_case_details.html",
        {"case": case})



@login_redirect
@dec.actions(
    EnvironmentTypeList,
    ["delete"])
@dec.filter("profiles",
            ("name", KeywordFilter),
            )
@dec.paginate("profiles")
@dec.sort("profiles")
@dec.ajax("manage/environment/_profiles_list.html")
def environment_profiles(request):
    profiles = EnvironmentTypeList.get(auth=request.auth).filter(groupType=True)
    return TemplateResponse(
        request,
        "manage/environment/profiles.html",
        {"profiles": profiles})



@login_redirect
@environment_actions()
def add_environment_profile(request):
    etl = EnvironmentTypeList.get(auth=request.auth)

    element_ids = set()
    name = ""

    if request.method == "POST":
        element_ids.update(request.POST.getlist("element"))
        name = request.POST.get("profile_name")

        if not name:
            messages.error(request, "Please provide a profile name.")
        elif not element_ids:
            messages.error(
                request, "At least one environment element must be selected.")
        else:
            profile = EnvironmentType(
                name=name, company=request.company, groupType=True)
            etl.post(profile)
            request.company.autogenerate_env_groups(element_ids, profile)

            return redirect("manage_environment_edit", profile_id=profile.id)

    categories = etl.filter(groupType=False)
    return TemplateResponse(
        request,
        "manage/environment/add_profile.html",
        {
            "categories": categories,
            "selected_elements": element_ids,
            "profile_name": name,
            }
        )


@login_redirect
@dec.actions(
    EnvironmentGroupList,
    ["delete"],
    fall_through=True)
@dec.paginate('environments')
@dec.ajax("manage/environment/edit_profile/_envs_list.html")
def edit_environment_profile(request, profile_id):
    profile = EnvironmentTypeList.get_by_id(profile_id, auth=request.auth)

    if request.is_ajax() and request.method == "POST":
        if "save-profile-name" in request.POST:
            new_name = request.POST.get("profile-name")
            data = {}
            if not new_name:
                messages.error(request, "Please enter a profile name.")
                data["success"] = False
            else:
                profile.name = new_name
                profile.put()
                messages.success(request, "Profile name saved!")
                data["success"] = True

            return HttpResponse(
                json.dumps(data),
                content_type="application/json")

        elif "add-environment" in request.POST:
            element_ids = request.POST.getlist("element")
            if not element_ids:
                messages.error(
                    request, "Please select some environment elements.")
            else:
                env = EnvironmentGroup(
                    company=request.company,
                    name=str([int(i) for i in element_ids]),
                    environmentType=profile,
                    )
                EnvironmentGroupList.get(auth=request.auth).post(env)
                env.environments = element_ids

    return TemplateResponse(
        request,
        "manage/environment/edit_profile.html",
        {
            "profile": profile,
            "environments": profile.environments, # platform-speak: env groups
            }
        )



def autocomplete_env_elements(request):
    text = request.GET.get("text")
    elements = []
    if text is not None:
        elements = EnvironmentList.get(auth=request.auth).filter(
            name="%s%%" % text)

    data = {"suggestions": [{"id": e.id, "name": e.name} for e in elements]}

    return HttpResponse(json.dumps(data), content_type="application/json")
