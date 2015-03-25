"""
Forms for test execution.

"""
import json
from django.core.exceptions import ValidationError, ObjectDoesNotExist

import floppyforms.__future__ as forms

from ... import model


class EnvironmentSelectionForm(forms.Form):
    """Form for selecting an environment."""
    def __init__(self, *args, **kwargs):
        """Accepts ``environments`` queryset and ``current`` env id."""
        environments = kwargs.pop("environments", [])
        current = kwargs.pop("current", None)

        super(EnvironmentSelectionForm, self).__init__(*args, **kwargs)

        # list of categories, ordered by name
        self.categories = []

        # maps category to set of elements
        self.elements_by_category = {}

        # maps environment ID to list of element IDs, ordered by category
        self.elementids_by_envid = {}

        # elements in current environment
        current_elements = []

        env_element_through_model = model.Environment.elements.through
        env_element_relationships = env_element_through_model.objects.filter(
            environment__in=environments).select_related()

        # first construct the ordered list of categories (and current elements)
        cat_set = set()
        for ee in env_element_relationships:
            cat_set.add(ee.element.category)
            if ee.environment.id == current:
                current_elements.append(ee.element)
        self.categories = sorted(cat_set, key=lambda c: c.name)

        num_categories = len(self.categories)

        # populate elements by category and environment
        for ee in env_element_relationships:
            byenv = self.elementids_by_envid.setdefault(
                ee.environment.id, [None] * num_categories)
            category_index = self.categories.index(ee.element.category)
            byenv[category_index] = ee.element.id

            bycat = self.elements_by_category.setdefault(
                ee.element.category, set())
            bycat.add(ee.element)

        # construct choice-field for each env type
        for category in self.categories:
            self.fields["category_{0}".format(category.id)] = forms.ChoiceField(
                choices=[("", "---------")] + [
                    (e.id, e.name) for e in sorted(
                        self.elements_by_category[category],
                        key=lambda e: e.name)
                    ],
                label=category.name,
                required=False)

        # set initial data based on current user environment
        for element in current_elements:
            field_name = "category_{0}".format(element.category.id)
            self.initial[field_name] = element.id


    def clean(self):
        """Validate that selected elements form valid environment."""
        # only act on category_ items.  There may be other fields
        # like "build" in here if a run series is being executed.
        selected_element_ids = set(
            [int(eid) for k, eid in self.cleaned_data.iteritems()
                if k.find("category_") == 0 and eid])
        matches = [
            envid for envid, element_ids in self.elementids_by_envid.items()
            if set([e for e in element_ids if e]).issubset(selected_element_ids)
            ]
        if not matches:
            raise forms.ValidationError(
                "The selected environment is not valid for this test run. "
                "Please select a different combination.")

        self.cleaned_data["environment"] = matches[0]

        return self.cleaned_data


    def save(self):
        """Return selected environment ID."""
        return self.cleaned_data["environment"]


    def valid_environments_json(self):
        """Return lists of element IDs representing valid envs, as JSON."""
        return json.dumps(self.elementids_by_envid.values())


class EnvironmentBuildSelectionForm(EnvironmentSelectionForm):
    """
    Form to select your environment and specify a build.

    This is if the user is running a Run that is a series.  If so, then it
    prompts for a build number::

        1. If the clone of this run with that build number already exists,
            Then execute that run with the specified env.
        2. If it does not exist, then clone this run, set the build field
            and execute it with the env specified.

    """
    build = forms.CharField(max_length=200, required=False)
    fields = ["build"]

    def __init__(self, *args, **kwargs):
        self.run = kwargs.pop("run", None)
        self.build = kwargs.pop("build", None)
        self.user = kwargs.pop("user", None)
        super(EnvironmentBuildSelectionForm, self).__init__(*args, **kwargs)


    def clean_build(self):
        """
        Check that the build value is set.
        """
        if not self.cleaned_data["build"]:
            raise ValidationError("You must specify a build to test.")

        return self.cleaned_data["build"]


    def save(self):
        """Find the run with this build, or create a new one."""
        try:
            this_run = model.Run.objects.get(
                series=self.run,
                build=self.cleaned_data["build"],
                )
        except ObjectDoesNotExist:
            this_run = self.run.clone_for_series(
                build=self.cleaned_data["build"],
                user=self.user,
                )
            this_run.activate()
        # now we need to return this new run as the one to be executed.
        return super(EnvironmentBuildSelectionForm, self).save(), this_run.id
