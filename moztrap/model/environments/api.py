from tastypie import fields
from tastypie.resources import ModelResource, ALL
from ..mtapi import MTResource, MTAuthorization

from .models import Profile, Environment, Element, Category



class EnvironmentAuthorization(MTAuthorization):
    """Atypically named permission."""

    @property
    def permission(self):
        """This permission should be checked by is_authorized."""
        return "environments.manage_environments"



class ProfileResource(MTResource):
    """Create, Read, Update, and Delete capabilities for Profile."""

    class Meta(MTResource.Meta):
        queryset = Profile.objects.all()
        fields = ["id", "name", "categories"]
        authorization = EnvironmentAuthorization()
        ordering = ["id", "name"]

    @property
    def model(self):
        """Model class related to this resource."""
        return Profile



class CategoryResource(MTResource):
    """Create, Read, Update and Delete capabilities for Category."""

    elements = fields.ToManyField(
        "moztrap.model.environments.api.ElementResource",
        "elements",
        full=True,
        readonly=True
    )

    class Meta(MTResource.Meta):
        queryset = Category.objects.all()
        fields = ["id", "name"]
        authorization = EnvironmentAuthorization()
        ordering = ["id", "name"]

    @property
    def model(self):
        """Model class related to this resource."""
        return Category



class ElementResource(MTResource):
    """Create, Read, Update and Delete capabilities for Element."""

    category = fields.ForeignKey(CategoryResource, "category")

    class Meta(MTResource.Meta):
        queryset = Element.objects.all()
        fields = ["id", "name", "category"]
        authorization = EnvironmentAuthorization()
        filtering = {
            "category": ALL,
        }
        ordering = ["id", "name"]


    @property
    def model(self):
        """Model class related to this resource."""
        return Element

    @property
    def read_create_fields(self):
        """List of fields that are required for create but read-only for update."""
        return ["category"]



class EnvironmentResource(ModelResource):
    """Return a list of environments"""

    elements = fields.ToManyField(ElementResource, "elements", full=True)

    class Meta:
        queryset = Environment.objects.all()
        list_allowed_methods = ['get']
        fields = ["id"]
        filtering = {"elements": ALL}
