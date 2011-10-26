# Case Conductor is a Test Case Management system.
# Copyright (C) 2011 uTest Inc.
# 
# This file is part of Case Conductor.
# 
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage

import floppyforms as forms

from ..attachments.models import Attachment
from ..core import forms as ccforms
from ..core.auth import admin
from ..core.filters import KeywordFilter
from ..products.models import Product, ProductList
from ..static.filters import TestCaseStatusFilter
from ..static.status import AttachmentType
from ..tags.models import Tag, TagList
from ..testcases import increment
from ..testcases.bulk import BulkParser
from ..testcases.forms import StepFormSet
from ..testcases.models import (
    TestSuite, TestSuiteList, TestCaseVersion, TestCaseList, TestCaseStep)
from ..testexecution.models import (
    TestCycle, TestCycleList, TestRun, TestRunList)
from ..users.filters import UserFieldFilter
from ..users.models import User, UserList



def product_id_attrs(obj):
    return {"data-product-id": obj.product.id}



class UserForm(ccforms.AddEditForm):
    screenName = forms.CharField(label="screen name")
    firstName = forms.CharField(label="first name")
    lastName = forms.CharField(label="last name")
    email = forms.CharField(label="email")
    roles = ccforms.ModelMultipleChoiceField(required=False)
    password = forms.CharField(label="password", widget=forms.PasswordInput)


    no_edit_fields = ["screenName"]
    assign_later = ["roles"]
    entryclass = User
    listclass = UserList


    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company")
        super(UserForm, self).__init__(*args, **kwargs)
        if self.instance is not None:
            fld = self.fields["password"]
            fld.required = False
            fld.widget.is_required = False
            fld.label = "new password"


    @property
    def extra_creation_data(self):
        return {"company": self.company}


    def edit_clean(self):
        ret = super(UserForm, self).edit_clean()

        # Password and email require special handling
        if self.cleaned_data["email"] != self.instance.email:
            try:
                self.instance.emailchange(self.cleaned_data["email"])
            except self.instance.Conflict, e:
                self.handle_error(self.instance, e)
        if self.cleaned_data["password"]:
            try:
                self.instance.passwordchange(self.cleaned_data["password"])
            except self.instance.Conflict, e:
                self.handle_error(self.instance, e)

        return ret



class ProductForm(ccforms.AddEditForm):
    name = forms.CharField()
    description = forms.CharField(widget=ccforms.BareTextarea)
    team = ccforms.ModelMultipleChoiceField(required=False)


    assign_later = ["team", "profile"]
    entryclass = Product
    listclass = ProductList


    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop("company")
        super(ProductForm, self).__init__(*args, **kwargs)


    def add_fields(self):
        if self.instance is None:
            self.fields["profile"] = ccforms.ModelChoiceField()



    @property
    def extra_creation_data(self):
        return {"company": self.company}



class TestCycleForm(ccforms.AddEditForm):
    name = forms.CharField()
    description = forms.CharField(widget=ccforms.BareTextarea)
    product = ccforms.ModelChoiceField()
    start_date = forms.DateField()
    end_date = forms.DateField(required=False)
    team = ccforms.ModelMultipleChoiceField(required=False)


    no_edit_fields = ["product"]
    field_mapping = {
        "start_date": "startDate",
        "end_date": "endDate"}
    assign_later = ["team"]
    entryclass = TestCycle
    listclass = TestCycleList
    extra_creation_data = {
        "communityAccessAllowed": True,
        "communityAuthoringAllowed": True,
        }



class TestRunForm(ccforms.AddEditForm):
    name = forms.CharField()
    description = forms.CharField(widget=ccforms.BareTextarea)
    test_cycle = ccforms.ModelChoiceField(
        option_attrs=product_id_attrs)
    start_date = forms.DateField()
    end_date = forms.DateField(required=False)
    team = ccforms.ModelMultipleChoiceField(required=False)
    suites = ccforms.ModelMultipleChoiceField(
        required=False, option_attrs=product_id_attrs)


    no_edit_fields = ["test_cycle"]
    field_mapping = {
        "test_cycle": "testCycle",
        "start_date": "startDate",
        "end_date": "endDate"}
    assign_later = ["team", "suites"]
    entryclass = TestRun
    listclass = TestRunList
    extra_creation_data = {
        "selfAssignLimit": 0,
        "selfAssignAllowed": True,
        }



