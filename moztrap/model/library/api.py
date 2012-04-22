from tastypie import fields
from tastypie.resources import ModelResource

from .models import CaseVersion


class CaseVersionResource(ModelResource):

    class Meta:
        queryset = CaseVersion.objects.all()
        fields = ["id", "name", "description", "resource_uri"]
