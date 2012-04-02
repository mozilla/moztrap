#!/usr/bin/env python


"""
Runs a Django management command, using the vendor library.

"""
import os, sys
from moztrap.deploy.paths import add_vendor_lib

if __name__ == "__main__":
    add_vendor_lib()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moztrap.settings.default")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
