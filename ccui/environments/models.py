# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
# 
# This file is part of Case Conductor.
# 
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
"""
Environment-related remote objects.

The nomenclature here is a massive pile of confusion, because the platform
follows one set of terminology that was determined to be too confusing for the
UI to use, so the UI uses a different set of terms. The translation, more or
less, takes place in this file and ccui/manage/views.py. Templates should
exclusively use UI terms.

Here, for reference, is a translation table with examples:

================================ ====================== ========================
         Platform                   UI                      Example
-------------------------------- ---------------------- ------------------------
EnvironmentType(groupType=True)  environment profile    Website Testing Envs
EnvironmentType(groupType=False) environment category   Operating System
EnvironmentGroup                 environment            Linux, English, Chrome
Environment                      environment element    Linux

"""
from collections import namedtuple

from ..core.api import RemoteObject, ListObject, fields, Named
from ..core.models import Company

from . import util


class EnvironmentType(Named, RemoteObject):
    """
    This resource conflates two objects that are really quite dissimilar into
    one resource (because that's how the platform does it).

    An EnvironmentType(groupType=True) is known in the UI as an "environment
    profile", e.g. "Website Testing Environments", and contains
    EnvironmentGroups (known in the UI as "environments"), e.g. "Linux,
    English, Chrome".

    An EnvironmentType(groupType=False) is known in the UI as an "environment
    category" (e.g. "Operating System") and contains Environments (known in the
    UI as "environment elements"), e.g. "Linux".

    """
    company = fields.Locator(Company)
    name = fields.CharField()
    groupType = fields.Field()

    _environments = fields.Link("EnvironmentList", "environments")


    @property
    def environmentgroups(self):
        if not self.groupType:
            return []
        return EnvironmentGroupList.get(auth=self.auth).filter(
            environmentType=self)


    @property
    def environmentgroups_prefetch(self):
        if not self.groupType:
            return []
        return ExplodedEnvironmentGroupList.get(auth=self.auth).filter(
            environmentType=self)


    @property
    def environmenttypes(self):
        if not self.groupType:
            return []
        typeids = set()
        types = {}
        for group in self.environmentgroups_prefetch:
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
        return self.name



class EnvironmentTypeList(ListObject):
    entryclass = EnvironmentType
    api_name = "environmenttypes"
    default_url = "environmenttypes"

    entries = fields.List(fields.Object(EnvironmentType))



class Environment(Named, RemoteObject):
    """
    This is an individual environment characteristic (e.g. "Linux" or
    "English"), known in the UI as an "environment element."

    Its environmentType attribute should be an
    EnvironmentType(groupType=False), or in UI terms an "environment category".

    """
    company = fields.Locator(Company)
    environmentType = fields.Locator(EnvironmentType)
    name = fields.CharField()


    # UI nomenclature
    @property
    def category(self):
        return self.environmentType


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



class BaseEnvironmentGroup(Named, RemoteObject):
    """
    This is a set of characteristics (e.g. "Linux, English, Chrome") that make
    up a full (in UI terms) "environment". It contains what the platform calls
    Environments (in UI terms, "environment elements").

    Its environmentType attribute should be an EnvironmentType(groupType=True),
    or a "profile" in UI terms.

    """
    company = fields.Locator(Company)
    environmentType = fields.Locator(EnvironmentType)
    name = fields.CharField()
    description = fields.CharField()

    non_field_filters = {
        "element": "includedEnvironmentId",
        }

    # UI nomenclature
    @property
    def elements(self):
        return self.environments


    @property
    def profile(self):
        return self.environmentType


    def __unicode__(self):
        return ", ".join(e.name for e in self.environments)


    def match(self, environments):
        """
        Return True if the given set of environments matches this environment
        group.

        If this environment group includes multiple environments of the same
        type (e.g. Windows 7 and Windows Vista), it will match a set of
        environments containing either one of those.

        """
        return util.match(environments, self.environments)



class EnvironmentGroup(BaseEnvironmentGroup):
    environments = fields.Link(EnvironmentList)



class ExplodedEnvironmentGroup(BaseEnvironmentGroup):
    """
    "Exploded" environment groups are environment groups where the API returns
    all the environment data as nested JSON, rather than requiring us to go
    fetch each individual environment separately.

    """
    api_name = "environmentgroup"
    environments = fields.List(
        fields.Object(Environment), api_name="ns1.environments")



HashableEnvironment = namedtuple("HashableEnvironment", ["name", "typename"])


class BaseEnvironmentGroupList(ListObject):
    api_name = "environmentgroups"
    default_url = "environmentgroups"


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



class EnvironmentGroupList(BaseEnvironmentGroupList):
    entryclass = EnvironmentGroup
    entries = fields.List(fields.Object(EnvironmentGroup))



class ExplodedEnvironmentGroupList(BaseEnvironmentGroupList):
    """
    "Exploded" environment groups are environment groups where the API returns
    all the environment data as nested JSON, rather than requiring us to go
    fetch each individual environment separately.

    """
    entryclass = ExplodedEnvironmentGroup
    default_url = "environmentgroups/exploded"
    array_name = "Environmentgroup"
    submit_ids_name = "environmentGroupIds"
    entries = fields.List(fields.Object(ExplodedEnvironmentGroup))
