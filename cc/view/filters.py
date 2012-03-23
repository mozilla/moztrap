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
List filtering options.

"""
from cc import model

from .lists import filters



class ProductFilterSet(filters.FilterSet):
    """FilterSet for Products."""
    filters = [
        filters.KeywordFilter("name"),
        filters.ModelFilter(
            "creator", lookup="created_by", queryset=model.User.objects.all()),
        ]



class ProductVersionFilterSet(filters.FilterSet):
    """FilterSet for Product versions."""
    filters = [
        filters.ModelFilter("product", queryset=model.Product.objects.all()),
        filters.KeywordFilter("version"),
        filters.KeywordFilter("codename"),
        filters.ModelFilter(
            "creator", lookup="created_by", queryset=model.User.objects.all()),
        filters.ModelFilter(
            "environment element",
            lookup="environments__elements",
            key="envelement",
            queryset=model.Element.objects.all()),
        ]



class RunFilterSet(filters.FilterSet):
    """FilterSet for runs."""
    filters = [
        filters.ChoicesFilter("status", choices=model.Run.STATUS),
        filters.ModelFilter(
            "product",
            lookup="productversion__product",
            queryset=model.Product.objects.all()),
        filters.ModelFilter(
            "productversion", queryset=model.ProductVersion.objects.all()),
        filters.KeywordFilter("name"),
        filters.KeywordFilter("description"),
        filters.ModelFilter(
            "suite",
            lookup="suites",
            queryset=model.Suite.objects.all()),
        filters.KeywordExactFilter(
            "case id", lookup="suites__cases__id", key="case", coerce=int),
        filters.ModelFilter(
            "creator", lookup="created_by", queryset=model.User.objects.all()),
        filters.ModelFilter(
            "environment element",
            lookup="environments__elements",
            key="envelement",
            queryset=model.Element.objects.all()),
        ]



class RunCaseVersionFilterSet(filters.FilterSet):
    """FilterSet for RunCaseVersions."""
    filters = [
        filters.ChoicesFilter(
            "status",
            lookup="caseversion__status",
            choices=model.CaseVersion.STATUS),
        filters.KeywordExactFilter(
            "id", lookup="caseversion__case__id", coerce=int),
        filters.KeywordFilter("name", lookup="caseversion__name"),
        filters.ModelFilter(
            "tag",
            lookup="caseversion__tags",
            queryset=model.Tag.objects.all()),
        filters.ModelFilter(
            "product",
            lookup="caseversion__case__product",
            queryset=model.Product.objects.all()),
        filters.ModelFilter("run", queryset=model.Run.objects.all()),
        filters.ModelFilter(
            "product version",
            lookup="run__productversion",
            key="productversion",
            queryset=model.ProductVersion.objects.all()),
        filters.KeywordFilter(
            "instruction", lookup="caseversion__steps__instruction"),
        filters.KeywordFilter(
            "expected result",
            lookup="caseversion__steps__expected",
            key="expected"),
        filters.ModelFilter(
            "creator",
            lookup="caseversion__created_by",
            queryset=model.User.objects.all()),
        filters.ModelFilter(
            "environment element",
            lookup="environments__elements",
            key="envelement",
            queryset=model.Element.objects.all()),
        filters.ModelFilter(
            "suite",
            lookup="suites",
            queryset=model.Suite.objects.all()),
        ]



class RunTestsRunCaseVersionFilterSet(filters.FilterSet):
    """FilterSet for RunCaseVersions while running tests."""
    filters = [
        filters.KeywordExactFilter(
            "id", lookup="caseversion__case__id", coerce=int),
        filters.KeywordFilter("name", lookup="caseversion__name"),
        filters.ModelFilter(
            "tag",
            lookup="caseversion__tags",
            queryset=model.Tag.objects.all()),
        filters.KeywordFilter(
            "instruction", lookup="caseversion__steps__instruction"),
        filters.KeywordFilter(
            "expected result",
            lookup="caseversion__steps__expected",
            key="expected"),
        filters.ModelFilter(
            "creator",
            lookup="caseversion__created_by",
            queryset=model.User.objects.all()),
        filters.ModelFilter(
            "suite",
            lookup="suites",
            queryset=model.Suite.objects.all()),
        ]



class ResultFilterSet(filters.FilterSet):
    """FilterSet for results."""
    filters = [
        filters.ChoicesFilter("status", choices=model.Result.STATUS),
        filters.ModelFilter("tester", queryset=model.User.objects.all()),
        filters.KeywordFilter("comment"),
        filters.ModelFilter(
            "environment element",
            lookup="environment__elements",
            key="envelement",
            queryset=model.Element.objects.all()),
        ]



class SuiteFilterSet(filters.FilterSet):
    """FilterSet for suites."""
    filters = [
        filters.ChoicesFilter("status", choices=model.Suite.STATUS),
        filters.ModelFilter("product", queryset=model.Product.objects.all()),
        filters.ModelFilter(
            "run",
            lookup="runs",
            queryset=model.Run.objects.all()
            ),
        filters.KeywordFilter("name"),
        filters.KeywordFilter("description"),
        filters.KeywordExactFilter(
            "case id", lookup="cases__id", key="case", coerce=int),
        filters.ModelFilter(
            "creator", lookup="created_by", queryset=model.User.objects.all()),
        ]



class CaseVersionBoundFilterSet(filters.BoundFilterSet):
    """Filters on ``latest`` if not filtered by ``productversion``."""
    def filter(self, queryset):
        """Add a filter on latest=True if not filtered on productversion."""
        queryset = super(CaseVersionBoundFilterSet, self).filter(queryset)
        pv = [bf for bf in self if bf.key == "productversion"][0]
        if not pv.values:
            queryset = queryset.filter(latest=True)
        return queryset



class CaseVersionFilterSet(filters.FilterSet):
    """FilterSet for CaseVersions."""
    bound_class = CaseVersionBoundFilterSet


    filters = [
        filters.ChoicesFilter("status", choices=model.CaseVersion.STATUS),
        filters.KeywordExactFilter("id", lookup="case__id", coerce=int),
        filters.KeywordFilter("name"),
        filters.ModelFilter(
            "tag", lookup="tags", queryset=model.Tag.objects.all()),
        filters.ModelFilter(
            "product",
            lookup="case__product",
            queryset=model.Product.objects.all()),
        filters.ModelFilter(
            "product version",
            lookup="productversion",
            key="productversion",
            queryset=model.ProductVersion.objects.all()),
        filters.KeywordFilter("instruction", lookup="steps__instruction"),
        filters.KeywordFilter(
            "expected result",
            lookup="steps__expected",
            key="expected"),
        filters.ModelFilter(
            "creator", lookup="created_by", queryset=model.User.objects.all()),
        filters.ModelFilter(
            "environment element",
            lookup="environments__elements",
            key="envelement",
            queryset=model.Element.objects.all()),
        filters.ModelFilter(
            "suite", lookup="case__suites", queryset=model.Suite.objects.all()),
        ]



class TagFilterSet(filters.FilterSet):
    """FilterSet for Tags."""
    filters = [
        filters.KeywordFilter("name"),
        filters.ModelFilter("product", queryset=model.Product.objects.all()),
        filters.ModelFilter(
            "creator", lookup="created_by", queryset=model.User.objects.all()),
        ]



class ProfileFilterSet(filters.FilterSet):
    """FilterSet for environment Profiles."""
    filters = [
        filters.KeywordFilter("name"),
        filters.ModelFilter(
            "environment element",
            lookup="environments__elements",
            key="envelement",
            queryset=model.Element.objects.all()),
        filters.ModelFilter(
            "creator", lookup="created_by", queryset=model.User.objects.all()),
        ]



class EnvironmentFilterSet(filters.FilterSet):
    """FilterSet for Environments."""
    filters = [
        filters.ModelFilter(
            "environment element",
            lookup="elements",
            key="envelement",
            queryset=model.Element.objects.all()),
        ]
