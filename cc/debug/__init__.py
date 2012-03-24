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
