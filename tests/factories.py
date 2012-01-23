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
Model factories.

"""
import itertools

from django.core.files.uploadedfile import SimpleUploadedFile

from django.contrib.auth.models import User, Permission

import factory

from cc.core import models as core_models
from cc.environments import models as environment_models
from cc.execution import models as execution_models
from cc.library import models as library_models
from cc.tags import models as tag_models



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
                if isinstance(user_or_name, User):
                    user = user_or_name
                else:
                    user = UserFactory.create(username=user_or_name)
                users.append(user)
            obj.add_to_team(*users)
        return obj



class UserFactory(factory.Factory):
    FACTORY_FOR = User

    username = factory.Sequence(lambda n: "test{0}".format(n))


    @classmethod
    def create(cls, **kwargs):
        """Create method that allows specifying permissions."""
        permissions = kwargs.pop("permissions", None)
        obj = super(UserFactory, cls).create(**kwargs)
        if permissions is not None:
            perms = []
            for perm_or_name in permissions:
                if isinstance(perm_or_name, Permission):
                    perm = perm_or_name
                else:
                    app_label, codename = perm_or_name.split(".", 1)
                    perm = Permission.objects.get(
                        content_type__app_label=app_label, codename=codename)
                perms.append(perm)
            obj.user_permissions.add(*perms)
        return obj


    @classmethod
    def _prepare(cls, create, **kwargs):
        """Special handling for ``set_password`` method."""
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.set_password(password)
            if create:
                user.save()
        return user



class ProductFactory(TeamFactoryMixin, factory.Factory):
    FACTORY_FOR = core_models.Product

    name = "Test Product"



class ProductVersionFactory(TeamFactoryMixin,
                            EnvironmentsFactoryMixin,
                            factory.Factory):
    FACTORY_FOR = core_models.ProductVersion

    version = "1.0"
    product = factory.SubFactory(ProductFactory)



class SuiteFactory(factory.Factory):
    FACTORY_FOR = library_models.Suite

    name = "Test Suite"
    product = factory.SubFactory(ProductFactory)



class CaseFactory(factory.Factory):
    FACTORY_FOR = library_models.Case

    product = factory.SubFactory(ProductFactory)



class SuiteCaseFactory(factory.Factory):
    FACTORY_FOR = library_models.SuiteCase

    suite = factory.SubFactory(SuiteFactory)
    case = factory.SubFactory(
        CaseFactory,
        product=factory.LazyContainerAttribute(
            lambda obj, containers: containers[0].suite.product))



class CaseVersionFactory(EnvironmentsFactoryMixin, factory.Factory):
    FACTORY_FOR = library_models.CaseVersion

    name = "Test Case Version"
    productversion = factory.SubFactory(ProductVersionFactory)
    case = factory.SubFactory(
        CaseFactory,
        product=factory.LazyContainerAttribute(
            lambda obj, containers: containers[0].productversion.product))



class CaseAttachmentFactory(factory.Factory):
    FACTORY_FOR = library_models.CaseAttachment

    caseversion = factory.SubFactory(CaseVersionFactory)


    @classmethod
    def _prepare(cls, create, **kwargs):
        """Special handling for attachment so we can set name and contents."""
        attachment = kwargs.pop("attachment", None)
        attachment_name = kwargs.pop("attachment__name", "somefile.txt")
        attachment_content = kwargs.pop("attachment__content", "some content")
        if attachment is None:
            attachment = SimpleUploadedFile(attachment_name, attachment_content)
        obj = super(CaseAttachmentFactory, cls)._prepare(create, **kwargs)
        obj.attachment = attachment
        if create:
            obj.save()
        return obj



class CaseStepFactory(factory.Factory):
    FACTORY_FOR = library_models.CaseStep

    instruction = "Test step instruction"
    caseversion = factory.SubFactory(CaseVersionFactory)


    @factory.lazy_attribute
    def number(obj):
        try:
            return obj.caseversion.steps.order_by("-number")[0].number + 1
        except IndexError:
            return 1



class ProfileFactory(factory.Factory):
    FACTORY_FOR = environment_models.Profile

    name = "Test Profile"



class CategoryFactory(factory.Factory):
    FACTORY_FOR = environment_models.Category

    name = "Test Category"



class ElementFactory(factory.Factory):
    FACTORY_FOR = environment_models.Element

    name = "Test Element"
    category = factory.SubFactory(CategoryFactory)



class EnvironmentFactory(factory.Factory):
    FACTORY_FOR = environment_models.Environment

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
    def create_full_set(cls, categories):
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

        for elements in itertools.product(*element_lists):
            env = cls.create()
            env.elements.add(*elements)
            environments.append(env)

        return environments



class RunFactory(TeamFactoryMixin, EnvironmentsFactoryMixin, factory.Factory):
    FACTORY_FOR = execution_models.Run

    name = "Test Run"
    productversion = factory.SubFactory(ProductVersionFactory)



class RunCaseVersionFactory(EnvironmentsFactoryMixin, factory.Factory):
    FACTORY_FOR = execution_models.RunCaseVersion

    run = factory.SubFactory(RunFactory)
    caseversion = factory.SubFactory(
        CaseVersionFactory,
        productversion=factory.LazyContainerAttribute(
            lambda obj, containers: containers[0].run.productversion))



class RunSuiteFactory(factory.Factory):
    FACTORY_FOR = execution_models.RunSuite

    run = factory.SubFactory(RunFactory)
    suite = factory.SubFactory(
        SuiteFactory,
        product=factory.LazyContainerAttribute(
            lambda obj, containers: containers[0].run.productversion.product))



class ResultFactory(factory.Factory):
    FACTORY_FOR = execution_models.Result

    tester = factory.SubFactory(UserFactory)
    runcaseversion = factory.SubFactory(RunCaseVersionFactory)
    environment = factory.SubFactory(EnvironmentFactory)



class StepResultFactory(factory.Factory):
    FACTORY_FOR = execution_models.StepResult

    result = factory.SubFactory(ResultFactory)
    step = factory.SubFactory(CaseStepFactory)



class TagFactory(factory.Factory):
    FACTORY_FOR = tag_models.Tag

    name = "Test Tag"
