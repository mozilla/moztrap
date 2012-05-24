"""
Finder for management pages.

"""
from ... import model
from ..lists import finder



class ManageFinder(finder.Finder):
    template_base = "manage/finder"

    columns = [
        finder.Column(
            "products",
            "_products.html",
            model.Product.objects.order_by("name"),
            "manage_productversions",
            ),
        finder.Column(
            "productversions",
            "_productversions.html",
            model.ProductVersion.objects.all(),
            "manage_runs",
            ),
        finder.Column(
            "runs",
            "_runs.html",
            model.Run.objects.order_by("start"),
            "manage_suites",
            ),
        finder.Column(
            "suites",
            "_suites.html",
            model.Suite.objects.order_by("name"),
            "manage_cases",
            ),
        ]
