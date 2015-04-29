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

from django.db import models
from django.db.models.fields import related

from phonenumber_field import modelfields
from django_google_maps import fields as mapfields

from swoptact import mixins

class SerializeableMixin:
    """
    Provides a .seralize method which serializes all properties on a model

    You should ensure when putting this on a model that all foreign keys also
    have this mixin added to them.

    This contains recursive functions, only use on models which you are sure
    do not contain cyclic relations.
    """

    def serialize(self):
        """ Provide a dictionary representation of model """
        # Get all the fields on the model
        fields = self._meta.fields

        # Produce the dictionary that will be built
        serialized = {}

        # Iterate over each field to and add the value to serialized.
        for field in fields:
            # Get the value of the field
            value = getattr(self, field.name)

            # If it's a foreign key we should run serialize on the foreign model
            # and also provide a handy string representation
            if isinstance(value, models.Model):
                val_str = str(value)
                value = value.serialize()
                value['__str__'] = val_str

            # Phone numbers give back PhoneNumber objects, we want a string
            if isinstance(value, modelfields.PhoneNumber):
                value = value.raw_input

            # For all other values just add them as per usual
            serialized[field.name] = value

        return serialized

class Address(models.Model, SerializeableMixin):
    """ Representation of an address in Chicago """
    TYPES = (
        ("St", "Street"),
        ("Av", "Avenue"),
        ("Blvd", "Boulevard"),
        ("Rd", "Road"),
    )

    DIRECTIONS = (
        ("N", "North"),
        ("E", "East"),
        ("S", "South"),
        ("W", "West"),
    )

    class Meta:
        verbose_name_plural = "Addresses"

    number = models.IntegerField()
    direction = models.CharField(max_length=1, choices=DIRECTIONS)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPES)
    apartment = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=255, default='Chicago', null=True, blank=True)
    state = models.CharField(max_length=2, default='IL', null=True, blank=True)
    zipcode = models.IntegerField(null=True, blank=True)
    

    def __init__(self, *args, **kwargs):
        super(Address, self).__init__(*args, **kwargs)

        # Compile a dictionary of the choices so we can quickly use them
        self.DICT_TYPES = dict(self.TYPES)
        self.DICT_DIRECTIONS = dict(self.DIRECTIONS)

    def __str__(self):
        return "{number} {direction} {name} {type} #{apartment} {city}, {state} {zipcode}".format(
            number=self.number,
            direction=self.DICT_DIRECTIONS[self.direction],
            name=self.name,
            type=self.DICT_TYPES[self.type],
            apartment = self.apartment,
            city = self.city,
            state = self.state,
            zipcode = self.zipcode
        )

class Institution(models.Model, SerializeableMixin):
    name = models.CharField(max_length=255)
    address = models.ForeignKey(Address, blank=True)
    def __str__(self):
        return "{name}".format(
            name=self.name,
        )

class Participant(models.Model, SerializeableMixin):
    """ Representation of a person who can participate in a Event """
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    primary_phone = modelfields.PhoneNumberField(null=True, blank=True)
    secondary_phone = modelfields.PhoneNumberField(null=True, blank=True)
    email = models.EmailField(blank=True)
    address = models.ForeignKey(Address, null=True, blank=True)
    institution = models.ForeignKey(Institution, null=True, blank=True)

    def __str__(self):
        return "{first_name} {last_name}".format(
            first_name=self.first_name,
            last_name=self.last_name
        )

    def name(self):
        """ The full name of the participant """
        return "{first} {last}".format(
            first=self.first_name,
            last=self.last_name
        )

    @property
    def events(self):
        """ List of all events participant is in """
        return Event.objects.filter(participants__in=[self]).all()


class Event(models.Model, mixins.AdminURLMixin, SerializeableMixin):
    TIMES = (
        ("10am", "Morning"),
        ("12pm", "Noon"),
        ("3pm", "Afternoon"),
        ("7pm", "Evening"),
    )

    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    time = models.CharField(choices = TIMES, max_length = 20, null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    participants = models.ManyToManyField(Participant, blank=True)
    is_prep = models.BooleanField(default=False, blank=True, 
                                  verbose_name = "This meeting is part of a major action:")
    major_action = models.ForeignKey("self", null=True, blank=True)

    def __str__(self):
        return self.name

    def attendee_count(self):
        return self.participants.count()

