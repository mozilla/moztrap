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
from ..responses import make_locator



users = ListBuilder(
    "user",
    "users",
    "User",
    {
        "companyId": 1,
        "companyLocator": make_locator(
            id=1, url="companies/1", name="The Company"),
        "email": "test@example.com",
        "firstName": "Test",
        "lastName": "Person",
        "screenName": "test",
        "userStatusId": 1,
        }
    )


permissions = ListBuilder(
    "permission",
    "permissions",
    "Permission",
    {
        "assignable": True,
        "name": "",
        "permissionCode": "PERMISSION_MOCK"
        }
    )
