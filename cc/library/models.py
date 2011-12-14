from django.db import models

from ..core.base_model import BaseModel
from ..core.models import Product



class Case(BaseModel):
    product = models.ForeignKey(Product, related_name="cases")


    def __unicode__(self):
        return "case #%s" % (self.id,)



class CaseVersion(BaseModel):
    case = models.ForeignKey(Case, related_name="versions")
    number = models.PositiveIntegerField(unique=True)
    latest = models.BooleanField(default=True, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)


    def __unicode__(self):
        return self.name


    class Meta:
        ordering = ["number"]



class CaseStep(BaseModel):
    caseversion = models.ForeignKey(CaseVersion, related_name="steps")
    number = models.IntegerField(unique=True)
    instruction = models.TextField()
    expected = models.TextField(blank=True)


    def __unicode__(self):
        return u"step #%s" % (self.number,)


    class Meta:
        ordering = ["number"]



class Suite(BaseModel):
    product = models.ForeignKey(Product, related_name="suites")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    cases = models.ManyToManyField(
        Case, through="SuiteCase", related_name="suites")


    def __unicode__(self):
        return self.name



class SuiteCase(BaseModel):
    suite = models.ForeignKey(Suite)
    case = models.ForeignKey(Case)
    order = models.IntegerField(default=0)


    class Meta:
        ordering = ["order"]
