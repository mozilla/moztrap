import httplib
import json
from logging import Formatter
import textwrap



class HTMLRequestFormatter(Formatter):
    def format(self, record):
        if "uri" in record.args:
            return self.format_request_response(record)

        elif "request" in record.args:
            return self.format_ui_request(record)

        return self.format_other(record)


    def format_request_response(self, record):
        cachekey = record.args.get("cache_key") or ""
        request = record.args["request"]
        response = record.args["response"]
        content = record.args["content"]

        return textwrap.dedent("""\
            <details class="apicall %(cached)s">
              <summary>
                <span class="method">%(method)s</span>
                <span class="uri">%(uri)s</span>
                <span class="status_code">%(status_code)s</span>
                <span class="status">%(status)s</span>
              </summary>
              <span class="cachekey">%(cachekey)s</span>
              <details class="request">
                <summary>Request</summary>
                <details class="headers">
                  <summary>Headers</summary>
                  <dl>
                    %(request_headers)s
                  </dl>
                </details>
                <pre>%(request_body)s</pre>
              </details>
              <details class="response">
                <summary>Response</summary>
                <details class="headers">
                  <summary>Headers</summary>
                  <dl>
                    %(response_headers)s
                  </dl>
                </details>
                <pre>%(response_body)s</pre>
              </details>
            </details>
            """) % {
            "cached": cachekey and "cached" or "",
            "cachekey": cachekey,
            "method": record.args["method"],
            "uri": record.args["uri"],
            "status_code": response.status,
            "status": httplib.responses[response.status],
            "request_headers": self._format_headers(request["headers"], 8),
            "request_body": self._format_body(
                    request.get("body", ""),
                    request["headers"].get("content-type", "")),
            "response_headers": self._format_headers(response, 8),
            "response_body": self._format_body(
                    content, response.get("content-type", "")),
            }


    def format_ui_request(self, record):
        request = record.args["request"]
        return textwrap.dedent("""\
            <details class="ui request">
              <summary>%(message)s</summary>
              <details class="headers">
                <summary>META</summary>
                <dl class="headers">
                  %(headers)s
                </dl>
              </details>
              <pre class="content">%(content)s</pre>
            </details>
            """) % {
            "message": record.getMessage(),
            "headers": self._format_headers(request.META, 6),
            "content": request.raw_post_data,
            }


    def format_other(self, record):
        return '<p class="other">%s</p>' % record.getMessage()


    def _format_headers(self, headers, indent=0):
        joiner = "\n" + (" " * indent)
        return joiner.join(
            ["<dt>%s</dt><dd>%s</dd>" % (h, v) for (h, v) in headers.items()])


    def _format_body(self, content, content_type):
        if content_type.endswith("json"):
            return json.dumps(json.loads(content), indent=4)
        return content
