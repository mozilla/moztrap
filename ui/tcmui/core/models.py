"""
Core remote objects.

"""
from .api import RemoteObject, ListObject, fields



class Company(RemoteObject):
    address = fields.Field()
    city = fields.Field()
    # @@@ country = fields.StaticDataField("COUNTRY")
    name = fields.Field()
    phone = fields.Field()
    url = fields.Field()
    zip = fields.Field()



class CompanyList(ListObject):
    entryclass = Company
    api_name = "companies"
    default_url = "companies"

    entries = fields.List(fields.Object(Company))
