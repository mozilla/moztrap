from tastypie.resources import ModelResource
from .models import Run, RunCaseVersion, Result
from ..library.models import CaseVersion
from tastypie import fields


class CaseVersionResource(ModelResource):

    class Meta:
        queryset = CaseVersion.objects.all()
        fields = ["id", "name", "description", "resource_uri"]



class ResultResource(ModelResource):

    class Meta:
        queryset = Result.objects.all()



class RunCaseVersionResource(ModelResource):
    caseversion = fields.ForeignKey(
        CaseVersionResource,
        'caseversion',
        full=True,
    )
    result = fields.ToManyField(
        ResultResource,
        'results',
        full=True,
    )

    class Meta:
        queryset = RunCaseVersion.objects.all()
        fields = ["id", "order", "resource_uri"]



class RunResource(ModelResource):
    caseversions = fields.ToManyField(
        RunCaseVersionResource,
        'runcaseversions',
        )

    class Meta:
        queryset = Run.objects.all()
        fields = ["id", "name", "description", "resource_uri"]



class RunCasesDetailResource(ModelResource):
    caseversions = fields.ToManyField(
        RunCaseVersionResource,
        'runcaseversions',
        full=True,
        )

    class Meta:
        queryset = Run.objects.all()
        fields = ["id", "name", "description", "resource_uri"]
