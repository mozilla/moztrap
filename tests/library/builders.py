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
Model builders for library models (Suite, Case, CaseVersion, CaseStep).

"""



def create_suite(**kwargs):
    from cc.library.models import Suite

    defaults = {
        "name": "Test Suite",
        }

    defaults.update(kwargs)

    if "product" not in defaults:
        from ..core.builders import create_product
        defaults["product"] = create_product()

    return Suite.objects.create(**defaults)



def create_case(**kwargs):
    from cc.library.models import Case

    defaults = {
        }

    defaults.update(kwargs)

    if "product" not in defaults:
        from ..core.builders import create_product
        defaults["product"] = create_product()

    return Case.objects.create(**defaults)



def create_caseversion(**kwargs):
    from cc.library.models import CaseVersion

    defaults = {
        "name": "Test Case Version",
        }

    defaults.update(kwargs)

    if "case" not in defaults:
        defaults["case"] = create_case()

    if "number" not in defaults:
        try:
            defaults["number"] = defaults["case"].versions.order_by(
                "-number")[0].number + 1
        except IndexError:
            defaults["number"] = 1

    return CaseVersion.objects.create(**defaults)



def create_casestep(**kwargs):
    from cc.library.models import CaseStep

    defaults = {
        "instruction": "Test step instruction"
        }

    defaults.update(kwargs)

    if "caseversion" not in defaults:
        defaults["caseversion"] = create_caseversion()

    if "number" not in defaults:
        try:
            defaults["number"] = defaults["caseversion"].steps.order_by(
                "-number")[0].number + 1
        except IndexError:
            defaults["number"] = 1

    return CaseStep.objects.create(**defaults)
