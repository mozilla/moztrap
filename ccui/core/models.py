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
Core remote objects.

"""
from .api import RemoteObject, ListObject, fields, Named
from .util import id_for_object
from ..static.fields import StaticData



# Fake Company ID constant
SYSTEM_WIDE = -22222



class Company(Named, RemoteObject):
    address = fields.Field()
    city = fields.Field()
    country = StaticData("COUNTRY")
    name = fields.Field()
    phone = fields.Field()
    url = fields.Field()
    zip = fields.Field()


    def __unicode__(self):
        return self.name


    def autogenerate_env_groups(self, environments, envtype=None, **kwargs):
        """
        Autogenerate environment groups for all combinations of given
        ``environments`` (should be an iterable of Environments or Environment
        IDs), optionally generating only groups of type ``envtype`` (should be
        an EnvironmentType with groupType=True, or the ID of one).

        """
        from ..environments.models import EnvironmentGroupList

        if envtype:
            url = ("environmentgroups/environmenttypes/%s/autogenerate"
                   % id_for_object(envtype))
        else:
            url = "environmentgroups/autogenerate"

        extra_payload = {
            "environmentIds": [id_for_object(e) for e in environments]}

        generated = EnvironmentGroupList()

        self._put(
            relative_url=url,
            extra_payload=extra_payload,
            update_from_response=generated,
            **kwargs)

        return generated



class CompanyList(ListObject):
    entryclass = Company
    api_name = "companies"
    default_url = "companies"

    entries = fields.List(fields.Object(Company))



class CategoryValueInfo(RemoteObject):
    categoryName = fields.Field()
    categoryValue = fields.Field()

    api_name = "CategoryValueInfo"


    def __unicode__(self):
        return u"%s: %s" % (self.categoryName, self.categoryValue)



class CategoryValueInfoList(ListObject):
    entryclass = CategoryValueInfo
    array_name = "CategoryValueInfo"

    entries = fields.List(fields.Object(CategoryValueInfo))


    def to_dict(self, enumclass, default=0):
        """
        Interpret the ``categoryName`` from each ``CategoryValueInfo`` as an
        identifier from the given enum class, and return a dictionary
        containing a key for every name in the enum, with values from each
        categoryValue, or ``default`` if no ``CategoryValueInfo`` is present
        for that enum value.

        For instance, given this enum:

        class SampleEnum(flufl.enum.Enum):
            ONE = 1
            TWO = 2

        If ``x`` is a ``CategoryValueInfoList`` containing a single
        ``CategoryValueInfo`` with categoryName=1 and categoryValue=5, a call
        to ``x.to_dict(SampleEnum)`` would return ``{"ONE": 5, "TWO": 0}``.

        """
        base = dict([(ev.enumname, default) for ev in enumclass])
        data = dict(
            [(enumclass[cvi.categoryName].enumname, cvi.categoryValue)
             for cvi in self])
        base.update(data)
        return base
