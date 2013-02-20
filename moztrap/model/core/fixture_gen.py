"""Sample products fixture generator."""
from django.core.management import call_command

from django.contrib.auth.models import User as BaseUser, Group

from .auth import User, Role

from fixture_generator import fixture_generator

from ..environments.models import Profile

from .models import Product, ProductVersion


@fixture_generator(
    Product, ProductVersion, requires=[
        "environments.sample_environments", "core.sample_users"])
def sample_products():
    admin = User.objects.get(username="admin")

    browserenvs = Profile.objects.get(name="Browser Testing Environments")

    ff = Product.objects.create(name="Firefox", user=admin)
    ff9 = ProductVersion.objects.create(version="9", product=ff, user=admin)
    ff9.environments.add(*browserenvs.environments.all())
    ff10 = ProductVersion.objects.create(version="10", product=ff, user=admin)
    ff10.environments.add(*browserenvs.environments.all())

    webenvs = Profile.objects.get(name="Website Testing Environments")

    cc = Product.objects.create(name="MozTrap", user=admin)
    cc6 = ProductVersion.objects.create(version="0.6", product=cc, user=admin)
    cc6.environments.add(*webenvs.environments.all())
    cc7 = ProductVersion.objects.create(version="0.7", product=cc, user=admin)
    cc7.environments.add(*webenvs.environments.all())
    cc8 = ProductVersion.objects.create(
        version="0.8", product=cc, codename="Django DB", user=admin)
    cc8.environments.add(*webenvs.environments.all())


# have to pass fixture-generator the real concrete models
@fixture_generator(Group, BaseUser)
def sample_users():
    call_command("create_default_roles", verbosity=0)

    tester_role = Role.objects.get(name="Tester")
    creator_role = Role.objects.get(name="Test Creator")
    manager_role = Role.objects.get(name="Test Manager")
    admin_role = Role.objects.get(name="Admin")

    # create and delete one user so we avoid using id=1 in the fixture; would
    # overwrite the default superuser that may have been created on syncdb.
    User.objects.create(username="delete")
    User._base_manager.all().delete()

    tester = User(username="tester", email="tester@example.com")
    creator = User(username="creator", email="creator@example.com")
    manager = User(username="manager", email="manager@example.com")
    admin = User(username="admin", email="admin@example.com")

    for user in [tester, creator, manager, admin]:
        user.set_password("testpw")
        user.save()

    tester.roles.add(tester_role)
    creator.roles.add(creator_role)
    manager.roles.add(manager_role)
    admin.roles.add(admin_role)
