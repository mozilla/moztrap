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
Model builders for test execution models.

Cycle, Run, RunCaseVersion, RunSuite, Result, StepResult

"""



def create_cycle(**kwargs):
    from cc.execution.models import Cycle

    defaults = {
        "name": "Test Cycle",
        }

    defaults.update(kwargs)

    if "product" not in defaults:
        from ..core.builders import create_product
        defaults["product"] = create_product()

    return Cycle.objects.create(**defaults)



def create_run(**kwargs):
    from cc.execution.models import Run

    defaults = {
        "name": "Test Run",
        }

    defaults.update(kwargs)

    if "cycle" not in defaults:
        defaults["cycle"] = create_cycle()

    return Run.objects.create(**defaults)



def create_runcaseversion(**kwargs):
    from cc.execution.models import RunCaseVersion

    defaults = {}
    defaults.update(kwargs)

    if "run" not in defaults:
        defaults["run"] = create_run()

    if "caseversion" not in defaults:
        from ..library.builders import create_caseversion
        defaults["caseversion"] = create_caseversion()

    return RunCaseVersion.objects.create(**defaults)



def create_runsuite(**kwargs):
    from cc.execution.models import RunSuite

    defaults = {}
    defaults.update(kwargs)

    if "run" not in defaults:
        defaults["run"] = create_run()

    if "suite" not in defaults:
        from ..library.builders import create_suite
        defaults["suite"] = create_suite()

    return RunSuite.objects.create(**defaults)



def create_result(**kwargs):
    from cc.execution.models import Result

    defaults = {}
    defaults.update(kwargs)

    if "tester" not in defaults:
        from ..core.builders import create_user
        defaults["tester"] = create_user()

    if "runcaseversion" not in defaults:
        defaults["runcaseversion"] = create_runcaseversion()

    if "environment" not in defaults:
        from ..environments.builders import create_environment
        defaults["environment"] = create_environment()

    return Result.objects.create(**defaults)



def create_stepresult(**kwargs):
    from cc.execution.models import StepResult

    defaults = {}
    defaults.update(kwargs)

    if "result" not in defaults:
        defaults["result"] = create_result()

    if "step" not in defaults:
        from ..library.builders import create_casestep
        defaults["step"] = create_casestep()

    return StepResult.objects.create(**defaults)
