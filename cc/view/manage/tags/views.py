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
Manage views for tags.

"""
import json

from django.http import HttpResponse

from django.contrib.auth.decorators import login_required

from ....model.tags.models import Tag



@login_required
def tag_autocomplete(request):
    """Return autocomplete list of existing tags in JSON format."""
    text = request.GET.get("text")
    if text is not None:
        tags = Tag.objects.filter(name__icontains=text)
    else:
        tags = []
    suggestions = []
    for tag in tags:
        # can't just use split due to case; we match "text" insensitively, but
        # want pre and post to be case-accurate
        start = tag.name.lower().index(text.lower())
        pre = tag.name[:start]
        post = tag.name[start+len(text):]
        suggestions.append({
                "preText": pre,
                "typedText": text,
                "postText": post,
                "id": tag.id,
                "name": tag.name,
                "type": "tag",
                })
    return HttpResponse(
        json.dumps(
            {
                "suggestions": suggestions
                }
            ),
        content_type="application/json",
        )
