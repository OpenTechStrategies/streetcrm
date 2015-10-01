# SWOPTACT is a list of contacts with a history of their event attendance
# Copyright (C) 2015  Local Initiatives Support Corporation (LISC)
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

import json

import phonenumbers

from django import forms
from django.forms import widgets
from django.forms.utils import flatatt
from django.utils.html import format_html

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

class TwelveHourTimeWidget(forms.MultiWidget):
    """ 12 Hour time widget that gives back a datetime.time object """

    AM_SUFFIX = 0
    PM_SUFFIX = 12

    # Time choices could be generated programatically however, I think for
    # constant values (which is essencially what choices are) they should
    # remain verbosely laid out like this.
    TIME_CHOICES = (
        ("", "--"), # Blank - no time specified.
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
        (6, "6"),
        (7, "7"),
        (8, "8"),
        (9, "9"),
        (10, "10"),
        (11, "11"),
        (12, "12"),
    )

    TIME_SUFFIXES = (
        (AM_SUFFIX, "am"),
        (PM_SUFFIX, "pm"),
    )

    def __init__(self, attrs=None):
        time = forms.Select(choices=self.TIME_CHOICES)
        suffix = forms.RadioSelect(choices=self.TIME_SUFFIXES)

        super(TwelveHourTimeWidget, self).__init__((time, suffix), attrs)

    def decompress(self, value):
        # Check for no value and return back
        if value is None:
            return [None, None]

        hours = int(value.strftime("%I"))
        suffix = self.AM_SUFFIX if value.hour < 12 else self.PM_SUFFIX

        return [hours, suffix]


PERSISTENT_AUTOCOMPLETE_TEMPLATE = """\
<div class="persistent-autocomplete" {}>
  <input type="text" class="user-widget" {} />
</div>"""


class PersistentTextAutocomplete(forms.Widget):
    """
    This field is for when you want to provide autocomplete, but don't
    want that widget to go away after the user selects something.

    This takes one two extra, mandatory arguments in addition to normal
    django fields, the `gather_options thunk' and
    `get_display_text' procedure.

    `gather_options' should return a dictionary of display: value, like:

      {"Wisconsin": 1, "Illinois": 2}

    (Why the display mapped to value and not the reverse?  Because the
    user is writing to a textbox, and each term can only map to one
    thing)

    `get_display_text' should take one argument, the current value,
    and return text for the value field.
    """
    def __init__(self, gather_options, get_display_text, *args, **kwargs):
        self.gather_options = gather_options
        self.get_display_text = get_display_text
        super(PersistentTextAutocomplete, self).__init__(
            *args, **kwargs)

    def render(self, name, value, attrs=None):
        options = self.gather_options()
        display_text = self.get_display_text(value)

        return format_html(
            PERSISTENT_AUTOCOMPLETE_TEMPLATE,
            flatatt({"data-options": json.dumps(options)}),
            flatatt({"value": display_text, "name": name}))


class SimpleFKAutocomplete(PersistentTextAutocomplete):
    """
    Like PersistentTextAutocomplete, but builds a simple completer
    for you out of the model
    """
    def __init__(self, model, to_string=str, *args, **kwargs):
        def gather_options():
            return [to_string(i) for i in model.objects.all()]

        def get_display_text(value):
            if value and isinstance(value, int):
                return str(model.objects.get(pk=value))
            # Should be a string then...
            elif value:
                return value
            else:
                return ""

        super(SimpleFKAutocomplete, self).__init__(
            gather_options, get_display_text, *args, **kwargs)
