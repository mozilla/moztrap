import httplib
import json

import logging
from logging import Formatter
from logging.handlers import MemoryHandler

from django.template.loader import render_to_string

from ..core.conf import conf


log = logging.getLogger("tcmui.core.log.api")

handler = MemoryHandler(capacity=conf.TCM_DEBUG_API_LOG_RECORDS)

if conf.TCM_DEBUG_API_LOG:
    log.setLevel(logging.DEBUG)
    log.addHandler(handler)
    ui_req_log = logging.getLogger("tcmui.core.middleware.RequestLogMiddleware")
    ui_req_log.setLevel(logging.DEBUG)
    ui_req_log.addHandler(handler)



def get_records():
    return reversed(handler.buffer)



class APILogHTMLFormatter(Formatter):
    def format(self, record):
        if "uri" in record.args:
            return self.format_apicall(record)

        elif "request" in record.args:
            return self.format_ui_request(record)

        return self.format_other(record)


    def formatTime(self, record, datefmt=None):
        if datefmt is None:
            datefmt = "%H:%M:%S"
        ret = Formatter.formatTime(self, record, datefmt)
        ret = "%s.%03d" % (ret, record.msecs)
        return ret


    def format_apicall(self, record):
        cachekey = record.args.get("cache_key") or ""
        request = record.args["request"]
        response = record.args["response"]
        content = record.args["content"]

        return render_to_string(
            "debug/apilog/_apicall.html",
            {
                "time": self.formatTime(record),
                "cachekey": cachekey,
                "method": record.args["method"],
                "uri": record.args["uri"],
                "status_code": response.status,
                "status": httplib.responses[response.status],
                "request_headers": request["headers"],
                "request_body": self._format_body(
                    request.get("body", ""),
                    request["headers"].get("content-type", "")),
                "response_headers": response,
                "response_body": self._format_body(
                    content, response.get("content-type", "")),
                })


    def format_ui_request(self, record):
        request = record.args["request"]
        return render_to_string(
            "debug/apilog/_uirequest.html",
            {
                "time": self.formatTime(record),
                "method": request.method,
                "uri": request.get_full_path(),
                "headers": request.META,
                "body": request.raw_post_data,
            })


    def format_other(self, record):
        return render_to_string(
            "debug/apilog/_other.html",
            {
                "time": self.formatTime(record),
                "message": record.getMessage()
                }
            )


    def _format_body(self, content, content_type):
        if content_type.endswith("json"):
            return json.dumps(json.loads(content), indent=4)
        return content



formatter = APILogHTMLFormatter()
