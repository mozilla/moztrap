"""
Environment-related remote objects.

"""
from ..core.api import RemoteObject, ListObject, fields
from ..core.models import Company

from . import util


class EnvironmentType(RemoteObject):
    company = fields.Locator(Company)
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


    def summary(self):
        return u", ".join([e.name for e in self])


    def match(self, environments):
        """
        Return True if the given set of environments matches this set of
        environments.

        If this set of environments includes multiple environments of the same
        type (e.g. Windows 7 and Windows Vista), it will match a set of
        environments containing either one of those.

        """
        return util.match(environments, self)



class EnvironmentGroup(RemoteObject):
    company = fields.Locator(Company)
    environmentType = fields.Locator(EnvironmentType)
    name = fields.Field()
    description = fields.Field()

    environments = fields.Link(EnvironmentList)


    def __unicode__(self):
        return self.name


    def match(self, environments):
        """
        Return True if the given set of environments matches this environment
        group.

        If this environment group includes multiple environments of the same
        type (e.g. Windows 7 and Windows Vista), it will match a set of
        environments containing either one of those.

        """
        return self.environments.match(environments)



class EnvironmentGroupList(ListObject):
    entryclass = EnvironmentGroup
    api_name = "environmentgroups"
    default_url = "environmentgroups"

    entries = fields.List(fields.Object(EnvironmentGroup))

    def match(self, environments):
        """
        If the given set of ``environments`` match any environment group in
        this environment group list, return that environment group. Else return
        None.

        """
        for group in self:
            if group.match(environments):
                return group
        return None
