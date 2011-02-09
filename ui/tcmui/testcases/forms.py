import floppyforms as forms

from .models import TestCaseVersion, TestCaseList


class TestCaseForm(forms.Form):
    name = forms.CharField()
    product = forms.ChoiceField(choices=[])
    tags = forms.CharField(required=False)


    def __init__(self, *args, **kwargs):
        products = kwargs.pop("products", [])
        super(TestCaseForm, self).__init__(*args, **kwargs)

        self.products = {}
        choices = []
        for p in products:
            choices.append((p.id, p.name))
            self.products[p.id] = p
        self.fields["product"].choices = choices
        self.auth = products.auth


    def save(self):
        # @@@ ignoring tags field
        testcase = TestCaseVersion(
            name=self.cleaned_data["name"],
            product=self.products[self.cleaned_data["product"]],
            maxAttachmentSizeInMbytes = 0, # @@@
            maxNumberOfAttachments = 0, # @@@
            description = "" # @@@
            )

        TestCaseList.get(auth=self.auth).post(testcase)

        return testcase
