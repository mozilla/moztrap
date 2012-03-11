# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-2012 Mozilla
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
"""
Management forms for products.

"""
import floppyforms as forms

from .... import model

from ...utils import ccforms




class ProductForm(ccforms.NonFieldErrorsClassFormMixin, ccforms.CCModelForm):
    """Base form for products."""
    class Meta:
        model = model.Product
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput,
            "description": ccforms.BareTextarea,
            }



class EditProductForm(ProductForm):
    """Form for editing a product."""
    pass



class AddProductForm(ProductForm):
    """Form for adding a product."""
    version = forms.CharField(required=True)
    profile = forms.ModelChoiceField(
        queryset=model.Profile.objects.all(),
        required=False,
        widget=forms.Select)


    def save(self, user=None):
        """Save and return the new Product; also save initial version."""
        user = user or self.user

        product = super(AddProductForm, self).save(user=user)

        version = model.ProductVersion.objects.create(
            product=product,
            version=self.cleaned_data["version"],
            user=user)

        profile = self.cleaned_data.get("profile")
        if profile is not None:
            version.environments.add(*profile.environments.all())

        return product
