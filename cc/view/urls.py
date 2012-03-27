# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-2012 Mozilla
#
# This file is part of Case Conductor.
#
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
"""
Case Conductor root URLconf.

"""
from django.conf.urls.defaults import patterns, url, include
from django.conf.urls.static import static
from django.conf import settings

from django.contrib import admin

admin.autodiscover()

import session_csrf
session_csrf.monkeypatch()


urlpatterns = patterns(
    "",
    url(r"^$", "cc.view.views.home", name="home"),

    # runtests ---------------------------------------------------------------
    url(r"^runtests/", include("cc.view.runtests.urls")),

    # users ------------------------------------------------------------------
    url(r"^users/", include("cc.view.users.urls")),

    # manage -----------------------------------------------------------------
    url(r"^manage/", include("cc.view.manage.urls")),

    # results ----------------------------------------------------------------
    url(r"^results/", include("cc.view.results.urls")),

    # admin ------------------------------------------------------------------
    url(r"^admin/", include(admin.site.urls)),

    # browserid --------------------------------------------------------------
    url(r"^browserid/", include("cc.view.users.browserid_urls")),

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
