import floppyforms as forms

from ..core.util import id_for_object



class EnvironmentSelectionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        groups = kwargs.pop("groups")
        super(EnvironmentSelectionForm, self).__init__(*args, **kwargs)

        # maps (envtype.id, envtype.name) to list of env options for that type
        # e.g. (1, "Operating System") => [(5, "Windows"), (6, "Linux")]
        self.types = {}

        # maps a set of env ids to a group id
        # e.g. {set([6, 8]): 1, set([6, 9]): 2, set([7, 8]): 3, set([7, 9]): 4}
        self.groups = {}

        for group in groups:
            env_ids = set()
            for env in group.environments:
                env_ids.add(env.id)
                et = env.environmentType
                options = self.types.setdefault((et.id, et.name), set())
                options.add((id_for_object(env), env.name))
            self.groups[frozenset(env_ids)] = group.id

        # construct choice-field for each env type
        for (typeid, typename), options in self.types.iteritems():
            self.fields["type_%s" % typeid] = forms.ChoiceField(
                choices=options, label=typename)


    def clean(self):
        """
        Check that the set of selected environments fit together into a valid
        environment group (all combinations should be valid if autogenerate was
        used, but this isn't guaranteed).

        """
        env_ids = frozenset([eid for eid in self.cleaned_data.itervalues()])
        try:
            self.cleaned_data["group_id"] = self.groups[env_ids]
        except KeyError:
            raise forms.ValidationError(
                "The selected environment combination is not valid for this "
                "product. Please select a different combination, or ask the "
                "system administrator to add this one.")

        return self.cleaned_data


    def save(self):
        return self.cleaned_data["group_id"]
