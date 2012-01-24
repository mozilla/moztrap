#!/usr/bin/env python

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
Runs a Django management command, using the vendor library.

"""
import os, sys
from deploy.paths import add_vendor_lib

if __name__ == "__main__":
    add_vendor_lib()

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cc.settings.default")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
