from django.conf.urls.defaults import patterns, url, include
from django.views.generic.simple import direct_to_template

from .users.decorators import login_required
direct_to_template_login = login_required(direct_to_template)

urlpatterns = patterns(
    "",
    url("^$", "tcmui.products.views.product_list", name="products"),
    url("^account/", include("tcmui.users.urls")),

    url("^product/1/environment/$", direct_to_template_login, {"template": "test/environment.html"}, name="environment"),
    url("^product/1/cycles/$", direct_to_template_login, {"template": "test/cycles.html"}, name="cycles"),
    url("^product/1/cycles/1/$", direct_to_template_login, {"template": "test/run.html"}, name="run"),
    url("^manage/testcase/add/$", direct_to_template_login, {"template": "test/add_case.html"}, name="add"),
)
