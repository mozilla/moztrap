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
Product-related remote objects.

"""
from ..core.api import ListObject, RemoteObject, fields, Named
from ..core.models import Company
from ..core.util import id_for_object
from ..environments.models import (
    EnvironmentGroupList, ExplodedEnvironmentGroupList)
from ..users.models import Team



class Product(Named, RemoteObject):
    company = fields.Locator(Company)
    description = fields.Field()
    name = fields.Field()

    environmentgroups = fields.Link(EnvironmentGroupList)
    environmentgroups_prefetch = fields.Link(
        ExplodedEnvironmentGroupList, api_name="environmentgroups/exploded")
    team = fields.Link(Team, api_name="team/members")

    @property
    def testcycles(self):
        from ..testexecution.models import TestCycleList

        return TestCycleList.get(auth=self.auth).filter(product=self)


    non_field_filters = {
        "tester": "teamMemberId",
        "environment": "includedEnvironmentId",
        }


    def __unicode__(self):
        return self.name


    def _get_profile(self):
        return self.environmentgroups[0].environmentType


    def _set_profile(self, val):
        self.environmentgroups = val.environmentgroups


    profile = property(_get_profile, _set_profile)


    def autogenerate_env_groups(self, environments, envtype=None, **kwargs):
        """
        Autogenerate environment groups for all combinations of given
        ``environments`` (should be an iterable of Environments or Environment
        IDs), optionally generating only groups of type ``envtype`` (should be
        an EnvironmentType with groupType=True, or the ID of one).

        """
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



class ProductList(ListObject):
    entryclass = Product
    api_name = "products"
    default_url = "products"

    entries = fields.List(fields.Object(Product))
