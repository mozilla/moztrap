"""
Environment-related remote objects.

"""
from ..core.api import RemoteObject, ListObject, fields
from ..core.models import Company



class EnvironmentType(RemoteObject):
    company = fields.Locator(Company)
    name = fields.Field()
    # @@@ broken in API, will be changed to 1/0?
    groupType = fields.Field()

    environments = fields.Link("EnvironmentList")


    def __unicode__(self):
        return self.name



class EnvironmentTypeList(ListObject):
    entryclass = EnvironmentType
    api_name = "environmenttypes"
    default_url = "environmenttypes"

    entries = fields.List(fields.Object(EnvironmentType))



class Environment(RemoteObject):
    company = fields.Locator(Company)
    environmentType = fields.Locator(EnvironmentType)
    name = fields.Field()


    def __unicode__(self):
        return self.name



class EnvironmentList(ListObject):
    entryclass = Environment
    api_name = "environments"
    default_url = "environments"

    entries = fields.List(fields.Object(Environment))



class EnvironmentGroup(RemoteObject):
    company = fields.Locator(Company)
    environmentType = fields.Locator(EnvironmentType)
    name = fields.Field()
    description = fields.Field()

    environments = fields.Link(EnvironmentList)


    def __unicode__(self):
        return self.name



class EnvironmentGroupList(ListObject):
    entryclass = EnvironmentGroup
    api_name = "environmentgroups"
    default_url = "environmentgroups"

    entries = fields.List(fields.Object(EnvironmentGroup))
