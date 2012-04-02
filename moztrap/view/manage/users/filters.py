"""
Filtering for users.

"""
from cc import model
from cc.view.lists import filters



class UserFilterSet(filters.FilterSet):
    """FilterSet for Users."""
    filters = [
        filters.ChoicesFilter(
            "active",
            lookup="is_active",
            choices=[(1, "active"), (0, "disabled")],
            coerce=int,
            ),
        filters.KeywordFilter("username"),
        filters.KeywordFilter("email"),
        filters.ModelFilter(
            "role", lookup="groups", queryset=model.Role.objects.all())
        ]
