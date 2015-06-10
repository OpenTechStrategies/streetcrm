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

from django import template, forms
from django.core.exceptions import ValidationError
from django.contrib import admin, staticfiles
from django.contrib.admin.options import InlineModelAdmin
from django.template import loader
from django.conf.urls import patterns, url
from django.shortcuts import render_to_response
from django.forms.models import modelform_factory

from django_google_maps import widgets as map_widgets
from django_google_maps import fields as mapfields

import autocomplete_light

from swoptact import forms as st_forms
from swoptact.models import Participant, Event, Institution, Contact, Tag, ActivityLog
from swoptact import mixins

class ContactInline(admin.TabularInline):
    model = Contact
    extra = 0
    verbose_name = "Contact"
    template = "admin/modified_tabular.html"
    form = st_forms.autocomplete_modelform_factory(Contact, exclude=tuple())

class ParticipantAdmin(mixins.SignInSheetAdminMixin, admin.ModelAdmin):
    """ Admin UI for participant including listing event history """
    list_display = ("name", "US_primary_phone",  "institution", "address",)
    readonly_fields = ("event_history", "event_history_name", )
    fieldsets = (
        (None, {
            "fields": ("first_name", "last_name", "primary_phone", "institution", "secondary_phone", "email",
                        "address")
        }),
    )

    change_fieldsets = (
        (None, {
            "fields": ("first_name", "last_name", "primary_phone", "institution", "secondary_phone", "email",
                        "address")
        }),
        ("Personal Event History", {
            "fields": ("event_history",),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if obj:
            return self.change_fieldsets
        return super(ParticipantAdmin, self).get_fieldsets(request, obj)

    form = st_forms.autocomplete_modelform_factory(Participant, exclude=tuple())
    actions = None

    @property
    def event_history_name(self, obj):
        """ Name of event history fieldset """
        return "Events that {first} {last} attended".format(
            first=obj.first_name,
            last=obj.last_name
        )

    def event_history(self, obj):
        """ HTML history of the events attended by the participant """
        template_name = "admin/includes/event_history.html"
        event_history_template = loader.get_template(template_name)
        context = template.Context({
            "events": obj.events,
        })
        return event_history_template.render(context)

    # To prevent django from distorting how the event_history method looks tell
    # it to allow HTML using the allow_tags method attribute.
    event_history.allow_tags = True

    def US_primary_phone(self, obj):
        if obj.primary_phone is None:
            return None

        # Is it a US number
        if obj.primary_phone.country_code == 1:
            return obj.primary_phone.as_national
        else:
            return obj.primary_phone.as_international

    US_primary_phone.short_description = "Phone Number"

class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "date", "attendee_count",)
    exclude = ('participants', 'time')
    change_form_template = "admin/event_change_form.html"
    form = autocomplete_light.modelform_factory(Event, exclude=tuple())
    actions = None

class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name", )
    form = st_forms.autocomplete_modelform_factory(Institution, exclude=tuple())
    inlines = (ContactInline,)
    actions = None

class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "group")
    actions = None

class LogAdmin(admin.ModelAdmin):
    actions = None

admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Institution, InstitutionAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ActivityLog, LogAdmin)
