"""
Manage views for cases.

"""
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from django.contrib import messages

from moztrap import model

from moztrap.view.filters import CaseVersionFilterSet
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
    model.CaseVersion,
    ["delete"],
    permission="library.manage_cases",
    fall_through=True)
@lists.actions(
    model.CaseVersion,
    ["clone", "activate", "draft", "deactivate"],
    permission="library.manage_cases")
@lists.finder(ManageFinder)
@lists.filter("caseversions", filterset_class=CaseVersionFilterSet)
@lists.sort("caseversions")
@ajax("manage/case/list/_cases_list.html")
def cases_list(request):
    """List caseversions."""
    return TemplateResponse(
        request,
        "manage/case/cases.html",
        {
            "caseversions": model.CaseVersion.objects.select_related(
                "case",
                "productversion",
                "productversion__product",
                ).prefetch_related(
                    "tags",
                    ),
            }
        )



@never_cache
@login_maybe_required
def case_details(request, caseversion_id):
    """Get details snippet for a caseversion."""
    caseversion = get_object_or_404(model.CaseVersion, pk=caseversion_id)
    return TemplateResponse(
        request,
        "manage/case/list/_case_details.html",
        {
            "caseversion": caseversion
            }
        )



@login_maybe_required
def case_id_redirect(request, case_id):
    """Given case ID redirect to latest version in manage list."""
    cv = get_object_or_404(
        model.CaseVersion.objects.all(), case=case_id, latest=True)
    return HttpResponseRedirect(
        "{0}?filter-id={1}#caseversion-id-{2}".format(
            reverse("manage_cases"), cv.case.id, cv.id))



@never_cache
@permission_required("library.create_cases")
def case_add(request):
    """Add a single case."""
    if request.method == "POST":
        form = forms.AddCaseForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            case = form.save()
            messages.success(
                request, u"Test case '{0}' added.".format(
                    case.versions.all()[0].name)
                )
            return redirect("manage_cases")
    else:
        pf = PinnedFilters(request.COOKIES)
        form = forms.AddCaseForm(
            user=request.user,
            initial=pf.fill_form_querystring(request.GET).dict(),
            )
    return TemplateResponse(
        request,
        "manage/case/add_case.html",
        {
            "form": form
            }
        )



@never_cache
@permission_required("library.create_cases")
def case_add_bulk(request):
    """Add cases in bulk."""
    if request.method == "POST":
        form = forms.AddBulkCaseForm(
            request.POST, request.FILES, user=request.user)
        if form.is_valid():
            cases = form.save()
            messages.success(
                request, u"Added {0} test case{1}.".format(
                    len(cases), "" if len(cases) == 1 else "s")
                )
            return redirect("manage_cases")
    else:
        pf = PinnedFilters(request.COOKIES)
        form = forms.AddBulkCaseForm(user=request.user, initial=pf.fill_form_querystring(request.GET))
    return TemplateResponse(
        request,
        "manage/case/add_case_bulk.html",
        {
            "form": form
            }
        )



@never_cache
@permission_required("library.manage_cases")
def caseversion_edit(request, caseversion_id):
    """Edit a caseversion."""
    caseversion = get_object_or_404(model.CaseVersion, pk=caseversion_id)
    if request.method == "POST":
        form = forms.EditCaseVersionForm(
            request.POST,
            request.FILES,
            instance=caseversion,
            user=request.user)
        cv = form.save_if_valid()
        if cv is not None:
            messages.success(request, u"Saved '{0}'.".format(cv.name))
            pre_page = request.GET.get('from', "manage_cases")
            return redirect(pre_page)
    else:
        form = forms.EditCaseVersionForm(
            instance=caseversion, user=request.user)
    return TemplateResponse(
        request,
        "manage/case/edit_case.html",
        {
            "form": form,
            "caseversion": caseversion,
            }
        )


@require_POST
@permission_required("library.manage_cases")
def caseversion_clone(request, caseversion_id):
    """Clone caseversion for productversion, and redirect to edit new clone."""
    try:
        productversion = model.ProductVersion.objects.get(
            pk=request.POST["productversion"])
    except (model.ProductVersion.DoesNotExist, KeyError):
        return redirect(
            "manage_caseversion_edit", caseversion_id=caseversion_id)

    caseversion = get_object_or_404(model.CaseVersion, pk=caseversion_id)

    # if it exists already, just redirect to edit it
    try:
        target = model.CaseVersion.objects.get(
            case=caseversion.case, productversion=productversion)
    except model.CaseVersion.DoesNotExist:
        target = caseversion.clone(
            overrides={
                "productversion": productversion,
                "name": caseversion.name
                },
            user=request.user
            )
        messages.success(
            request,
            u"Created new version of '{0}' for {1}.".format(
                caseversion.name, productversion)
            )

    return redirect("manage_caseversion_edit", caseversion_id=target.id)
