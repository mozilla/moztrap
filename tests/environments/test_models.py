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
from mock import patch

from ..responses import response
from ..utils import ResourceTestCase, BaseResourceTest

from .builders import (
    environments, environmentgroups, explodedenvironmentgroups,
    environmenttypes)



@patch("ccui.core.api.userAgent")
class EnvironmentTypeTest(BaseResourceTest, ResourceTestCase):
    def get_resource_class(self):
        from ccui.environments.models import EnvironmentType
        return EnvironmentType


    def get_resource_list_class(self):
        from ccui.environments.models import EnvironmentTypeList
        return EnvironmentTypeList


    def test_environmentgroups_prefetch(self, http):
        http.request.return_value = response(
            environmenttypes.one(groupType=True))
        egt = self.resource_class.get("environmenttypes/1", auth=self.auth)
        egt.deliver()

        http.request.return_value = response(
            explodedenvironmentgroups.array({}, {}, {}))

        self.assertEqual(len(egt.environmentgroups_prefetch), 3)


@patch("ccui.core.api.userAgent")
class EnvironmentGroupTest(BaseResourceTest, ResourceTestCase):
    builder = environmentgroups

    def get_resource_class(self):
        from ccui.environments.models import EnvironmentGroup
        return EnvironmentGroup


    def get_resource_list_class(self):
        from ccui.environments.models import EnvironmentGroupList
        return EnvironmentGroupList


    def test_put_list(self, http):
        # This is especially for Exploded env groups, to make sure they
        # submit using the right querystring names.
        http.request.return_value = response(self.builder.array(
                {"_id": 1}, {"_id": 2}))

        egl = self.resource_list_class.get(auth=self.auth)

        egl.put()

        req = http.request.call_args_list[1][1]

        self.assertEqual(
            req["body"], "environmentGroupIds=1&environmentGroupIds=2")


    @patch("ccui.environments.util.match")
    def test_match(self, match, http):
        """
        The logic in util.match can be tested independently; here we just test
        that it ends up getting called with the right sets of environments.

        """
        from ccui.environments.models import EnvironmentList

        envs = EnvironmentList()
        envs.update_from_dict(environments.searchresult({}, {}, {}))

        http.request.return_value = response(self.builder.one())

        group = self.resource_class.get("environmentgroups/1", auth=self.auth)
        group.deliver()

        http.request.return_value = response(
            environments.searchresult({}, {}))

        match.return_value = False

        result = group.match(envs)

        match_args = match.call_args[0]

        self.assertEqual(result, False)
        self.assertSameResourceList(envs, match_args[0])
        self.assertSameResourceList(group.environments, match_args[1])



class ExplodedEnvironmentGroupTest(EnvironmentGroupTest):
    """
    Exploded environment groups should behave just like their non-exploded
    counterparts, so we run them through the same tests.

    """
    builder = explodedenvironmentgroups

    def get_resource_class(self):
        from ccui.environments.models import ExplodedEnvironmentGroup
        return ExplodedEnvironmentGroup


    def get_resource_list_class(self):
        from ccui.environments.models import ExplodedEnvironmentGroupList
        return ExplodedEnvironmentGroupList
