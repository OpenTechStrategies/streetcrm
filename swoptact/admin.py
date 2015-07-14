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

from django import template
from django.contrib import admin
from django.template import loader
from django.contrib.admin.views import main

import autocomplete_light

from swoptact import forms as st_forms
from swoptact import mixins, models

class ContactInline(admin.TabularInline):
    model = models.Contact
    extra = 0
    verbose_name = "Key Contact"
    verbose_name_plural = "Key Contacts"
    template = "admin/institution_contacts_inline_tabular.html"
    form = st_forms.autocomplete_modelform_factory(
        model=models.Contact,
        exclude=tuple()
    )

class ParticipantAdmin(mixins.SignInSheetAdminMixin, admin.ModelAdmin):
    """ Admin UI for participant including listing event history """
    list_display = ("name", "US_primary_phone", "institution", "address",)
    readonly_fields = ("event_history", "event_history_name", )
    fieldsets = (
        (None, {
            "fields": ("name", "primary_phone",
                       "institution", "title", "secondary_phone", "email", "address")
        }),
    )

    change_fieldsets = (
        (None, {
            "fields": ("name", "primary_phone",
                       "institution", "title", "secondary_phone", "email", "address")
        }),
        ("Personal Event History", {
            "fields": ("event_history",),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if obj:
            return self.change_fieldsets
        return super(ParticipantAdmin, self).get_fieldsets(request, obj)

    form = st_forms.autocomplete_modelform_factory(
        model=models.Participant,
        exclude=tuple()
    )
    actions = None

    @property
    def event_history_name(self, obj):
        """ Name of event history fieldset """
        return "Events that {name} attended".format(
            name=obj.name
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

    def __init__(self,*args,**kwargs):
        super(ParticipantAdmin, self).__init__(*args, **kwargs)
        main.EMPTY_CHANGELIST_VALUE = ''

class AjaxyInlineAdmin(admin.ModelAdmin):
    """
    Base class for those using the ajax'y inline form stuff.

    If you use this, you MUST set inline_form_config!
    """
    # TODO: eventually make this a method so we can use the URL dispatcher?
    inline_form_config = None

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if self.inline_form_config is None:
            raise ValueError("inline_form_config not set D:")

        extra_context = extra_context or {}
        extra_context["inline_form_config"] = json.dumps(
            self.inline_form_config)
        return super(AjaxyInlineAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context)


class EventAdmin(AjaxyInlineAdmin):
    list_display = ("name", "location", "date", "attendee_count",)
    exclude = ('participants',)
    change_form_template = "admin/event_change_form.html"
    form = st_forms.autocomplete_modelform_factory(
        model=models.Event,
        exclude=tuple()
    )
    actions = None
    inline_form_config = {
        "autocomplete_url": "/autocomplete/ContactAutocomplete/",
        "current_inlines_for_page_url": [
            "/api/events/", "<page_model_id>", "/participants"],
        "link_inlined_model_url": [
            "/api/events/", "<page_model_id>",
            "/participants/", "<inlined_model_id>", "/"],
        "existing_inlined_model_url": [
            "/api/participants/", "<inlined_model_id>", "/"],
        "new_inlined_model_url": "/api/participants/",
        "fields": [
            {"descriptive_name": "Name",
             "form_name": "name",
             "input_type": "text"},
            {"descriptive_name": "Institution",
             "form_name": "institution",
             "input_type": "fkey_autocomplete_name",
             "autocomplete_uri": "/autocomplete/InstitutionAutocomplete/"},
            {"descriptive_name": "Attendee's Phone Number",
             "form_name": "primary_phone",
             "input_type": "text"},
         ],
    }

    def __init__(self,*args,**kwargs):
        super(EventAdmin, self).__init__(*args, **kwargs)
        main.EMPTY_CHANGELIST_VALUE = ''


class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name", )
    form = st_forms.autocomplete_modelform_factory(
        model=models.Institution,
        exclude=tuple()
    )
    inlines = (ContactInline,)
    actions = None
    change_list_template = "admin/change_list_without_header.html"

class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "group")
    actions = None
    readonly_fields = ("date_created",)
    form = st_forms.TagAdminForm
    change_form_template = "admin/change_tag_form.html"

    def __init__(self,*args,**kwargs):
        super(TagAdmin, self).__init__(*args, **kwargs)
        main.EMPTY_CHANGELIST_VALUE = ''

class LogAdmin(admin.ModelAdmin):
    actions = None

admin.site.register(models.Participant, ParticipantAdmin)
admin.site.register(models.Event, EventAdmin)
admin.site.register(models.Institution, InstitutionAdmin)
admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.ActivityLog, LogAdmin)