class TestSuiteForm(ccforms.AddEditForm):
    name = forms.CharField()
    description = forms.CharField(widget=ccforms.BareTextarea)
    product = ccforms.ModelChoiceField(
        option_attrs=lambda p: {"data-product-id": p.id})
    cases = ccforms.ModelMultipleChoiceField(
        required=False,
        label_from_instance=lambda c: c.name,
        option_attrs=product_id_attrs)


    def __init__(self, *args, **kwargs):
        super(TestSuiteForm, self).__init__(*args, **kwargs)
        self.fields["cases"].widget = ccforms.FilteredSelectMultiple(
            auth=self.auth,
            filters=[
                ("status", TestCaseStatusFilter),
                ("name", KeywordFilter),
                ("author", UserFieldFilter)
                ])


    no_edit_fields = ["product"]
    assign_later = ["cases"]
    entryclass = TestSuite
    listclass = TestSuiteList



class BulkTestCaseForm(ccforms.RemoteObjectForm):
    product = ccforms.ModelChoiceField()
    cases = forms.CharField(widget=ccforms.BareTextarea)


    def __init__(self, *args, **kwargs):
        product_choices = kwargs.pop("product_choices")
        self.company = kwargs.pop("company")

        self.auth = kwargs.pop("auth")

        super(BulkTestCaseForm, self).__init__(*args, **kwargs)

        self.fields["product"].obj_list = product_choices


    def clean_cases(self):
        parser = BulkParser()
        data = parser.parse(self.cleaned_data["cases"])

        for d in data:
            if "error" in d:
                raise ValidationError(d["error"])

        return data


    def clean(self):
        cases = []
        tcl = TestCaseList.get(auth=self.auth)

        tag_ids = self.data.getlist("tag")
        new_tags = self.data.getlist("newtag")

        tl = TagList.get(auth=self.auth)
        for name in new_tags:
            t = Tag(name=name, company=self.company)
            tl.post(t)
            tag_ids.append(t.id)

        for d in self.cleaned_data.get("cases", []):
            tcdata = dict(
                TestCaseForm.extra_creation_data,
                product=self.cleaned_data["product"],
                name=d["name"],
                description="\r\n".join(d["description"]),
                )

            tcv = TestCaseVersion(**tcdata)
            try:
                tcl.post(tcv)
            except TestCaseList.Conflict, e:
                for case in cases:
                    TestCaseList.get_by_id(
                        case.testCaseId, auth=self.auth).delete()
                self.handle_error(tcv, e)
                break

            cases.append(tcv)

            for i, stepdata in enumerate(d["steps"]):
                step = TestCaseStep(
                    stepNumber=i+1,
                    instruction="\n".join(stepdata["instruction"]),
                    expectedResult="\n".join(stepdata["expectedResult"]),
                    name="step %s" % str(i + 1),
                    testCaseVersion=tcv,
                    estimatedTimeInMin=0,
                    )

                tcv.steps.post(step)

            tcv.approve(auth=admin)

            tcv.tags = tag_ids

        self.cases = cases

        return self.cleaned_data


    def save(self):
        return self.cases



def no_name_just_version(tcv):
        return u"v%s (%s)" % (
            tcv.majorVersion,
            tcv.latestVersion and "latest" or "obsolete",
            )



