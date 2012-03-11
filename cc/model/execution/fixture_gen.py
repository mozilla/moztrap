# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-12 Mozilla
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
"""Sample runs fixture generator."""
from fixture_generator import fixture_generator

from ..core.auth import User
from ..core.models import ProductVersion
from ..library.models import Suite

from .models import Run, RunSuite, RunCaseVersion

@fixture_generator(
    Run, RunSuite, RunCaseVersion, requires=[
        "library.sample_suites", "core.sample_users", "core.sample_products"])
def sample_runs():
    manager = User.objects.get(username="manager")

    accounts = Suite.objects.get(name="Accounts")

    cc8 = ProductVersion.objects.get(product=accounts.product, version="0.8")

    alpha = Run.objects.create(productversion=cc8, name="Alpha 1", user=manager)

    RunSuite.objects.create(run=alpha, suite=accounts)

    alpha.activate(user=manager)
