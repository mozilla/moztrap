"""
Core remote objects.

"""
from .api import TCMRemoteObject, TCMListObject, fields



class Company(TCMRemoteObject):
    # @@@
    # identity = ResourceIdentityField()
    address = fields.Field()
    city = fields.Field()
    # @@@
    # country = StaticDataField("COUNTRY")
    name = fields.Field()
    phone = fields.Field()
    url = fields.Field()
    zip = fields.Field()



class CompanyList(TCMListObject):
    entryclass = Company
    api_name = "companies"

    entries = fields.List(fields.Object(Company))
