"""Sample runs fixture generator."""
from fixture_generator import fixture_generator

from ..core.auth import User
from ..core.models import ProductVersion
from ..library.models import Suite

from .models import Run, RunSuite, RunCaseVersion


@fixture_generator(
    Run, RunSuite, RunCaseVersion, requires=[
        "library.sample_suites", "core.sample_users", "core.sample_products"])
def sample_runs():
    manager = User.objects.get(username="manager")

    accounts = Suite.objects.get(name="Accounts")

    cc8 = ProductVersion.objects.get(product=accounts.product, version="0.8")

    alpha = Run.objects.create(productversion=cc8, name="Alpha 1", user=manager)

    RunSuite.objects.create(run=alpha, suite=accounts)

    alpha.activate(user=manager)
