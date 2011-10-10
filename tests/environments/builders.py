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
from ..builder import ListBuilder
from ..responses import make_locator, make_boolean




environments = ListBuilder(
    "environment",
    "environments",
    "Environment",
    {
        "companyId": 1,
        "companyLocator": make_locator(
            id=1, url="companies/1", name="The Company"),
        "environmentTypeId": 1,
        "environmentTypeLocator": make_locator(
            id=1, url="environmenttypes/1", name="The Environment Type"),
        "name": "Default Environment",
        }
    )


environmentgroups = ListBuilder(
    "environmentgroup",
    "environmentgroups",
    "Environmentgroup",
    {
        "companyId": 1,
        "companyLocator": make_locator(
            id=1, url="companies/1", name="The Company"),
        "environmentTypeId": 1,
        "environmentTypeLocator": make_locator(
            id=1, url="environmenttypes/1", name="The Environment Type"),
        "description": "",
        "name": "Default Environmentgroup",
        }
    )


explodedenvironmentgroups = ListBuilder(
    "environmentgroup",
    "environmentgroups",
    "Environmentgroup",
    {
        "companyId": 1,
        "companyLocator": make_locator(
            id=1, url="companies/1", name="The Company"),
        "environmentTypeId": 1,
        "environmentTypeLocator": make_locator(
            id=1, url="environmenttypes/1", name="The Environment Type"),
        "description": "",
        "name": "Default Exploded Environmentgroup",
        "environments": environments.list({}, {})
        }
    )



environmenttypes = ListBuilder(
    "environmenttype",
    "environmenttypes",
    "Environmenttype",
    {
        "companyId": 1,
        "companyLocator": make_locator(
            id=1, url="companies/1", name="The Company"),
        "groupType": False,
        "parentEnvironmentTypeId": make_boolean(None),
        "parentEnvironmentTypeLocator": make_boolean(None),
        "sortOrder": 0,
        "name": "Default Environmenttype",
        }
    )
