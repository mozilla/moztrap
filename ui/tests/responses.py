"""
Fake JSON response generators for stubbing out API responses in tests.

"""
import httplib
import json
from posixpath import join

from tcmui.core.conf import conf



def make_array(single_type, array_type, *args):
    objects = list(args)
    total = len(objects)
    if total == 1:
        # simulate broken length-1 lists from BadgerFish XML translation
        objects = objects[0]
    data = {"@xsi.type": "ns1.ArrayOf%s" % array_type}
    # when there are no objects, platform omits the key entirely
    if objects:
        data["ns1.%s" % single_type] = objects
    return {"ns1.ArrayOf%s" % array_type: [data]}



def make_searchresult(single_type, plural_type, *args):
    objects = list(args)
    total = len(objects)
    if total == 1:
        # simulate broken length-1 lists from BadgerFish XML translation
        objects = objects[0]
    # when there are no objects, platform sends empty string in place of dict
    if objects:
        data = {"ns1.%s" % single_type: objects}
    else:
        data = ""
    return {
        "ns1.searchResult": [
            {
                "@xsi.type": "ns1.searchResult",
                "ns1.%s" % plural_type: data,
                "ns1.totalResults": total
                }
            ]
        }



def make_one(resource_type, defaults=None, **kwargs):
    if defaults:
        for k, v in defaults.items():
            kwargs.setdefault(k, v)

    if kwargs.pop("add_identity", True):
        kwargs.setdefault("resourceIdentity", make_identity())
    if kwargs.pop("add_timeline", True):
        kwargs.setdefault("timeline", make_timeline())

    data = dict(("ns1.%s" % k, v) for k, v in kwargs.items())
    data["@xsi.type"] = "ns1:%s" % resource_type
    return data



def make_list(resource_type, *dicts, **kwargs):
    defaults = kwargs.pop("defaults", None)
    ret = []
    for i, info in enumerate(dicts):
        if kwargs.get("add_identity", True):
            info.setdefault("resourceIdentity", make_identity(id=i+1))
        info.update(kwargs)
        ret.append(make_one(resource_type, defaults=defaults, **info))
    return ret



def make_identity(id="1", url="some/url", version="0"):
    return {
        "@id": str(id),
        "@url": join(conf.TCM_API_BASE, url),
        "@version": str(version),
        "@xsi.type": "ns1:resourceIdentity",
        }


def make_locator(id="1", url="some/url"):
    return {
        "@id": str(id),
        "@url": join(conf.TCM_API_BASE, url),
        "@xsi.type":"ns1:ResourceLocator"}


def make_timeline(createDate=None, createdBy="1",
                  lastChangeDate=None, lastChangedBy="1"):
    return {
        "@createDate": createDate or "2010-10-18T00:00:00Z",
        "@createdBy": createdBy,
        "@lastChangeDate": lastChangeDate or "2010-10-18T00:00:00Z",
        "@lastChangedBy": lastChangedBy,
        "@xsi.type": "ns1:Timeline",
        }



def make_boolean(val):
    if val is None:
        return { "@xsi.nil": "true" }
    return {
        "xsd.boolean":
            [{"@xsi.type":"xsd:boolean","$":"true" if val else "false"}]
        }



def response(content="", status=httplib.OK, headers=None):
    headers = headers or {}
    if content:
        headers.setdefault("content-type", "application/json")
        if headers["content-type"] == "application/json":
            content = json.dumps(content)
    return (FakeResponse(status, headers=headers), content)



class FakeResponse(dict):
    def __init__(self, status, headers=None):
        self.status = status
        self.reason = ""
        if headers:
            for k, v in headers.iteritems():
                self[k.lower()] = v
