"""
All models.

"""
from django.db.models import ProtectedError, signals
from django.dispatch import receiver

from registration.models import RegistrationProfile

from .mtmodel import ConcurrencyError
from .core.models import MTModel, Product, ProductVersion, ApiKey
from .core.auth import User, Role, Permission
from .environments.models import Environment, Profile, Element, Category
from .execution.models import Run, RunSuite, RunCaseVersion, Result, StepResult
from .library.bulk import BulkParser
from .library.models import (
    Case, CaseVersion, CaseAttachment, CaseStep, Suite, SuiteCase)
from .tags.models import Tag

# version of the REST endpoint APIs for TastyPie
API_VERSION = "v1"


@receiver(signals.post_save, sender=Tag)
@receiver(signals.post_save, sender=User)
@receiver(signals.post_save, sender=Role)
@receiver(signals.post_save, sender=Element)
@receiver(signals.post_save, sender=Suite)
@receiver(signals.post_save, sender=Run)
@receiver(signals.post_save, sender=Product)
@receiver(signals.post_save, sender=ProductVersion)
def invalidate_model_choices(sender, instance, **kwargs):
    """This makes sure that the model choices for forms related to these
    are invalidated when changes are made.

    The place where the caching is set is in
    moztrap.view.lists.filters.ModelFilter
    """
    MTModel.delete_modelfilter_choices_cache(sender)
