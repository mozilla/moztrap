"""
Core remote objects.

"""
from . import api



class Company(api.RemoteObject):
    # @@@
    # identity = ResourceIdentityField()
    address = api.Field()
    city = api.Field()
    # @@@
    # country = StaticDataField("COUNTRY")
    name = api.Field()
    phone = api.Field()
    url = api.Field()
    zip = api.Field()



class CompanyList(api.ListObject):
    entryclass = Company
    api_name = "companies"

    entries = api.List(api.Object(Company))
