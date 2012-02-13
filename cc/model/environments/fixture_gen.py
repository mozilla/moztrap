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
"""Sample environments fixture generator."""
import itertools

from fixture_generator import fixture_generator

from ..core.auth import User
from .models import Profile, Environment, Element, Category

@fixture_generator(
    Profile, Category, Element, Environment, requires=["core.sample_users"])
def sample_environments():
    admin = User.objects.get(username="admin")

    webenvs = Profile.objects.create(
        name="Website Testing Environments", user=admin)
    browserenvs = Profile.objects.create(
        name="Browser Testing Environments", user=admin)

    browser = Category.objects.create(name="Browser", user=admin)
    browsers = {}
    for name in ["Firefox", "Safari", "Chrome", "Internet Explorer"]:
        browsers[name] = Element.objects.create(
            name=name, category=browser, user=admin)

    language = Category.objects.create(name="Language", user=admin)
    languages = {}
    for name in ["English", "Spanish", "Mandarin", "French", "German"]:
        languages[name] = Element.objects.create(
            name=name, category=language, user=admin)

    os = Category.objects.create(name="Operating System", user=admin)
    oses = {}
    for name in ["Windows", "Linux", "OS X"]:
        oses[name] = Element.objects.create(name=name, category=os, user=admin)

    for elements in itertools.product(
            browsers.values(), languages.values(), oses.values()):
        if (browsers["Internet Explorer"] in elements and
                oses["Windows"] not in elements):
            continue
        if browsers["Safari"] in elements and oses["Linux"] in elements:
            continue
        env = Environment.objects.create(profile=webenvs, user=admin)
        env.elements.add(*elements)

    for elements in itertools.product(languages.values(), oses.values()):
        env = Environment.objects.create(profile=browserenvs, user=admin)
        env.elements.add(*elements)
