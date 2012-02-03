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
from django.contrib.auth.models import User

from fixture_generator import fixture_generator

from ..core.models import Product
from ..tags.models import Tag

from .models import (
    Case, CaseVersion, Suite, SuiteCase, CaseStep, CaseAttachment)

@fixture_generator(
    Case, CaseVersion, CaseStep, CaseAttachment,
    requires=["core.sample_products", "tags.sample_tags", "core.sample_users"])
def sample_cases():
    manager = User.objects.get(username="manager")
    creator = User.objects.get(username="creator")

    cc = Product.objects.get(name="Case Conductor")
    cc6 = cc.versions.get(version="0.6")
    cc7 = cc.versions.get(version="0.7")
    cc8 = cc.versions.get(version="0.8")

    registration = Tag.objects.get(name="registration")

    login = Case.objects.create(product=cc, user=manager)
    login_data = {
        "name": "Can log in.",
        "case": login,
        "description": "A user can log in to the app.",
        "status": CaseVersion.STATUS.active,
        "user": manager,
        }
    login_steps = [
        {
            "instruction": "Click the login link in the upper right.",
            "expected": "See a form with username and password fields.",
            },
        {
            "instruction": "Fill in a valid username and password, submit.",
            "expected": "See a welcome message in the upper right.",
            },
        ]
    for pv in [cc6, cc7, cc8]:
        cv = CaseVersion.objects.create(**dict(login_data, productversion=pv))
        for i, step_data in enumerate(login_steps):
            CaseStep.objects.create(
                **dict(step_data, caseversion=cv, number=i, user=manager))

    register = Case.objects.create(product=cc, user=creator)
    register_data = {
        "name": "Can register.",
        "case": register,
        "description": "A new user can register for the app.",
        "status": CaseVersion.STATUS.active,
        "user": creator,
        }
    register_steps = [
        {
            "instruction": "Click the register link in the upper right.",
            "expected": "See a user registration form.",
            },
        {
            "instruction": "Fill in all fields, submit.",
            "expected": "Receive a verification email.",
            },
        ]
    for pv in [cc7, cc8]:
        cv = CaseVersion.objects.create(
            **dict(register_data, productversion=pv))
        if pv is cc8:
            cv.tags.add(registration)
        for i, step_data in enumerate(register_steps, 1):
            CaseStep.objects.create(
                **dict(step_data, caseversion=cv, number=i, user=creator))
        # registration not translated into Mandarin yet?
        for env in cv.environments.all():
            if any([el.name == "Mandarin" for el in env]):
                cv.environments.remove(env)

    ff = Product.objects.get(name="Firefox")
    ff9 = ff.versions.get(version="9")
    ff10 = ff.versions.get(version="10")

    key = Tag.objects.get(name="key")

    fast = Case.objects.create(product=ff, user=creator)
    fast_data = {
        "name": "It is fast.",
        "case": fast,
        "description": "It's a fast browser.",
        "user": creator,
        }
    for pv in [ff9, ff10]:
        cv = CaseVersion.objects.create(
            **dict(fast_data, productversion=pv))
        cv.tags.add(key)


@fixture_generator(Suite, SuiteCase, requires=["library.sample_cases"])
def sample_suites():
    manager = User.objects.get(username="manager")

    login = Case.objects.distinct().get(versions__name="Can log in.")
    register = Case.objects.distinct().get(versions__name="Can register.")

    accounts = Suite.objects.create(
        product=login.product,
        name="Accounts",
        status=Suite.STATUS.active,
        user=manager,
        )

    SuiteCase.objects.create(
        case=register, suite=accounts, order=1, user=manager)
    SuiteCase.objects.create(
        case=login, suite=accounts, order=2, user=manager)
