from tastypie import fields
from tastypie.resources import ModelResource

from .models import Environment


class EnvironmentResource(ModelResource):

    class Meta:
        queryset = Environment.objects.all()
        #fields = ["id", "name", "description", "resource_uri"]
