import json

from django.contrib import messages

from .conf import conf
from .auth import admin
from .models import Company



class StaticCompanyMiddleware(object):
    def __init__(self):
        self.company = Company.get(
            "companies/%s" % conf.TCM_COMPANY_ID,
            auth=admin
            )
        self.company.deliver()


    def process_request(self, request):
        request.company = self.company



class AjaxMessagesMiddleware(object):
    """
    Middleware to handle messages for AJAX requests

    If the AJAX response is already JSON, add a "messages" key to it (or append
    to an existing "messages" key) with a list of messages (each message is an
    object with "level", "message", and "tags" keys). If an existing key
    "no_messages" is present and True, messages will not be read or added.

    If the AJAX response is currently html, turn it into JSON and stuff the
    HTML content into the "html" key, adding a "messages" key as well.

    If the AJAX response is neither json nor html, return it as-is (with no
    messages attached, and without iterating over messages).

    """
    def process_response(self, request, response):
        if request.is_ajax():
            content_type = response['content-type'].split(";")[0]

            if content_type == "application/json":
                data = json.loads(response.content)
            elif content_type == "text/html":
                data = {"html": response.content}
            else:
                return response

            if not data.get("no_messages", False):
                messagelist = data.setdefault("messages", [])

                for message in messages.get_messages(request):
                    messagelist.append({
                        "level": message.level,
                        "message": message.message,
                        "tags": message.tags,
                    })

            response.content = json.dumps(data)
            response["content-type"] = "application/json"
        return response
