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
Utility base TestCase classes for Case Conductor.

django.utils.unittest.TestCase provides a bare TestCase class for tests that
don't access the database or need any of the other Django TestCase class
utilities.

DBTestCase is a Django TestCase, plus some CC-specific helpers.

View and admin test case classes (using WebTest) are available from the view
and admin sub-modules.

"""
from django.utils.unittest import TestCase

from . import admin
from . import view
from .base import DBTestCase, TransactionTestCase
