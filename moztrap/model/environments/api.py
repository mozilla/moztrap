from tastypie import fields
from tastypie.resources import ModelResource, ALL

from .models import Environment, Element, Category



class CategoryResource(ModelResource):
    """Return a list of environment categories."""

    class Meta:
        queryset = Category.objects.all()
        list_allowed_methods = ['get']
        fields = ["id", "name"]


class ElementResource(ModelResource):
    """Return a list of environment elements."""

    category = fields.ForeignKey(CategoryResource, "category", full=True)

    class Meta:
        queryset = Element.objects.all()
        list_allowed_methods = ['get']
        fields = ["id", "name"]



class EnvironmentResource(ModelResource):
    """Return a list of environments"""

    elements = fields.ToManyField(ElementResource, "elements", full=True)

    class Meta:
        queryset = Environment.objects.all()
        list_allowed_methods = ['get']
        fields = ["id"]
        filtering = {"elements": ALL}
