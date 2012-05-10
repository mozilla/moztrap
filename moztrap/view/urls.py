"""
MozTrap root URLconf.

"""
from django.conf.urls.defaults import patterns, url, include
from django.conf.urls.static import static
from django.conf import settings

from django.contrib import admin

from tastypie.api import Api

from moztrap.model.execution.api import RunResource, \
    RunCaseVersionResource, ResultResource

from moztrap.model.environments.api import EnvironmentResource, ElementResource
from moztrap.model.core.api import ProductResource, ProductVersionResource, UserResource

from moztrap.model.library.api import CaseVersionResource, CaseResource

from moztrap.model import mtadmin
from moztrap.model.mtresource import MTModelResource

admin.site = mtadmin.MTAdminSite()
admin.autodiscover()

import session_csrf
session_csrf.monkeypatch()

v1_api = Api(api_name=MTModelResource.API_VERSION)

v1_api.register(RunResource())
v1_api.register(RunCaseVersionResource())
v1_api.register(ResultResource())

v1_api.register(CaseResource())
v1_api.register(CaseVersionResource())

v1_api.register(EnvironmentResource())
v1_api.register(ElementResource())

v1_api.register(ProductResource())
v1_api.register(ProductVersionResource())
v1_api.register(UserResource())



run_resource = RunResource()

urlpatterns = patterns(
    "",
    url(r"^$", "moztrap.view.views.home", name="home"),

    # runtests ---------------------------------------------------------------
    url(r"^runtests/", include("moztrap.view.runtests.urls")),

    # users ------------------------------------------------------------------
    url(r"^users/", include("moztrap.view.users.urls")),

    # manage -----------------------------------------------------------------
    url(r"^manage/", include("moztrap.view.manage.urls")),

    # results ----------------------------------------------------------------
    url(r"^results/", include("moztrap.view.results.urls")),

    # admin ------------------------------------------------------------------
    url(r"^admin/", include(admin.site.urls)),

    # browserid --------------------------------------------------------------
    url(r"^browserid/", include("moztrap.view.users.browserid_urls")),

    # api --------------------------------------------------------------------
    url(r"^api/", include(v1_api.urls), name="api_dispatch"),

    ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
