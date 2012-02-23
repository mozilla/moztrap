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
Tests for management command to import cases.

"""
from cStringIO import StringIO

from django.core.management import call_command

from mock import patch

from tests import case




class ImportCasesTest(case.DBTestCase):
    """Tests for import_cases management command."""

    def call_command(self, **kwargs):
        """Runs the management command under test and returns stdout output."""
        with patch("sys.stdout", StringIO()) as stdout:
            call_command("import_cases", **kwargs)

        stdout.seek(0)
        return stdout.read()


    def test_no_args(self):
        """Command shows usage."""
        self.call_command()

        self.assertRoles("Tester", "Test Creator", "Test Manager", "Admin")

    def test_imports_all_new(self):
        pass

    def test_imports_skip_existing(self):
        pass

    def test_skips_existing_roles(self):
        """Command skips roles that already exist."""
        self.model.Role.objects.create(name="Tester")

        output = self.call_command()

        self.assertIn("Role 'Tester' already exists; skipping.", output)

        self.assertRoles("Tester", "Test Creator", "Test Manager", "Admin")


    def test_unknown_permission(self):
        """Gracefully skips unknown permission."""
        with patch(
            "cc.model.core.management.commands.create_default_roles.ROLES",
            {"Foo": ["foo.foo"]}):
            output = self.call_command()

        self.assertIn("Permission 'foo.foo' unknown; skipping.", output)

        self.assertRoles("Foo")


    def test_normal_output(self):
        """Test output when all roles are created."""
        output = self.call_command()

        self.assertEqual(
            output,
            """Role 'Test Creator' created.
  Permission 'library.create_cases' added.
  Permission 'library.manage_suite_cases' added.
  Permission 'execution.execute' added.
Role 'Admin' created.
  Permission 'core.manage_products' added.
  Permission 'core.manage_users' added.
  Permission 'library.manage_cases' added.
  Permission 'library.manage_suites' added.
  Permission 'tags.manage_tags' added.
  Permission 'execution.manage_runs' added.
  Permission 'execution.review_results' added.
  Permission 'environments.manage_environments' added.
  Permission 'library.create_cases' added.
  Permission 'library.manage_suite_cases' added.
  Permission 'execution.execute' added.
Role 'Test Manager' created.
  Permission 'library.manage_cases' added.
  Permission 'library.manage_suites' added.
  Permission 'tags.manage_tags' added.
  Permission 'execution.manage_runs' added.
  Permission 'execution.review_results' added.
  Permission 'environments.manage_environments' added.
  Permission 'library.create_cases' added.
  Permission 'library.manage_suite_cases' added.
  Permission 'execution.execute' added.
Role 'Tester' created.
  Permission 'execution.execute' added.
""")


    def test_creates_all_quietly(self):
        """Test output when verbosity=0."""
        output = self.call_command(verbosity=0)

        self.assertEqual(output, "")


    def test_skips_existing_roles_quietly(self):
        """Command skips roles with no output when verbosity 0."""
        self.model.Role.objects.create(name="Tester")

        output = self.call_command(verbosity=0)

        self.assertEqual(output, "")


    def test_skips_unknown_permission_quietly(self):
        """Skips unknown permission silently with verbosity 0."""
        with patch(
            "cc.model.core.management.commands.create_default_roles.ROLES",
            {"Foo": ["foo.foo"]}):
            output = self.call_command(verbosity=0)

        self.assertEqual(output, "")
