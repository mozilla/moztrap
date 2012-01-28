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
All models.

"""
from django.contrib.auth.models import User, Permission

from .core.models import Product, ProductVersion
from .environments.models import Environment, Profile, Element, Category
from .execution.models import Run, RunSuite, RunCaseVersion, Result, StepResult
from .library.bulk import BulkParser
from .library.models import (
    Case, CaseVersion, CaseAttachment, CaseStep, Suite, SuiteCase)
from .tags.models import Tag
