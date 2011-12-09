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
"""
Debug helpers, including apilog view.

To log details of all UI requests and platform API calls to an HTML file (in
this example, "/home/carljm/projects/mozilla/logs/apilog.html"), use a logging
config in your ``settings/local.py`` similar to this::

    LOGGING = {
        "version": 1,
        "formatters": {
            "html": {
                "()": "ccui.debug.apilog.APILogHTMLFormatter"
                }
            },
        "handlers": {
            "apilog": {
                "level": "DEBUG",
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "/home/carljm/projects/mozilla/logs/apilog.html",
                "maxBytes": 10000000,
                "backupCount": 10,
                "formatter": "html",
                }
            },
        "loggers": {
            "ccui.core.log.api": {
                "handlers": ["apilog"],
                "level": "DEBUG",
                },
            "ccui.core.middleware.RequestLogMiddleware": {
                "handlers": ["apilog"],
                "level": "DEBUG",
                },
            }
        }

"""
