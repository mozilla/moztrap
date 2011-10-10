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
from mock import patch, Mock

from ..environments.builders import (
    environmenttypes, environmentgroups, environments)
from ..responses import response, make_boolean
from ..utils import ResourceTestCase, BaseResourceTest
from .builders import products



@patch("ccui.core.api.userAgent")
class ProductTest(BaseResourceTest, ResourceTestCase):
    def get_resource_class(self):
        from ccui.products.models import Product
        return Product


    def get_resource_list_class(self):
        from ccui.products.models import ProductList
        return ProductList


    def test_unicode(self, http):
        p = self.resource_class()
        p.update_from_dict(products.one(name="The Product"))

        self.assertEqual(unicode(p), u"The Product")


    def test_set_profile(self, http):
        from ccui.environments.models import EnvironmentGroupList

        http.request.return_value = response(products.one(
                _url="products/1", _version=0))
        p = self.resource_class.get("/products/1")
        p.deliver()

        http.request.return_value = response(
            environmentgroups.array({"_id": 1}, {"_id": 2}))

        egt = Mock()
        egt.groupType = True
        egt.environmentgroups = EnvironmentGroupList.get(auth=self.auth)
        egt.environmentgroups.deliver()

        http.request.return_value = response(make_boolean(True))

        p.profile = egt

        # one to get product, one to get envgroups, one to set product envgroups
        self.assertEqual(http.request.call_count, 3)

        req = http.request.call_args_list[-1][1]

        self.assertEqual(req["method"], "PUT")
        self.assertEqual(
            req["uri"],
            "http://fake.base/rest/products/1/environmentgroups?_type=json")
        self.assertEqual(
            req["body"],
            "originalVersionId=0&environmentGroupIds=1&environmentGroupIds=2")


    def test_autogenerate_env_groups(self, http):
        from ccui.environments.models import (
            EnvironmentGroupList, Environment, EnvironmentType)

        p = self.resource_class()
        p.update_from_dict(products.one(_url="products/1"))

        egt = EnvironmentType()
        egt.update_from_dict(environmenttypes.one(groupType=True))

        eta = EnvironmentType()
        eta.update_from_dict(environmenttypes.one(groupType=False, _id=1))

        etb = EnvironmentType()
        etb.update_from_dict(environmenttypes.one(groupType=False, _id=2))

        enva1 = Environment()
        enva1.update_from_dict(environments.one(_id=3, environmentType=eta))
        enva2 = Environment()
        enva2.update_from_dict(environments.one(_id=4, environmentType=eta))

        envb1 = Environment()
        envb1.update_from_dict(environments.one(_id=5, environmentType=etb))
        envb2 = Environment()
        envb2.update_from_dict(environments.one(_id=6, environmentType=etb))

        http.request.return_value = response(
            environmentgroups.array({}, {}, {}, {}))

        generated = p.autogenerate_env_groups([enva1, enva2, envb1, envb2], egt)

        self.assertIsInstance(generated, EnvironmentGroupList)
        self.assertEqual(len(generated), 4)
        req = http.request.call_args[1]
        self.assertEqual(req["uri"], "http://fake.base/rest/products/1/environmentgroups/environmenttypes/1/autogenerate?_type=json")
        self.assertEqual(req["body"], "environmentIds=3&environmentIds=4&environmentIds=5&environmentIds=6&originalVersionId=0")


    def test_autogenerate_env_groups_no_type(self, http):
        from ccui.environments.models import (
            EnvironmentGroupList, Environment, EnvironmentType)

        p = self.resource_class()
        p.update_from_dict(products.one(_url="products/1"))

        eta = EnvironmentType()
        eta.update_from_dict(environmenttypes.one(groupType=False, _id=1))

        etb = EnvironmentType()
        etb.update_from_dict(environmenttypes.one(groupType=False, _id=2))

        enva1 = Environment()
        enva1.update_from_dict(environments.one(_id=3, environmentType=eta))
        enva2 = Environment()
        enva2.update_from_dict(environments.one(_id=4, environmentType=eta))

        envb1 = Environment()
        envb1.update_from_dict(environments.one(_id=5, environmentType=etb))
        envb2 = Environment()
        envb2.update_from_dict(environments.one(_id=6, environmentType=etb))

        http.request.return_value = response(
            environmentgroups.array({}, {}, {}, {}))

        generated = p.autogenerate_env_groups([enva1, enva2, envb1, envb2])

        self.assertIsInstance(generated, EnvironmentGroupList)
        self.assertEqual(len(generated), 4)
        req = http.request.call_args[1]
        self.assertEqual(req["uri"], "http://fake.base/rest/products/1/environmentgroups/autogenerate?_type=json")
        self.assertEqual(req["body"], "environmentIds=3&environmentIds=4&environmentIds=5&environmentIds=6&originalVersionId=0")
