from django.conf.urls.defaults import url, patterns

from ..core.conf import conf



urlpatterns = patterns("")

if conf.TCM_DEBUG_API_LOG:
    urlpatterns += patterns(
        "tcmui.debug.views",
        url("^apilog/$", "apilog", name="debug_apilog"),
        )
