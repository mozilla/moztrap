"""
Manage views for suites.

"""
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache

from django.contrib import messages

from moztrap import model
from moztrap.model.mtmodel import NotDeletedCount
from moztrap.view.filters import SuiteFilterSet
from moztrap.view.lists import decorators as lists
from moztrap.view.lists.filters import PinnedFilters
from moztrap.view.users.decorators import permission_required
from moztrap.view.utils.ajax import ajax
from moztrap.view.utils.auth import login_maybe_required

from ..finders import ManageFinder

from . import forms



@never_cache
@login_maybe_required
@lists.actions(
    model.Suite,
    ["delete", "clone", "activate", "draft", "deactivate"],
    permission="library.manage_suites")
@lists.finder(ManageFinder)
@lists.filter("suites", filterset_class=SuiteFilterSet)
@lists.sort("suites")
@ajax("manage/suite/list/_suites_list.html")
def suites_list(request):
    """List suites."""
    return TemplateResponse(
        request,
        "manage/suite/suites.html",
        {
            "suites": model.Suite.objects.select_related().annotate(
                case_count=NotDeletedCount("cases", distinct=True)),
            }
        )



@never_cache
@login_maybe_required
def suite_details(request, suite_id):
    """Get details snippet for a suite."""
    suite = get_object_or_404(
        model.Suite, pk=suite_id)
    return TemplateResponse(
        request,
        "manage/suite/list/_suite_details.html",
        {
            "suite": suite
            }
        )



@never_cache
@permission_required("library.manage_suites")
def suite_add(request):
    """Add a suite."""
    if request.method == "POST":
        form = forms.AddSuiteForm(request.POST, user=request.user)
        suite = form.save_if_valid()
        if suite is not None:
            messages.success(
                request, u"Suite '{0}' added.".format(
                    suite.name)
                )
            return redirect("manage_suites")
    else:
        pf = PinnedFilters(request.COOKIES)
        # Note: inital takes a dict, NOT a QueryDict.  It won't work correctly
        # with a QueryDict.
        form = forms.AddSuiteForm(
            user=request.user,
            initial=pf.fill_form_querystring(request.GET).dict(),
            )
    return TemplateResponse(
        request,
        "manage/suite/add_suite.html",
        {
            "form": form
            }
        )



@never_cache
@permission_required("library.manage_suites")
def suite_edit(request, suite_id):
    """Edit a suite."""
    suite = get_object_or_404(model.Suite, pk=suite_id)
    if request.method == "POST":
        form = forms.EditSuiteForm(
            request.POST, instance=suite, user=request.user)
        saved_suite = form.save_if_valid()
        if saved_suite is not None:
            messages.success(request, u"Saved '{0}'.".format(saved_suite.name))
            pre_page = request.GET.get('from', "manage_suites")
            return redirect(pre_page)
    else:
        form = forms.EditSuiteForm(
            instance=suite, user=request.user)
    return TemplateResponse(
        request,
        "manage/suite/edit_suite.html",
        {
            "form": form,
            "suite": suite,
            }
        )
