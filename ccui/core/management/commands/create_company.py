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


TESTER_ROLE_PERMISSIONS = set([
        "PERMISSION_COMPANY_INFO_VIEW",
        "PERMISSION_PRODUCT_VIEW",
        "PERMISSION_TEST_CASE_VIEW",
        "PERMISSION_TEST_SUITE_VIEW",
        "PERMISSION_TEST_CYCLE_VIEW",
        "PERMISSION_TEST_RUN_VIEW",
        "PERMISSION_TEST_RUN_ASSIGNMENT_EXECUTE",
        "PERMISSION_ENVIRONMENT_VIEW",
        "PERMISSION_USER_ACCOUNT_VIEW",
        "PERMISSION_TEAM_VIEW",
        "PERMISSION_EXTERNAL_BUG_VIEW",
        ])


TEST_CREATOR_ROLE_PERMISSIONS = TESTER_ROLE_PERMISSIONS.union(
    set([
        "PERMISSION_TEST_CASE_ADD",
        "PERMISSION_TEST_SUITE_EDIT",
        ]))


TEST_MANAGER_ROLE_PERMISSIONS = TEST_CREATOR_ROLE_PERMISSIONS.union(
    set([
        "PERMISSION_TEST_CASE_EDIT",
        "PERMISSION_TEST_CASE_APPROVE",
        "PERMISSION_TEST_CASE_ACTIVATE",
        "PERMISSION_TEST_SUITE_APPROVE",
        "PERMISSION_TEST_SUITE_ACTIVATE",
        "PERMISSION_TEST_CYCLE_EDIT",
        "PERMISSION_TEST_CYCLE_ACTIVATE",
        "PERMISSION_TEST_RUN_EDIT",
        "PERMISSION_TEST_RUN_ACTIVATE",
        "PERMISSION_TEST_RUN_TEST_CASE_ASSIGN",
        "PERMISSION_TEST_RUN_RESULT_APPROVE",
        "PERMISSION_ENVIRONMENT_EDIT", # @@@ required for tagging
        "PERMISSION_TEAM_EDIT",
        "PERMISSION_EXTERNAL_BUG_EDIT",
        ]))


ADMIN_ROLE_PERMISSIONS = TEST_MANAGER_ROLE_PERMISSIONS.union(
    set([
        "PERMISSION_COMPANY_USERS_VIEW",
        "PERMISSION_PRODUCT_EDIT",
        "PERMISSION_USER_ACCOUNT_EDIT",
        ]))


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

        roles = RoleList.get(auth=admin)

        tester_role = Role(name="Tester", company=company)
        roles.post(tester_role)

        tester_role.permissions = [
            p for p in PermissionList.get(auth=admin)
            if p.permissionCode in TESTER_ROLE_PERMISSIONS]

        creator_role = Role(name="Test Creator", company=company)
        roles.post(creator_role)

        creator_role.permissions = [
            p for p in PermissionList.get(auth=admin)
            if p.permissionCode in TEST_CREATOR_ROLE_PERMISSIONS]

        manager_role = Role(name="Test Manager", company=company)
        roles.post(manager_role)

        manager_role.permissions = [
            p for p in PermissionList.get(auth=admin)
            if p.permissionCode in TEST_MANAGER_ROLE_PERMISSIONS]

        admin_role = Role(name="Admin", company=company)
        roles.post(admin_role)

        admin_role.permissions = [
            p for p in PermissionList.get(auth=admin)
            if p.permissionCode in ADMIN_ROLE_PERMISSIONS]

        print (
            "Created company id %s, "
            "tester role id %s, test creator role id %s, "
            "manager role id %s, and admin role id %s."
            % (company.id,
               tester_role.id,
               creator_role.id,
               manager_role.id,
               admin_role.id)
            )
