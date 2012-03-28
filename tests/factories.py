"""
Model factories.

"""
import itertools

from django.core.files.uploadedfile import SimpleUploadedFile

import factory

from cc import model



class EnvironmentsFactoryMixin(object):
    """
    Mixin for Factory subclasses for models with m2m to environments.

    Allows additional ``environments`` kwarg (to ``create`` only, as m2ms can't
    be populated on an unsaved object) with list of environments, or dictionary
    in the format expected by ``EnvironmentFactory.create_full_set``

    """
    @classmethod
    def create(cls, **kwargs):
        envs = kwargs.pop("environments", None)
        obj = super(EnvironmentsFactoryMixin, cls).create(**kwargs)
        if envs is not None:
            if isinstance(envs, dict):
                envs = EnvironmentFactory.create_full_set(envs)
            obj.environments.clear()
            obj.environments.add(*envs)
        return obj



class TeamFactoryMixin(object):
    """
    Mixin for Factory subclasses for models with a team.

    Allows additional ``team`` kwarg (to ``create`` only, as m2ms can't
    be populated on an unsaved object) with list of usernames or users.

    """
    @classmethod
    def create(cls, **kwargs):
        """Create method that allows specifying team."""
        team = kwargs.pop("team", None)
        obj = super(TeamFactoryMixin, cls).create(**kwargs)
        if team is not None:
            users = []
            for user_or_name in team:
                if isinstance(user_or_name, model.User):
                    user = user_or_name
                else:
                    user = UserFactory.create(username=user_or_name)
                users.append(user)
            obj.add_to_team(*users)
        return obj



