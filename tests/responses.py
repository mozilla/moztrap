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
Fake JSON response generators for stubbing out API responses in tests.

"""
import httplib
import json
from posixpath import join

from ccui.core.conf import conf



def make_array(single_type, array_type, *args):
    """
    Given a list of single objects (as returned by ``make_one``), return a
    platform-style array.

    """
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
    """
    Given a list of single objects (as returned by ``make_one``), return a
    platform-style search result.

    """
    total = len(args)
    data = make_list(single_type, *args)
    return {
        "ns1.searchResult": [
            {
                "@xsi.type": "ns1.searchResult",
                "ns1.%s" % plural_type: data,
                "ns1.totalResults": total
                }
            ]
        }


def make_list(single_type, *args):
    """
    Given a list of single objects (as returned by ``make_one``), return the
    list wrapped as the platform does for a nested list.

    """
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
    return data



def make_one(resource_type, **kwargs):
    """
    Given a ``resource_type`` string and a dictionary of data, return a data
    structure that matches the platform's representation of an object of that
    type.

    """
    data = dict(("ns1.%s" % k, v) for k, v in kwargs.items())
    data["@xsi.type"] = "ns1:%s" % resource_type
    return data



def make_identity(id="1", url="some/url", version="0"):
    return {
        "@id": str(id),
        "@url": join(conf.CC_API_BASE, url),
        "@version": str(version),
        "@xsi.type": "ns1:resourceIdentity",
        }



def make_locator(id="1", url="some/url", name="Some Name"):
    return {
        "@id": str(id),
        "@name": name,
        "@url": join(conf.CC_API_BASE, url),
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



def make_error(message):
    return {"errors": [{"error": message }]}



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
