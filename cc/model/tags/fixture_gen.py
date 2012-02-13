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
"""Sample cases and suites fixture generator."""
from fixture_generator import fixture_generator

from ..core.auth import User
from ..core.models import Product

from .models import Tag

@fixture_generator(Tag, requires=["core.sample_products", "core.sample_users"])
def sample_tags():
    admin = User.objects.get(username="admin")
    manager = User.objects.get(username="manager")

    cc = Product.objects.get(name="Case Conductor")

    Tag.objects.create(name="registration", product=cc, user=manager)

    Tag.objects.create(name="key", user=admin)
