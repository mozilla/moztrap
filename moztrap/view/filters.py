"""
List filtering options.

"""
from model_utils import Choices
from moztrap import model

from .lists import filters
from .lists import cases



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
            "productversion",
            queryset=model.ProductVersion.objects.all().select_related()),
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
        filters.ChoicesFilter(
            "is Series",
            lookup="is_series",
            key="is_series",
            choices=[(1, "series"), (0, "individual")],
            coerce=int,
            ),
        filters.ModelFilter(
            "members of series",
            lookup="series",
            queryset=model.Run.objects.filter(is_series=True)
            ),
        filters.KeywordExactFilter("build"),
        ]



class RunCaseVersionFilterSet(filters.FilterSet):
    """FilterSet for RunCaseVersions."""
    filters = [
        filters.ChoicesFilter(
            "status",
            lookup="caseversion__status",
            choices=model.CaseVersion.STATUS),
        filters.ChoicesFilter(
            "result status",
            key="resultstatus",
            lookup="results__status",
            extra_filters={"results__is_latest": True},
            choices=Choices(*model.Result.COMPLETED_STATES),
            ),
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
            lookup="caseversion__case__suites",
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
            lookup="caseversion__case__suites",
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
            "product version",
            lookup="product__versions",
            key="productversion",
            queryset=model.ProductVersion.objects.all(),
            ),
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



class CaseVersionFilterSet(filters.FilterSet):
    """FilterSet for CaseVersions."""

    filters = [
        filters.ChoicesFilter("status", choices=model.CaseVersion.STATUS),
        cases.PrefixIDFilter("id"),
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
            queryset=model.ProductVersion.objects.all().select_related()),
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
            "product version",
            lookup="product__versions",
            key="productversion",
            queryset=model.ProductVersion.objects.all(),
            ),
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
