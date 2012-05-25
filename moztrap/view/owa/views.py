"""
Open Web Apps view.

"""
import json

from django.conf import settings
from django.http import HttpResponse
from django.template.response import TemplateResponse




def manifest(request):
    manifest = {"name": "MozTrap",
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
