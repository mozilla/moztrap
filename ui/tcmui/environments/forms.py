import floppyforms as forms

from ..core.util import id_for_object



class EnvironmentSelectionForm(forms.Form):
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
        for (typeid, typename), options in self.types.iteritems():
            self.fields["type_%s" % typeid] = forms.ChoiceField(
                choices=options, label=typename)

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
                "product. Please select a different combination, or ask the "
                "system administrator to add this one.")

        return self.cleaned_data


    def save(self):
        return [(int(field_name[len("type_"):]), eid) for field_name, eid
                in self.cleaned_data.iteritems()]
