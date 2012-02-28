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
from contextlib import contextmanager
from cStringIO import StringIO
import os
from tempfile import mkstemp

from django.core.management import call_command

from mock import patch

from tests import case




class ImportCasesTest(case.DBTestCase):
    """Tests for import_cases management command."""

    def call_command(self, *args):
        """
        Runs the management command and returns (stdout, stderr) output.

        Also patch ``sys.exit`` so a ``CommandError`` doesn't cause an exit.

        """
        with patch("sys.stdout", StringIO()) as stdout:
            with patch("sys.stderr", StringIO()) as stderr:
                with patch("sys.exit"):
                    call_command("import", *args)

        stdout.seek(0)
        stderr.seek(0)
        return (stdout.read(), stderr.read())


    @contextmanager
    def tempfile(self, contents):
        """
        Write given contents to a temporary file, yielding its path.

        Used as a context manager; automatically deletes the temporary file
        when context manager exits.

        """
        (fd, path) = mkstemp()
        fh = os.fdopen(fd, "w")
        fh.write(contents)
        fh.close()

        try:
            yield path
        finally:
            os.remove(path)


    def test_no_args(self):
        """Command shows usage."""
        output = self.call_command()

        self.assertEqual(
            output,
            (
                "",
                "Error: Usage: <product_name> <product_version> <filename>\n",
                )
            )


    def test_bad_product(self):
        """Error if given non-existent product name."""
        output = self.call_command("Foo", "1.0", "file.json")

        self.assertEqual(
            output,
            (
                "",
                'Error: Product "Foo" does not exist\n',
                )
            )


    def test_bad_productversion(self):
        """Error if given non-existent product version."""
        self.F.ProductFactory.create(name="Foo")

        output = self.call_command("Foo", "1.0", "file.json")

        self.assertEqual(
            output,
            (
                "",
                'Error: Version "1.0" of product "Foo" does not exist\n',
                )
            )


    def test_bad_file(self):
        """Error if given nonexistent file."""
        self.F.ProductVersionFactory.create(product__name="Foo", version="1.0")

        output = self.call_command("Foo", "1.0", "does/not/exist.json")

        self.assertEqual(
            output,
            (
                "",
                (
                    'Error: Could not open "does/not/exist.json", '
                    "I/O error 2: No such file or directory\n"
                    ),
                )
            )


    def test_bad_json(self):
        """Error if file contains malformed JSON."""
        self.F.ProductVersionFactory.create(product__name="Foo", version="1.0")

        with self.tempfile("{") as path:
            output = self.call_command("Foo", "1.0", path)


        self.assertEqual(
            output,
            (
                "",
                (
                    "Error: Could not parse JSON: "
                    "Expecting property name: line 1 column 1 (char 1)\n"
                    ),
                )
            )


    def test_success(self):
        """Successful import prints summary data and creates objects."""
        self.F.ProductVersionFactory.create(product__name="Foo", version="1.0")

        with self.tempfile("{}") as path:
            output = self.call_command("Foo", "1.0", path)



        self.assertEqual(output, ("Imported 0 cases\nImported 0 suites\n", ""))
