"""
Management command to create default roles, if they don't exist.

"""
from django.core.management.base import NoArgsCommand

from moztrap.model.core.auth import Role, Permission



ROLES = {}

# Testers have read-only permissions, aside from running tests.
ROLES["Tester"] = [
    "execution.execute",
    ]

# Test Creators can create new test cases and add/remove them from suites.
ROLES["Test Creator"] = [
    "library.create_cases",
    "library.manage_suite_cases",
    ] + ROLES["Tester"]

# Test Managers can fully manage cases, suites, runs, environments, etc.
ROLES["Test Manager"] = [
    "core.manage_products",
    "library.manage_cases",
    "library.manage_suites",
    "tags.manage_tags",
    "execution.manage_runs",
    "execution.review_results",
    "environments.manage_environments",
    ] + ROLES["Test Creator"]

# Admins can also manage users and products
ROLES["Admin"] = [
    "core.manage_users",
    ] + ROLES["Test Manager"]



class Command(NoArgsCommand):
    help = ("Create default user roles (unless they already exist).")

    def handle_noargs(self, **options):
        verbosity = int(options.get('verbosity', 1))

        for role_name, perms in ROLES.iteritems():
            role, created = Role.objects.get_or_create(name=role_name)
            if not created:
                if verbosity:
                    print("Role %r already exists; skipping." % role_name)
                continue # pragma: no cover http://bugs.python.org/issue2506

            if verbosity:
                print("Role %r created." % role_name)

            for perm_label in perms:
                app_label, codename = perm_label.split(".")
                try:
                    perm = Permission.objects.get(
                        content_type__app_label=app_label,
                        codename=codename)
                except Permission.DoesNotExist:
                    if verbosity:
                        print("  Permission %r unknown; skipping." % perm_label)
                    continue # pragma: no cover http://bugs.python.org/issue2506

                role.permissions.add(perm)

                if verbosity:
                    print("  Permission %r added." % perm_label)
