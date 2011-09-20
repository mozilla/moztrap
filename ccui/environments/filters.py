from ..core.filters import RelatedFieldFilter

from .models import EnvironmentList



class EnvironmentFilter(RelatedFieldFilter):
    target = EnvironmentList
