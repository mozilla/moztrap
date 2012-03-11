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
Open Web Apps view.

"""
import json

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.template.response import TemplateResponse




def manifest(request):
    manifest = {"name": "Case Conductor",
                "description": "A Test Case and Results management System.",
                "launch_path": "/",
                "icons": {
                    "126": settings.STATIC_URL + "images/126x126.png"
                 },
                 "developer": {
                    "name": "Mozilla QA",
                    "url": "http://quality.mozilla.org"
                 }
             }
    return HttpResponse(
        json.dumps(manifest),
        content_type="application/x-web-app-manifest+json",
        )

def self_register(request):
    return TemplateResponse(request, "owa/self_register.html", {
        "manifest_url": request.build_absolute_uri(reverse("owa_manifest")),
        })


