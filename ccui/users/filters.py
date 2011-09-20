from ..core.filters import RelatedFieldFilter

from .models import UserList, Team



class UserFieldFilter(RelatedFieldFilter):
    target = UserList



class TeamFieldFilter(RelatedFieldFilter):
    target = Team
