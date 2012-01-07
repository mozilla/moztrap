# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
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
Model builders for environment models (Profile, Category, Element, Environment).

"""



def create_profile(**kwargs):
    from cc.environments.models import Profile

    defaults = {
        "name": "Test Profile",
        }

    defaults.update(kwargs)

    return Profile.objects.create(**defaults)



def create_category(**kwargs):
    from cc.environments.models import Category

    defaults = {
        "name": "Test Category",
        }

    defaults.update(kwargs)

    return Category.objects.create(**defaults)



def create_element(**kwargs):
    from cc.environments.models import Element

    defaults = {
        "name": "Test Element",
        }

    defaults.update(kwargs)

    if "category" not in defaults:
        defaults["category"] = create_category()

    return Element.objects.create(**defaults)



def create_environment(**kwargs):
    from cc.environments.models import Environment

    defaults = {}

    defaults.update(kwargs)

    if "profile" not in defaults:
        defaults["profile"] = create_profile()

    elements = defaults.pop("elements", None)
    if elements is None:
        elements = []

    env = Environment.objects.create(**defaults)
    env.elements.add(*elements)

    return env



def create_environments(category_names, *envs):
    """
    Create a set of environments given category and element names.

    Given a list of category names, and some number of same-length lists of
    element names, create and return a list of environments made up of the
    given elements. For instance::

      create_environments(
          ["OS", "Browser"],
          ["Windows", "Internet Explorer"],
          ["Windows", "Firefox"],
          ["Linux", "Firefox"]
          )

    """
    categories = [create_category(name=name) for name in category_names]

    environments = []

    for element_names in envs:
        elements = [
            create_element(name=name, category=categories[i])
            for i, name in enumerate(element_names)
            ]

        environments.append(create_environment(elements=elements))

    return environments
