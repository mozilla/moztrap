"""
Core remote objects.

"""
from .api import RemoteObject, ListObject, fields
from ..static.fields import StaticData


class Company(RemoteObject):
    address = fields.Field()
    city = fields.Field()
    country = StaticData("COUNTRY")
    name = fields.Field()
    phone = fields.Field()
    url = fields.Field()
    zip = fields.Field()


    def __unicode__(self):
        return self.name



class CompanyList(ListObject):
    entryclass = Company
    api_name = "companies"
    default_url = "companies"

    entries = fields.List(fields.Object(Company))


    def __unicode__(self):
        return u"%s Companies" % len(self)
