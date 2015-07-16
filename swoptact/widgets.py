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
