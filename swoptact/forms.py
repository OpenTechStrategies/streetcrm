# SWOPTACT is a list of contacts with a history of their event attendance
# Copyright (C) 2015  Open Tech Strategies, LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import django.forms
from autocomplete_light import forms

from swoptact import models

class TagAdminForm(django.forms.ModelForm):
    class Meta:
        exclude = tuple()
        model = models.Tag
        widgets = {
            "name": django.forms.TextInput(
                attrs={"size": models.Tag.get_field("name").max_length}
            )
        }

class AutoCompleteModelForm(forms.ModelForm):
    """ Creation of new objects from text field of autocomplete fields

    When a field is using an autocomplete field and the object they're entering
    has not been created, this will create the object if the field is the only
    required field to create the object. If the object has other required fields
    this will not provide this functionality.
    """

    def full_clean(self, *args, **kwargs):
        """ Look through fields to see which need models creating """
        if self.data:
            for name, field in self.fields.items():
                # If it's not an autocompletion field we're not interested.
                if not hasattr(field, "autocomplete"):
                    continue

                # Turns out sometimes it has a prefix (for formsets I think)
                name = self.add_prefix(name)

                # Check if we've found a model, if we have no need to create.
                if name in self.data:
                    continue

                # Get the value entered
                value = self.data["{0}-autocomplete".format(name)]

                # If the value is empty just continue.
                if not value:
                    continue

                # Get the model and create it for value
                model = field.autocomplete.create(value)
                model.save()

                # Add the PK to the list
                self.data[name] = model.pk
        super(AutoCompleteModelForm, self).full_clean(*args, **kwargs)

def autocomplete_modelform_factory(model, form=None, *args, **kwargs):
    """ Wrap autocomplete's modelform factory to inject our own form """
    if form is None:
        kwargs["form"] = AutoCompleteModelForm

    return forms.modelform_factory(model, *args, **kwargs)