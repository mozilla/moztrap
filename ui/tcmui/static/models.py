"""
Core objects for accessing staticData API.

"""
import urlparse

import remoteobjects

from ..core import conf
from ..core.api import ObjectMixin, fields

class CodeValue(ObjectMixin, remoteobjects.RemoteObject):
    id = fields.Field()
    description = fields.Field()
    sortOrder = fields.Field()


    def __unicode__(self):
        return self.description


    def __repr__(self):
        return "<CodeValue: %s>" % self


class ArrayOfCodeValue(ObjectMixin, remoteobjects.ListObject):
    api_base_url = urlparse.urljoin(conf.TCM_API_BASE, "staticData/values/")

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
