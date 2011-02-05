"""
Core remote objects.

"""
from .api import RemoteObject, ListObject, fields
from ..static.fields import StaticData
from . import conf


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



class CompanyLinked(object):
    company = fields.Locator(Company)


    @classmethod
    def ours(cls, **kwargs):
        return cls.get(**kwargs).filter(companyId=conf.TCM_COMPANY_ID)
