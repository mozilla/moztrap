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
