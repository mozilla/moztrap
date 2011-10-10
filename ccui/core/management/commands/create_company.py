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
from django.core.management.base import BaseCommand, CommandError

from ...auth import admin
from ...models import Company, CompanyList
from ....users.models import Role, RoleList, PermissionList


DEFAULT_NEW_USER_ROLE_PERMISSIONS = set([
        "PERMISSION_COMPANY_INFO_VIEW",
        "PERMISSION_PRODUCT_VIEW",
        "PERMISSION_TEST_CASE_VIEW",
        "PERMISSION_TEST_CASE_ADD",
        "PERMISSION_TEST_CYCLE_VIEW",
        "PERMISSION_TEST_RUN_VIEW",
        "PERMISSION_TEST_RUN_ASSIGNMENT_EXECUTE",
        "PERMISSION_TEST_SUITE_VIEW",
        "PERMISSION_ENVIRONMENT_VIEW",
        "PERMISSION_USER_ACCOUNT_VIEW",
        "PERMISSION_EXTERNAL_BUG_VIEW",
        ])

DEFAULT_ADMIN_ROLE_PERMISSIONS = set([
        "PERMISSION_COMPANY_INFO_VIEW",
        "PERMISSION_COMPANY_USERS_VIEW",
        "PERMISSION_PRODUCT_VIEW",
        "PERMISSION_PRODUCT_EDIT",
        "PERMISSION_TEST_CASE_VIEW",
        "PERMISSION_TEST_CASE_EDIT",
        "PERMISSION_TEST_CASE_ADD",
        "PERMISSION_TEST_CASE_APPROVE",
        "PERMISSION_TEST_CASE_ACTIVATE",
        "PERMISSION_TEST_SUITE_VIEW",
        "PERMISSION_TEST_SUITE_EDIT",
        "PERMISSION_TEST_SUITE_APPROVE",
        "PERMISSION_TEST_SUITE_ACTIVATE",
        "PERMISSION_TEST_PLAN_VIEW",
        "PERMISSION_TEST_PLAN_EDIT",
        "PERMISSION_TEST_PLAN_APPROVE",
        "PERMISSION_TEST_PLAN_ACTIVATE",
        "PERMISSION_TEST_CYCLE_VIEW",
        "PERMISSION_TEST_CYCLE_EDIT",
        "PERMISSION_TEST_CYCLE_ACTIVATE",
        "PERMISSION_TEST_RUN_VIEW",
        "PERMISSION_TEST_RUN_EDIT",
        "PERMISSION_TEST_RUN_ACTIVATE",
        "PERMISSION_TEST_RUN_TEST_CASE_ASSIGN",
        "PERMISSION_TEST_RUN_ASSIGNMENT_EXECUTE",
        "PERMISSION_TEST_RUN_RESULT_APPROVE",
        "PERMISSION_USER_ACCOUNT_VIEW",
        "PERMISSION_USER_ACCOUNT_EDIT",
        "PERMISSION_ENVIRONMENT_VIEW",
        "PERMISSION_ENVIRONMENT_EDIT",
        "PERMISSION_TEAM_VIEW",
        "PERMISSION_TEAM_EDIT",
        "PERMISSION_EXTERNAL_BUG_VIEW",
        "PERMISSION_EXTERNAL_BUG_EDIT",
        ])

class Command(BaseCommand):
    help = ("Create a company resource and associated default new user role "
            "with appropriate tester permissions.")
    args = '"Company Name"'

    def handle(self, *args, **options):
        if not args:
            raise CommandError("Company name is required.")
        name = " ".join(args)

        # @@@ U.S. is country ID 239, un-hardcode this
        company = Company(name=name, country=239)
        CompanyList.get(auth=admin).post(company)

        tester_role = Role(name="%s Tester" % name, company=company)
        RoleList.get(auth=admin).post(tester_role)

        tester_role.permissions = [
            p for p in PermissionList.get(auth=admin)
            if p.permissionCode in DEFAULT_NEW_USER_ROLE_PERMISSIONS]

        admin_role = Role(name="%s Admin" % name, company=company)
        RoleList.get(auth=admin).post(admin_role)

        admin_role.permissions = [
            p for p in PermissionList.get(auth=admin)
            if p.permissionCode in DEFAULT_ADMIN_ROLE_PERMISSIONS]

        print ("Created company id %s, tester role id %s and admin role id %s."
               % (company.id, tester_role.id, admin_role.id))
