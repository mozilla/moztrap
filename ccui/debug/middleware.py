# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
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
import logging

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.http import HttpResponse



log = logging.getLogger("ccui.core.middleware.RequestLogMiddleware")



class RequestLogMiddleware(object):
    def process_request(self, request):
        log.debug(
            "%(method)s %(url)s",
            {
                "method": request.method,
                "url": request.get_full_path(),
                "request": request
                }
            )



class AjaxTracebackMiddleware(object):
    def __init__(self):
        if not settings.DEBUG:
            raise MiddlewareNotUsed


    def process_exception(self, request, *args, **kwargs):
        if request.is_ajax():
            import traceback
            return HttpResponse(traceback.format_exc().replace("\n", "<br>\n"))
