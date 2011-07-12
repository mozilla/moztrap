from django.forms.formsets import formset_factory, BaseFormSet

import floppyforms as forms

from ..core import forms as tcmforms
from ..core.util import id_for_object

from .models import EnvironmentGroupList
from .util import environments_of

class EnvironmentSelectionForm(tcmforms.NonFieldErrorsClassFormMixin,
                               forms.Form):
    """
    A form for selecting an environment group from a set of possible
    environment groups, in the form of a dropdown for each environment type
    present in the groups.

    Validates that the selected combination (one value per environment type)
    actually matches one of the possible groups.

    """
    def __init__(self, *args, **kwargs):
        groups = kwargs.pop("groups")
        # should be a list of (envtypeid, envid) tuples
        current = kwargs.pop("current", None)

        super(EnvironmentSelectionForm, self).__init__(*args, **kwargs)

        # maps (envtype.id, envtype.name) to list of env options for that type
        # e.g. (1, "Operating System") => [(5, "Windows"), (6, "Linux")]
        self.types = {}

        # list of sets of env ids, each one representing a group
        self.groups = []

        for group in groups:
            env_ids = set()
            for env in group.environments:
                env_ids.add(env.id)
                et = env.environmentType
                options = self.types.setdefault((et.id, et.name), set())
                options.add((id_for_object(env), env.name))
            self.groups.append(env_ids)

        # construct choice-field for each env type
        for (typeid, typename), options in sorted(
            self.types.items(), key=lambda x: x[0][1]):
            self.fields["type_%s" % typeid] = forms.ChoiceField(
                choices=sorted(options, key=lambda x: x[1]),
                label=typename)

        # set initial data based on current user environments
        if current:
            for (envtypeid, envid) in current:
                field_name = "type_%s" % envtypeid
                if field_name in self.fields:
                    self.initial[field_name] = envid


    def clean(self):
        """
        Check that the set of selected environments fit together into a valid
        environment group (all combinations should be valid if autogenerate was
        used, but this isn't guaranteed).

        """
        env_ids = set([eid for eid in self.cleaned_data.itervalues()])
        match = None
        for group in self.groups:
            if env_ids.issubset(group):
                match = group
                break
        if not match:
            raise forms.ValidationError(
                "The selected environment combination is not valid for this "
                "product, test cycle, or test run. Please select a different "
                "combination, or ask the system administrator to add this one.")

        return self.cleaned_data


    def save(self):
        return [(int(field_name[len("type_"):]), eid) for field_name, eid
                in self.cleaned_data.iteritems()]
