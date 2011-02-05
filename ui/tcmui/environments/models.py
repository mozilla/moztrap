"""
Environment-related remote objects.

"""
from ..core.api import ListObject, fields
from ..core.models import CompanyLinkedRemoteObject



class EnvironmentType(CompanyLinkedRemoteObject):
    name = fields.Field()
    groupType = fields.Field()

    environments = fields.Link("EnvironmentList")


    def __unicode__(self):
        return u"%s%s" % (self.groupType and u"(Group Type) " or u"", self.name)



class EnvironmentTypeList(ListObject):
    entryclass = EnvironmentType
    api_name = "environmenttypes"
    default_url = "environmenttypes"

    entries = fields.List(fields.Object(EnvironmentType))



class Environment(CompanyLinkedRemoteObject):
    environmentType = fields.Locator(EnvironmentType)
    name = fields.Field()


    def __unicode__(self):
        return self.name



class EnvironmentList(ListObject):
    entryclass = Environment
    api_name = "environments"
    default_url = "environments"

    entries = fields.List(fields.Object(Environment))


    def summary(self):
        return u", ".join([e.name for e in self])



class EnvironmentGroup(CompanyLinkedRemoteObject):
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
