"""
Utility base TestCase classes for MozTrap.

django.utils.unittest.TestCase provides a bare TestCase class for tests that
don't access the database or need any of the other Django TestCase class
utilities.

DBTestCase is a Django TestCase, plus some MT-specific helpers.

View and admin test case classes (using WebTest) are available from the view
and admin sub-modules.

"""
from . import admin
from . import api
from . import view
from .base import TestCase, DBTestCase, TransactionTestCase
