from django.forms.formsets import formset_factory, BaseFormSet

import floppyforms as forms

from ..core import forms as tcmforms
from ..core.util import id_for_object

from .models import EnvironmentGroupList
from .util import environments_of

class EnvironmentSelectionForm(forms.Form):
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



class EnvironmentConstraintForm(forms.Form):
    """
    Form for selecting multiple options for a single environment type, given a
    set of environment groups.

    """
    env_type = forms.ChoiceField(choices=[])
    environments = forms.MultipleChoiceField(choices=[], required=False)


    def __init__(self, *args, **kwargs):
        # If filtered is set to False, will not filter
        filtered = kwargs.pop("filtered", True)
        # map of (et.id, et.name) to set of (env.id, env.name)
        environments = kwargs.pop("environments")

        super(EnvironmentConstraintForm, self).__init__(*args, **kwargs)

        # contains (envtype.id, envtype.name) tuples
        types = set(environments.iterkeys())
        # contains ((envtype.id, env.id), env.name) tuples
        choices = set()
        for (etid, etname), envs in environments.iteritems():
            for (envid, envname) in envs:
                choices.add(((etid, envid), envname))

        k = lambda x: x[1]

        self.fields["env_type"].choices = sorted(types, key=k)
        self.fields["env_type"].widget.attrs["class"] = "env_type"

        # Filter the list of choices to only those relevant to the
        # selected environment type.
        if filtered:
            etid = self.data.get(
                self.add_prefix("env_type"),
                self.initial.get(
                    "env_type",
                    self.fields["env_type"].choices[0][0]))
            if etid is not None:
                choices = (c for c in choices if c[0][0] == etid)

        self.fields["environments"].choices = sorted(
            ((":".join(c[0]), c[1]) for c in choices),
            key=k)
        self.fields["environments"].widget.attrs["size"] = 5
        self.fields["environments"].widget.attrs["class"] = "environments"



class BaseEnvironmentConstraintFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        # map of (et.id, et.name) to set of (env.id, env.name)
        self.environments = environments_of(kwargs.pop("groups"))
        self.instance = kwargs.pop("instance", None)
        if self.instance is not None:
            initial = kwargs.setdefault("initial", [])
            narrowed = environments_of(self.instance.environmentgroups)
            # reconstruct previously selected constraints from difference
            # between candidate environments and actual (narrowed)
            for et, envs in self.environments.iteritems():
                diff = envs.difference(narrowed[et])
                if diff:
                    selected = envs.difference(diff)
                    initial.append(
                        {
                            "env_type": et[0],
                            "environments": [
                                "%s:%s" % (et[0], env[0])
                                for env in selected
                                ]
                            })

        super(BaseEnvironmentConstraintFormSet, self).__init__(*args, **kwargs)


    def _get_empty_form(self, **kwargs):
        kwargs["environments"] = self.environments
        # the template form needs all options; no filtering.
        kwargs["filtered"] = False
        # @@@ work around http://code.djangoproject.com/ticket/15349
        kwargs["data"] = None
        kwargs["files"] = None
        return super(BaseEnvironmentConstraintFormSet, self)._get_empty_form(
            **kwargs)
    empty_form = property(_get_empty_form)


    def _construct_form(self, i, **kwargs):
        kwargs["environments"] = self.environments
        return super(BaseEnvironmentConstraintFormSet, self)._construct_form(
            i, **kwargs)


    def save(self, owner, validgroups):
        constraints = {}
        for form in self.forms:
            envs = [v.split(":") for v in form.cleaned_data["environments"]]
            if envs:
                etid = form.cleaned_data["env_type"]
                for_type = constraints.setdefault(etid, set())
                for_type.update([v[1] for v in envs if v[0] == etid])

        if constraints:
            valid_group_ids = set()
            for group in validgroups:
                valid = True
                for env in group.environments:
                    etid = env.environmentType.id
                    if (etid in constraints and
                        env.id not in constraints[etid]):
                        valid = False
                        break
                if valid:
                    valid_group_ids.add(group.id)

            owner.environmentgroups = valid_group_ids
        elif self.instance is not None:
            owner.environmentgroups = validgroups



EnvironmentConstraintFormSet = formset_factory(
    EnvironmentConstraintForm,
    formset=BaseEnvironmentConstraintFormSet,
    extra=0
    )



class EnvConstrainedAddEditForm(tcmforms.AddEditForm):
    parent_name = "product"


    def create_formsets(self, *args, **kwargs):
        if self.instance is None:
            possible_groups = EnvironmentGroupList.ours(auth=self.auth)
        else:
            possible_groups = getattr(
                self.instance, self.parent_name).environmentgroups
        self.env_formset = EnvironmentConstraintFormSet(
            *args,
            **dict(kwargs, groups=possible_groups, prefix="environments")
        )


    def is_valid(self):
        return (
            self.env_formset.is_valid() and
            super(EnvConstrainedAddEditForm, self).is_valid()
            )


    def save(self):
        self.env_formset.save(
            self.instance,
            getattr(self.instance, self.parent_name).environmentgroups)

        return self.instance
