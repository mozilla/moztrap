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
Core objects for accessing staticData API.

"""
import urlparse

import remoteobjects

from ..core.conf import conf
from ..core.api import ObjectMixin, fields



class CodeValue(ObjectMixin, remoteobjects.RemoteObject):
    id = fields.Field()
    description = fields.CharField()
    sortOrder = fields.Field()


    def __unicode__(self):
        return self.description


    def __repr__(self):
        return "<CodeValue: %s>" % self



class ArrayOfCodeValue(ObjectMixin, remoteobjects.ListObject):
    api_base_url = urlparse.urljoin(conf.CC_API_BASE, "staticData/values/")

    entries = fields.List(fields.Object(CodeValue))


    def update_from_dict(self, data):
        """
        Unwrap the JSON data.

        We expect to get data in a form like this:

        {
           "ns1.ArrayOfCodeValue":[
              {
                 "@xsi.type":"ns1:ArrayOfCodeValue",
                 "ns1.CodeValue":[
                    {
                       "@xsi.type":"ns1:CodeValue",
                       "ns1.description":"Active",
                       "ns1.id":1,
                       "ns1.sortOrder":0
                    },
                    {
                       "@xsi.type":"ns1:CodeValue",
                       "ns1.description":"Disabled",
                       "ns1.id":3,
                       "ns1.sortOrder":0
                    },
                    {
                       "@xsi.type":"ns1:CodeValue",
                       "ns1.description":"Inactive",
                       "ns1.id":2,
                       "ns1.sortOrder":0
                    }
                 ]
              }
           ]
        }

        We pass on the inner list of data dictionaries.

        """
        if "ns1.ArrayOfCodeValue" in data:
            data = data["ns1.ArrayOfCodeValue"][0]["ns1.CodeValue"]
            # Because this JSON is BadgerFish-translated XML
            # (http://ajaxian.com/archives/badgerfish-translating-xml-to-json)
            # length-1 lists are not sent as lists, so we re-listify.
            if "@xsi.type" in data:
                data = [data]
        return super(ArrayOfCodeValue, self).update_from_dict(data)
