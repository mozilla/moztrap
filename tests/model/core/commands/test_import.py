"""
Tests for management command to import cases.

"""
from contextlib import contextmanager
from cStringIO import StringIO
import json
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

        self.assertIn("Error: Could not parse JSON: Expecting", output[1])


    def test_success(self):
        """Successful import prints summary data and creates objects."""
        self.F.ProductVersionFactory.create(product__name="Foo", version="1.0")

        data = {
            "cases": [{"name": "Foo", "steps": [{"instruction": "do this"}]}]}

        with self.tempfile(json.dumps(data)) as path:
            output = self.call_command("Foo", "1.0", path)

        self.assertEqual(output, ("Imported 1 cases\nImported 0 suites\n", ""))
        self.assertEqual(self.model.CaseVersion.objects.get().name, "Foo")