class UserFactory(factory.Factory):
    FACTORY_FOR = model.User

    username = factory.Sequence(lambda n: "test{0}".format(n))
    email = factory.Sequence(lambda n: "test{0}@example.com".format(n))


    @classmethod
    def create(cls, **kwargs):
        """Create method that allows specifying permissions."""
        permissions = kwargs.pop("permissions", None)
        obj = super(UserFactory, cls).create(**kwargs)
        if permissions is not None:
            perms = []
            for perm_or_name in permissions:
                if isinstance(perm_or_name, model.Permission):
                    perm = perm_or_name
                else:
                    app_label, codename = perm_or_name.split(".", 1)
                    perm = model.Permission.objects.get(
                        content_type__app_label=app_label, codename=codename)
                perms.append(perm)
            obj.user_permissions.add(*perms)
        return obj


    @classmethod
    def _prepare(cls, create, **kwargs):
        """Special handling for ``set_password`` method."""
        password = kwargs.pop("password", None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user



class RoleFactory(factory.Factory):
    FACTORY_FOR = model.Role

    name = factory.Sequence(lambda n: "test{0}".format(n))



class ProductFactory(TeamFactoryMixin, factory.Factory):
    FACTORY_FOR = model.Product

    name = "Test Product"



class ProductVersionFactory(TeamFactoryMixin,
                            EnvironmentsFactoryMixin,
                            factory.Factory):
    FACTORY_FOR = model.ProductVersion

    version = "1.0"
    product = factory.SubFactory(ProductFactory)


    @classmethod
    def create(cls, **kwargs):
        """Handle name kwarg that is concatenated product name / version."""
        name = kwargs.pop("name", None)
        if name:
            if ("version" in kwargs or
                "product" in kwargs or
                "product__name" in kwargs):
                raise ValueError(
                    "Can't provide both name and version/product/product__name")
            else:
                kwargs["product__name"], kwargs["version"] = name.rsplit(" ", 1)
        return super(ProductVersionFactory, cls).create(**kwargs)



class SuiteFactory(factory.Factory):
    FACTORY_FOR = model.Suite

    name = "Test Suite"
    product = factory.SubFactory(ProductFactory)



class CaseFactory(factory.Factory):
    FACTORY_FOR = model.Case

    product = factory.SubFactory(ProductFactory)



class SuiteCaseFactory(factory.Factory):
    FACTORY_FOR = model.SuiteCase

    suite = factory.SubFactory(SuiteFactory)
    case = factory.SubFactory(
        CaseFactory,
        product=factory.LazyContainerAttribute(
            lambda obj, containers: containers[0].suite.product))



class CaseVersionFactory(EnvironmentsFactoryMixin, factory.Factory):
    FACTORY_FOR = model.CaseVersion

    name = "Test Case Version"
    productversion = factory.SubFactory(ProductVersionFactory)
    case = factory.SubFactory(
        CaseFactory,
        product=factory.LazyContainerAttribute(
            lambda obj, containers: containers[0].productversion.product))



class CaseAttachmentFactory(factory.Factory):
    FACTORY_FOR = model.CaseAttachment

    name = "somefile.txt"
    caseversion = factory.SubFactory(CaseVersionFactory)


    @classmethod
    def _prepare(cls, create, **kwargs):
        """Special handling for attachment so we can set name and contents."""
        attachment = kwargs.pop("attachment", None)
        attachment_name = kwargs.get("name", "somefile.txt")
        attachment_content = kwargs.pop("content", "some content")
        if attachment is None:
            attachment = SimpleUploadedFile(attachment_name, attachment_content)
        obj = super(CaseAttachmentFactory, cls)._prepare(create, **kwargs)
        obj.attachment = attachment
        if create:
            obj.save()
        return obj



class CaseStepFactory(factory.Factory):
    FACTORY_FOR = model.CaseStep

    instruction = "Test step instruction"
    caseversion = factory.SubFactory(CaseVersionFactory)


    @factory.lazy_attribute
    def number(obj):
        try:
            return obj.caseversion.steps.order_by("-number")[0].number + 1
        except IndexError:
            return 1



class ProfileFactory(factory.Factory):
    FACTORY_FOR = model.Profile

    name = "Test Profile"



class CategoryFactory(factory.Factory):
    FACTORY_FOR = model.Category

    name = "Test Category"



class ElementFactory(factory.Factory):
    FACTORY_FOR = model.Element

    name = "Test Element"
    category = factory.SubFactory(CategoryFactory)



class EnvironmentFactory(factory.Factory):
    FACTORY_FOR = model.Environment

    profile = factory.SubFactory(ProfileFactory)


    @classmethod
    def create_set(cls, category_names, *envs):
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
        categories = [
            CategoryFactory.create(name=name) for name in category_names]

        environments = []

        for element_names in envs:
            elements = [
                ElementFactory.create(name=name, category=categories[i])
                for i, name in enumerate(element_names)
                ]

            env = cls.create()
            env.elements.add(*elements)

            environments.append(env)

        return environments


    @classmethod
    def create_full_set(cls, categories, profile=None):
        """
        Create all possible environment combinations from given categories.

        Given a dictionary mapping category names to lists of element names in
        that category, create and return list of environments constituting all
        possible combinations of one element from each category.

        """
        element_lists = []

        for category_name, element_names in categories.items():
            category = CategoryFactory.create(name=category_name)
            element_lists.append(
                [
                    ElementFactory.create(category=category, name=element_name)
                    for element_name in element_names
                    ]
                )

        environments = []

        env_kwargs = {}
        if profile:
            env_kwargs["profile"] = profile

        for elements in itertools.product(*element_lists):
            env = cls.create(**env_kwargs)
            env.elements.add(*elements)
            environments.append(env)

        return environments



class RunFactory(TeamFactoryMixin, EnvironmentsFactoryMixin, factory.Factory):
    FACTORY_FOR = model.Run

    name = "Test Run"
    productversion = factory.SubFactory(ProductVersionFactory)



class RunCaseVersionFactory(EnvironmentsFactoryMixin, factory.Factory):
    FACTORY_FOR = model.RunCaseVersion

    run = factory.SubFactory(RunFactory)
    caseversion = factory.SubFactory(
        CaseVersionFactory,
        productversion=factory.LazyContainerAttribute(
            lambda obj, containers: containers[0].run.productversion))



class RunSuiteFactory(factory.Factory):
    FACTORY_FOR = model.RunSuite

    run = factory.SubFactory(RunFactory)
    suite = factory.SubFactory(
        SuiteFactory,
        product=factory.LazyContainerAttribute(
            lambda obj, containers: containers[0].run.productversion.product))



class ResultFactory(factory.Factory):
    FACTORY_FOR = model.Result

    tester = factory.SubFactory(UserFactory)
    runcaseversion = factory.SubFactory(RunCaseVersionFactory)
    environment = factory.SubFactory(EnvironmentFactory)



class StepResultFactory(factory.Factory):
    FACTORY_FOR = model.StepResult

    result = factory.SubFactory(ResultFactory)
    step = factory.SubFactory(CaseStepFactory)



class TagFactory(factory.Factory):
    FACTORY_FOR = model.Tag

    name = "Test Tag"
