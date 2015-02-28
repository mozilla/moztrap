"""
Tests for management command to import cases.

"""
from contextlib import contextmanager
from cStringIO import StringIO
import json
import os
from tempfile import mkstemp, mkdtemp

from django.core.management import call_command
from django.core.management.base import CommandError

from mock import patch

from tests import case




class ImportCasesTest(case.DBTestCase):
    """Tests for import_cases management command."""

    def call_command(self, *args, **kwargs):
        """
        Runs the management command and returns (stdout, stderr) output.

        Also patch ``sys.exit`` so a ``CommandError`` doesn't cause an exit.

        """
        with patch("sys.stdout", StringIO()) as stdout:
            with patch("sys.stderr", StringIO()) as stderr:
                with patch("sys.exit"):
                    call_command("import", *args, **kwargs)

        stdout.seek(0)
        stderr.seek(0)
        return (stdout.read(), stderr.read())


    @contextmanager
    def tempfile(self, contents, dir=None):
        """
        Write given contents to a temporary file, yielding its path.

        Used as a context manager; automatically deletes the temporary file
        when context manager exits.

        """
        (fd, path) = mkstemp(dir=dir)
        fh = os.fdopen(fd, "w")
        fh.write(contents)
        fh.close()

        try:
            yield path
        finally:
            os.remove(path)


    def test_no_args(self):
        """Command shows usage."""
        self.assertRaises(CommandError, self.call_command)


    def test_bad_product(self):
        """Error if given non-existent product name."""
        self.assertRaises(
            CommandError,
            self.call_command,
            "Foo", "1.0", "file.json"
        )


    def test_bad_productversion(self):
        """Error if given non-existent product version."""
        self.F.ProductFactory.create(name="Foo")

        self.assertRaises(
            CommandError,
            self.call_command,
            "Foo", "1.0", "file.json"
        )


    def test_bad_file(self):
        """Error if given nonexistent file."""
        self.F.ProductVersionFactory.create(product__name="Foo", version="1.0")

        self.assertRaises(
            CommandError,
            self.call_command,
            "Foo", "1.0", "does/not/exist.json"
        )


    def test_bad_json(self):
        """Error if file contains malformed JSON."""
        self.F.ProductVersionFactory.create(product__name="Foo", version="1.0")

        with self.tempfile("{") as path:
            self.assertRaises(
                CommandError,
                self.call_command,
                "Foo", "1.0", path
            )


    def test_success_single_file(self):
        """Successful import prints summary data and creates objects."""
        self.F.ProductVersionFactory.create(product__name="Foo", version="1.0")

        data = {
            "cases": [{"name": "Foo", "steps": [{"instruction": "do this"}]}]}

        with self.tempfile(json.dumps(data)) as path:
            output = self.call_command("Foo", "1.0", path)

        self.assertEqual(output, ("Imported 1 cases\nImported 0 suites\n", ""))
        self.assertEqual(self.model.CaseVersion.objects.get().name, "Foo")


    def test_success_single_file_with_dupes(self):
        """Successful import prints summary data and creates objects."""
        self.F.ProductVersionFactory.create(product__name="Foo", version="1.0")

        data = {
            "cases": [
                {"name": "Foo", "steps": [{"instruction": "do this"}]},
                {"name": "Foo", "steps": [{"instruction": "do this"}]},
                ]}

        with self.tempfile(json.dumps(data)) as path:
            output = self.call_command("Foo", "1.0", path, force_dupes=True)

        self.assertEqual(("Imported 2 cases\nImported 0 suites\n", ""), output)
        self.assertEqual(
            set(self.model.CaseVersion.objects.values_list("name", flat=True)),
            set(["Foo", "Foo"]))


    def test_success_single_file_skip_dupes(self):
        """Successful import of one case, second dupe is skipped."""
        self.F.ProductVersionFactory.create(product__name="Foo", version="1.0")

        data = {
            "cases": [
                {"name": "Foo", "steps": [{"instruction": "do this"}]},
                {"name": "Foo", "steps": [{"instruction": "do this"}]},
                ]}

        with self.tempfile(json.dumps(data)) as path:
            output = self.call_command("Foo", "1.0", path)

        self.assertEqual(
            "Skipped: Case with this name already exists for this product",
            output[0][:60],
            )
        self.assertEqual("", output[1])
        self.assertEqual(
            set(self.model.CaseVersion.objects.values_list("name", flat=True)),
            set(["Foo"]))


    def test_success_multiple_files(self):
        """Successful import prints summary data and creates objects."""
        self.F.ProductVersionFactory.create(product__name="Foo", version="1.0")

        data1 = {
            "cases": [{"name": "Foo", "steps": [{"instruction": "do this"}]}]}
        data2 = {
            "cases": [{"name": "Foo2", "steps": [{"instruction": "do this"}]}]}

        dir = mkdtemp()
        with self.tempfile(json.dumps(data1), dir=dir) as filepath:
            # create another file in that same directory
            with open("{0}/{1}".format(dir, "file2"), "w") as fh:
                fh.write(json.dumps(data2))
                fh.close()

            output = self.call_command("Foo", "1.0", dir)

        self.assertEqual(output, ("Imported 2 cases\nImported 0 suites\n", ""))
        self.assertEqual(
            set(self.model.CaseVersion.objects.values_list("name", flat=True)),
            set(["Foo", "Foo2"]))


    def test_skip_hidden_files(self):
        """Don't attempt to import hidden files in a directory."""
        self.F.ProductVersionFactory.create(product__name="Foo", version="1.0")

        data1 = {
            "cases": [{"name": "Foo", "steps": [{"instruction": "do this"}]}]}
        data2 = {
            "cases": [{"name": "Foo2", "steps": [{"instruction": "do this2"}]}]}

        dir = mkdtemp()
        with self.tempfile(json.dumps(data1), dir=dir) as filepath:
            # create another file in that same directory
            with open("{0}/{1}".format(dir, ".file2"), "w") as fh:
                fh.write(json.dumps(data2))
                fh.close()

            output = self.call_command("Foo", "1.0", dir)

        self.assertEqual(output, ("Imported 1 cases\nImported 0 suites\n", ""))
        self.assertEqual(self.model.CaseVersion.objects.get().name, "Foo")


    def test_no_files_in_dir(self):
        """Don't attempt to import hidden files in a directory."""
        self.F.ProductVersionFactory.create(product__name="Foo", version="1.0")

        dir = mkdtemp()
        output = self.call_command("Foo", "1.0", dir)

        self.assertEqual(output, ("No files found to import.\n", ""))
        self.assertEqual(self.model.CaseVersion.objects.count(), 0)
