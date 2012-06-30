from tastypie.resources import ALL
from tastypie import fields
from tastypie.resources import ModelResource

from .models import CaseVersion, Case
from ..environments.api import EnvironmentResource
from ..core.api import ProductVersionResource


class CaseResource(ModelResource):

    class Meta:
        queryset = Case.objects.all()
        fields= ["id"]



class CaseVersionResource(ModelResource):

    case = fields.ForeignKey(CaseResource, "case", full=True)
    environments = fields.ToManyField(EnvironmentResource, "environments")
    productversion = fields.ForeignKey(ProductVersionResource, "productversion")


    class Meta:
        queryset = CaseVersion.objects.all()
        list_allowed_methods = ['get']
        fields = ["id", "name", "description", "case"]
        filtering = {
            "environments": ALL,
            "productversion": ALL,
            }



