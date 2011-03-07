from django.core.management.base import BaseCommand, CommandError

from ...api import admin
from ...models import Company, CompanyList
from ....users.models import Role, RoleList, PermissionList


DEFAULT_NEW_USER_ROLE_PERMISSIONS = set([
        "PERMISSION_COMPANY_INFO_VIEW",
        "PERMISSION_PRODUCT_VIEW",
        "PERMISSION_TEST_CASE_VIEW",
        "PERMISSION_TEST_CASE_EDIT",
        "PERMISSION_TEST_CYCLE_VIEW",
        "PERMISSION_TEST_RUN_VIEW",
        "PERMISSION_TEST_RUN_ASSIGNMENT_EXECUTE",
        "PERMISSION_ENVIRONMENT_VIEW",
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

        role = Role(name="%s Tester" % name, company=company)
        RoleList.get(auth=admin).post(role)

        permissions = [p for p in PermissionList.get(auth=admin)
                       if p.permissionCode in DEFAULT_NEW_USER_ROLE_PERMISSIONS]

        role.permissions = permissions

        print "Created company id %s and role id %s." % (company.id, role.id)
