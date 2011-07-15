"""
Environment-related remote objects.

"""
from collections import namedtuple

from ..core.api import RemoteObject, ListObject, fields
from ..core.models import Company

from . import util


class EnvironmentType(RemoteObject):
    company = fields.Locator(Company)
    name = fields.Field()
    groupType = fields.Field()

    _environments = fields.Link("EnvironmentList", "environments")


    @property
    def environmentgroups(self):
        if not self.groupType:
            return []
        return EnvironmentGroupList.get(auth=self.auth).filter(
            environmentType=self)


    @property
    def environmenttypes(self):
        if not self.groupType:
            return []
        typeids = set()
        types = {}
        for group in self.environmentgroups:
            for env in group.environments:
                et = env.environmentType
                typeids.add(et.id)
                types.setdefault(et.id, et)

        return [types[id] for id in typeids]


    # translate between platform and UI nomenclature
    @property
    def environments(self):
        # "environments" is a nomenclature collision, so we allow both uses
        # where they make sense.
        if self.groupType:
            # in UI terms, environment groups are "environments" - only for
            # group types ("profiles" in UI terms)
            return self.environmentgroups
        else:
            # non-group-types have environments (in platform terms)
            return self._environments


    @property
    def elements(self):
        if self.groupType:
            return []
        return self._environments


    categories = environmenttypes



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

    # UI nomenclature
    @property
    def elements(self):
        return self.environments


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


HashableEnvironment = namedtuple("HashableEnvironment", ["name", "typename"])


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


    def environments(self):
        """
        Return a list of all unique environments in this environment group list.

        Each environment is represented as a dictionary with keys "name" and
        "typename".

        """
        ret = set()
        for group in self:
            for env in group.environments:
                ret.add(
                    HashableEnvironment(
                        name=env.name, typename=env.environmentType.name)
                    )
        return sorted(ret, key=lambda e: e.typename)


    # UI nomenclature
    elements = environments
