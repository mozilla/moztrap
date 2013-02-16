"""
Management forms for runs.

"""
import floppyforms as forms

from django.core.exceptions import ValidationError

from moztrap import model
from moztrap.view.lists import filters
from moztrap.view.utils import mtforms




class RunForm(mtforms.NonFieldErrorsClassFormMixin, mtforms.MTModelForm):
    """Base form for adding/editing runs."""
    suites = mtforms.MTMultipleChoiceField(
        required=False,
        widget=mtforms.FilteredSelectMultiple(
            choice_template="manage/run/suite_select/_suite_select_item.html",
            listordering_template=(
                "manage/run/suite_select/_suite_select_listordering.html"),
            filters=[
                filters.KeywordFilter("name"),
                filters.ModelFilter(
                    "author", queryset=model.User.objects.all()),
                ],
            )
        )
    productversion = mtforms.MTModelChoiceField(
        queryset=model.ProductVersion.objects.all(),
        choice_attrs=mtforms.product_id_attrs,
        )
    build = forms.CharField(max_length=200, required=False)
    is_series = forms.BooleanField(required=False)


    class Meta:
        model = model.Run
        fields = [
            "productversion",
            "name",
            "description",
            "is_series",
            "build",
            "start",
            "end",
            "is_series",
            ]
        widgets = {
            "name": forms.TextInput,
            "description": mtforms.BareTextarea,
            "build": forms.TextInput,
            "is_series": forms.CheckboxInput,
            "start": forms.DateInput,
            "end": forms.DateInput,
            }


    def clean_suites(self):
        """
        Make sure all the ids for the suites are valid and populate
        self.cleaned_data with the real objects.

        If these are not ids, then they are read-only strings of the title
        and therefore don't need to be validated.  So first verify they're
        all ints.
        """

        try:
            suites = dict((unicode(x.id), x) for x in
                model.Suite.objects.filter(pk__in=self.cleaned_data["suites"]))
            try:
                return [suites[x] for x in self.cleaned_data["suites"]]

            except KeyError as e:
                raise ValidationError("Not a valid suite for this run.")

        except ValueError:
            # some of the values weren't ints, and therefore this is
            # from the read-only list of suites.  so return None so that we
            # don't try to remove and re-add them.
            if "suites" in self.changed_data:  # pragma: no cover
                self.changed_data.remove("suites")
            return None


    def clean_build(self):
        """If this is a series, then null out the build field."""
        if self.cleaned_data["is_series"]:
            return None


    def save(self, user=None):
        """Save and return run, with suite associations."""
        user = user or self.user
        run = super(RunForm, self).save(user=user)

        if "suites" in self.changed_data:
            # if this is empty, then don't make any changes, because
            # either there are no suites, or this came from the read
            # only suite list.
            run.runsuites.all().delete(permanent=True)
            for i, suite in enumerate(self.cleaned_data["suites"]):
                model.RunSuite.objects.create(
                    run=run, suite=suite, order=i, user=user)

        return run



class AddRunForm(RunForm):
    """Form for adding a run."""
    def __init__(self, *args, **kwargs):
        """Initialize AddRunForm; default to being a series."""
        super(AddRunForm, self).__init__(*args, **kwargs)

        isf = self.fields["is_series"]
        isf.initial = True



class EditRunForm(RunForm):
    """Form for editing a run."""
    def __init__(self, *args, **kwargs):
        """Initialize EditRunForm; no changing product version of active run."""
        super(EditRunForm, self).__init__(*args, **kwargs)

        pvf = self.fields["productversion"]
        sf = self.fields["suites"]
        isf = self.fields["is_series"]
        self.initial["suites"] = list(
            self.instance.suites.values_list(
                "name", flat=True).order_by("runsuites__order"))
        if self.instance.status == model.Run.STATUS.active:
            # can't change the product version of an active run.
            pvf.queryset = pvf.queryset.filter(
                pk=self.instance.productversion_id)
            pvf.readonly = True
            # can't change being a series in an active run
            isf.readonly = True
            # can't change suites of an active run either
            sf.readonly = True
#            self.initial["suites"] = list(
#                self.instance.suites.values_list(
#                    "name", flat=True).order_by("runsuites__order"))
        else:
            # regardless, can't switch to different product entirely
            pvf.queryset = pvf.queryset.filter(
                product=self.instance.productversion.product_id)

            # ajax populates available and included suites on page load