class TestCaseForm(ccforms.AddEditForm):
    name = forms.CharField()
    description = forms.CharField()
    product = ccforms.ModelChoiceField()


    no_edit_fields = ["product"]
    entryclass = TestCaseVersion
    listclass = TestCaseList
    extra_creation_data = {
        # @@@ these attachment-related attributes are non-functional
        "maxAttachmentSizeInMbytes": 0,
        "maxNumberOfAttachments": 0,
        "automationUri": "",
        }


    def add_fields(self):
        if self.instance is not None:
            self.fields["version"] = ccforms.ModelChoiceField(
                initial=self.instance.id,
                label_from_instance=no_name_just_version)
            self.fields["version"].obj_list = TestCaseList.get_by_id(
                self.instance.testCaseId, auth=self.instance.auth).versions

            self.fields["increment"] = forms.ChoiceField(
                choices=[
                    ("major", "save as new version"),
                    ("inplace", "save in place"),
                    ]
                )



    def create_formsets(self, *args, **kwargs):
        self.steps_formset = StepFormSet(
            *args, **dict(kwargs, prefix="steps"))

        super(TestCaseForm, self).create_formsets(*args, **kwargs)


    def is_valid(self):
        if self.steps_formset.is_valid():
            self.steps_formset_clear = True
            return super(TestCaseForm, self).is_valid()
        return False


    def _save_tags(self):
        # @@@ convert into proper form field with widget?
        tag_ids = self.data.getlist("tag")
        new_tags = self.data.getlist("newtag")

        tl = TagList.get(auth=self.auth)
        for name in new_tags:
            t = Tag(name=name, company=self.instance.company)
            tl.post(t)
            tag_ids.append(t.id)

        self.instance.tags = tag_ids


    def _save_attachments(self):
        # @@@ convert into proper form field with widget?
        delete_ids = set(self.data.getlist("remove-attachment"))
        for attachment in self.instance.attachments:
            if attachment.id in delete_ids:
                attachment.delete()

        # if we're saving as new version, bring forward existing attachments
        # from previous version
        prior_version = getattr(self, "prior_version", None)
        if prior_version is not None:
            for attachment in prior_version.attachments:
                self.instance.attachments.post(attachment)

        if not self.files:
            return
        for uf in self.files.getlist("attachment"):
            try:
                file_name = uf.name
                file_size = uf.size
            except AttributeError:
                continue

            if not file_name or not file_size:
                continue

            storage_name = default_storage.get_available_name(
                default_storage.get_valid_name(file_name))

            default_storage.save(storage_name, uf)

            attachment = Attachment(
                name=storage_name,
                description=file_name,
                url=default_storage.url(storage_name),
                size=file_size,
                attachmentType=AttachmentType.UNSPECIFIED
                )

            self.instance.attachments.post(attachment)


    def clean(self):
        # If the formset is not valid, we don't want to actually try saving the
        # testcase.
        if self.errors or not getattr(self, "steps_formset_clear", False):
            return self.cleaned_data
        ret = super(TestCaseForm, self).clean()

        self._save_tags()
        self._save_attachments()

        return ret


    def edit_clean(self):
        for k, v in self.prep_form_data(
            self.cleaned_data, editing=True).iteritems():
            setattr(self.instance, k, v)
        incr = self.cleaned_data["increment"]
        try:
            if incr == "minor":
                self.prior_version = self.instance.refresh()
                self.instance.versionincrement(increment.MINOR)
                self.instance.approve(auth=admin)
            elif incr == "major":
                self.prior_version = self.instance.refresh()
                self.instance.versionincrement(increment.MAJOR)
                self.instance.approve(auth=admin)
            else:
                self.instance.put()
        except self.instance.Conflict, e:
            self.handle_error(self.instance, e)

        # Name field can't be edited via TestCaseVersion, so we do it via the
        # TestCase proper
        if self.cleaned_data["name"] != self.instance.name:
            tc = self.instance.testCase
            tc.name = self.instance.name = self.cleaned_data["name"]
            try:
                tc.put()
            except self.instance.Conflict, e:
                self.handle_error(self.instance, e)

        return self.cleaned_data



    def save(self):
        self.steps_formset.save(self.instance)

        instance = super(TestCaseForm, self).save()

        instance.approve(auth=admin)

        return instance

