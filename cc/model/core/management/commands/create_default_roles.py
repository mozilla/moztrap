# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-2012 Mozilla
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
Management command to create default roles, if they don't exist.

"""
from django.core.management.base import NoArgsCommand

from django.contrib.auth.models import Group, Permission



GROUPS = {}

# Testers have read-only permissions, aside from running tests.
GROUPS["Tester"] = [
    "execution.execute",
    ]

# Test Creators can create new test cases and add/remove them from suites.
GROUPS["Test Creator"] = [
    "library.create_cases",
    "library.manage_suite_cases",
    ] + GROUPS["Tester"]

# Test Managers can fully manage cases, suites, runs, environments, etc.
GROUPS["Test Manager"] = [
    "library.manage_cases",
    "library.manage_suites",
    "tags.manage_tags",
    "execution.manage_runs",
    "execution.review_results",
    "environments.manage_environments",
    ] + GROUPS["Test Creator"]

# Admins can also manage users and products
GROUPS["Admin"] = [
    "core.manage_products",
    "core.manage_users",
    ] + GROUPS["Test Manager"]



class Command(NoArgsCommand):
    help = ("Create default user roles (unless they already exist).")

    def handle_noargs(self, **options):
        verbosity = int(options.get('verbosity', 1))

        for group_name, perms in GROUPS.iteritems():
            group, created = Group.objects.get_or_create(name=group_name)
            if not created:
                if verbosity:
                    print("Role %r already exists; skipping." % group_name)
                continue

            if verbosity:
                print("Role %r created." % group_name)

            for perm_label in perms:
                app_label, codename = perm_label.split(".")
                try:
                    perm = Permission.objects.get(
                        content_type__app_label=app_label,
                        codename=codename)
                except Permission.DoesNotExist:
                    if verbosity:
                        print("  Permission %r unknown; skipping." % perm_label)
                    continue

                group.permissions.add(perm)

                if verbosity:
                    print("  Permission %r added." % perm_label)
