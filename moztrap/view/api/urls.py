from django.conf.urls.defaults import patterns, url, include

from tastypie.api import Api

from moztrap.model.core import api as core
from moztrap.model.environments import api as environments
from moztrap.model.execution import api as execution
from moztrap.model.library import api as library
from moztrap.model.tags import api as tags
from moztrap.model import API_VERSION


v1_api = Api(api_name=API_VERSION)

v1_api.register(execution.RunResource())
v1_api.register(execution.RunCaseVersionResource())
v1_api.register(execution.ResultResource())
v1_api.register(execution.SuiteSelectionResource())
v1_api.register(library.CaseResource())
v1_api.register(library.CaseVersionResource())
v1_api.register(library.CaseStepResource())
v1_api.register(library.SuiteResource())
v1_api.register(library.CaseSelectionResource())
v1_api.register(library.CaseVersionSelectionResource())
v1_api.register(environments.EnvironmentResource())
v1_api.register(environments.ElementResource())
v1_api.register(environments.CategoryResource())
v1_api.register(core.ProductResource())
v1_api.register(core.ProductVersionResource())
v1_api.register(core.ProductVersionEnvironmentsResource())
v1_api.register(tags.TagResource())

urlpatterns = patterns(
    "moztrap.view.api",
    url(r"", include(v1_api.urls)),
)
