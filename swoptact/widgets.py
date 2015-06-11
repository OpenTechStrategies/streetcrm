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

import phonenumbers

from django import forms
from django.forms import widgets

class LocalPhoneNumberWidget(forms.TextInput):
    """ Renders phone number in the national format """

    def render(self, name, value, *args, **kwargs):
        if isinstance(value, phonenumbers.PhoneNumber):
            # If the number is a US number - format it as a national value
            if value is not None and value.country_code == 1:
                value = value.as_national

        return super(LocalPhoneNumberWidget, self).render(
            name, value, *args, **kwargs
        )

class ForeignKeyRadioRenderer(widgets.RadioFieldRenderer):

    def __init__(self, *args, **kwargs):
        super(ForeignKeyRadioRenderer, self).__init__(*args, **kwargs)
        # Remove the None value which is "---------" (it's always the first one)
        self.choices = self.choices[1:]


class ForeignKeyRadioWidget(forms.RadioSelect):
    """ Radio widget that provides radio buttons """
    renderer = ForeignKeyRadioRenderer