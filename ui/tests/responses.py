"""
Fake JSON response generators for stubbing out API responses in tests.

"""
import json
from posixpath import join

from tcmui.core.conf import conf

COMPANY_DEFAULTS = {
    "name": "Default company name",
    "address": "Default company address",
    "city": "Default company city",
    "country": 239,
    "phone": "123-456-7890",
    "url": "www.example.com",
    "zip": "12345",
    }



def make_company(**kwargs):
    for k, v in COMPANY_DEFAULTS.items():
        kwargs.setdefault(k, v)
    return make_one("company", **kwargs)



def make_one(resource_type, **kwargs):
    kwargs.setdefault("resourceIdentity", make_resource_id())
    kwargs.setdefault("timeline", make_timeline())

    data = dict(("ns1.%s" % k, v) for k, v in kwargs.items())
    data["@xsi.type"] = "ns1:%s" % resource_type
    return data



def make_resource_id(id="1", url="some/url", version="0"):
    return {
        "@id": id,
        "@url": join(conf.TCM_API_BASE, url),
        "@version": version,
        "@xsi.type": "ns1:resourceIdentity",
        }



def make_timeline(createDate=None, createdBy="1",
                  lastChangeDate=None, lastChangedBy="1"):
    return {
        "@createDate": createDate or "2010-10-18T00:00:00Z",
        "@createdBy": createdBy,
        "@lastChangeDate": lastChangeDate or "2010-10-18T00:00:00Z",
        "@lastChangedBy": lastChangedBy,
        "@xsi.type": "ns1:Timeline",
        }



def response(status, content):
    return (FakeResponse(status, headers={"content-type": "application/json"}),
            json.dumps(content))



class FakeResponse(dict):
    def __init__(self, status, headers=None):
        self.status = status
        if headers:
            for k, v in headers.iteritems():
                self[k.lower()] = v
