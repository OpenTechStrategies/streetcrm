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

import copy
import json
import datetime
import functools

from django import template
from django.conf import settings
from django.core import exceptions
from django.contrib import admin, auth
from django.template import loader
from django.conf.urls import url
from django.contrib.admin.views import main
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _

import watson
import autocomplete_light

from swoptact import forms as st_forms
from swoptact import mixins, models, admin_filters

class SWOPTACTAdminSite(admin.AdminSite):

    login_form = st_forms.AdminLoginForm
    search_engine = watson.admin.admin_search_engine
    search_template = "admin/search.html"
    advanced_search_template = "admin/advanced_search.html"

    def has_permission(self, request):
        """
        Checks if the user has access to at least one admin page.

        This previously checked `request.user.is_staff.` All users should
        have access to the "admin" site so we removed that check.  It's
        redundant.

        """
        return request.user.is_active

    def password_change(self, request, *args, **kwargs):
        """
        Verify that they are in the "can_change_password" group
        """
        if not request.user.has_perm("auth.can_change_password"):
            raise exceptions.PermissionDenied

        return super(SWOPTACTAdminSite, self).password_change(
            request,
            *args,
            **kwargs
        )

    def get_urls(self, *args, **kwargs):
        urls = super(SWOPTACTAdminSite, self).get_urls(*args, **kwargs)

        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)
            wrapper.admin_site = self
            return functools.update_wrapper(wrapper, view)

        # Add a URL for the search results

        urls.append(
            url(r"^search/$", wrap(self.search_dispatcher), name="search"),
        )

        return urls

    def search_dispatcher(self, request):
        """ Takes in searches and sends them to the advanced or basic view """
        advanced = request.GET.get("advanced", False)

        # Build the form from the POST data
        if request.method == "POST":
            form = st_forms.SearchForm(request.POST)
        else:
            form = st_forms.SearchForm()

        # If it's a GET request or the form is invalid, return now.
        if request.method == "GET" or not form.is_valid():
            return TemplateResponse(
                request,
                self.search_template,
                {
                    "advanced": advanced,
                    "form": form,
                }
            )

        # If it's advanced send it that view, else send it to the basic view
        if advanced:
            return self.advanced_search_view(request, form)
        else:
            return self.basic_search_view(request, form)

    def basic_search_view(self, request, form):
        """
        View for the basic search for objects
        """
        # Peform the search
        results = self.search_engine.search(form.cleaned_data["query"])

        # Process the results into their objects
        results = [result.object for result in results]

        # Display the results
        return TemplateResponse(
            request,
            self.search_template,
            {
                "search_results": {None: results},
                "form": form,
            }
        )

    def advanced_search_view(self, request, form):
        """
        This provides advanced searching options
        """
        data = form.get_processed_data()
        categorize = data["search_model"]

        exclude_major = data["exclude_major_events"]
        exclude_minor = data["exclude_minor_events"]

        # Initially we should build up a list of Events that we could be
        # be potentially searching through, these can come from Events with
        # a specific tag, events which were specified as part of the form
        major_events = []
        minor_events = []

        # Look up all of the events that could fit the search, since this is
        # the only time we'll have a queryset and it's far faster to do this
        # in the database we should handle the situation of tags here too.
        event_query = models.Event.objects.all()
        if data["event_tags"]:
            event_query = event_query.filter(tags__in=data["event_tags"])

        # Filter by the datetime constraints if they have been given
        if data["start_date"] is not None:
            event_query = event_query.filter(date__gte=data["start_date"])
        if data["end_date"] is not None:
            event_query = event_query.filter(date__lte=data["end_date"])

        if isinstance(data["event"], str):
            major_events += event_query.filter(
                name__contains=data["event"],
                is_prep=False
            )
            minor_events += event_query.filter(
                name__contains=data["event"],
                is_prep=True
            )

        # If there is an event found by the autocompletion
        elif isinstance(data["event"], models.Event):
            # If there are tags double check it has the tags required
            shared_tags = [
                t for t in data["event_tags"] if t in data["event"].tags.all()
            ]
            if not data["event_tags"] or (data["event_tags"] and shared_tags):
                # Add it to the correct list
                if data["event"].is_prep:
                    minor_events.append(data["event"])
                else:
                    major_events.append(data["event"])

        else:
            major_events += event_query.filter(is_prep=False)
            minor_events += event_query.filter(is_prep=True)

        # If we are to include minor events we should look up all the minor
        # events for the major events that we have found so far.
        if not exclude_minor:
            for major_event in major_events:
                minor_events += major_event.minor_events

        # Make a general Events list.
        events = []
        if not exclude_major:
            events += major_events
        if not exclude_minor:
            events += minor_events

        event_participants = []

        # If a participant was specified then we need to filter the results
        # to only show those which either match in the case of an object found
        # with the autocompletion or if it contains the search string.
        if isinstance(data.get("participant"), str):
            event_participants = dict((
                (e, e.participants.filter(name__contains=data["participant"]))
                for e in events
            ))
        elif isinstance(data.get("participant"), models.Participant):
            event_participants = dict((
                (e, e.participants.filter(name__in=[data["participant"]]))
                for e in events
            ))
        else:
            event_participants = dict((
                (event, event.participants.all()) for event in events
            ))

        # If there has been a query on the institution we need to filter on that
        # unfortunately I can't think of any other way to do this so it'll be in
        # python, which will make it a little slower than the rest.
        institutions = []
        institution_query = models.Institution.objects.all()

        # Narrow the institutions down if there have been tags selected
        if data["institution_tags"]:
            institution_query = institution_query.filter(
                tags__in=data["institution_tags"]
            )

        if isinstance(data.get("institution"), str):
            # Perform a search for the institution(s) which match
            institutions += institution_query.filter(
                name__contains=data["institution"]
            )
        elif isinstance(data.get("institution"), models.Institution):
            # This is when the autocomplete has found one
            institutions.append(data["institution"])
        elif categorize == form.INSTITUTION:
            # Because we're going to catagorise based on institution we need to
            # build the institution list with all the institutions
            institutions += institution_query

        # Build the end results
        if categorize == form.PARTICIPANT:
            # When searching just for participants don't show a section, just list
            # the participants on their own.
            results = {None: set()}
        elif categorize == form.EVENT:
            # Both participants and events, we actually want to group by event
            results = dict([(e, list()) for e, p in event_participants.items()])
        elif categorize == form.INSTITUTION:
            results = dict([(i, set()) for i in institutions])

        if categorize == form.INSTITUTION or data["institution"]:
            # We then should iterate through the institution and filter participants
            # out which are not part contacts of the institution.
            for institution in institutions:
                contacts = institution.contacts.all()

                # Look at the intersection between event_participants and contacts
                for event, participants in event_participants.items():
                    intersection = [p for p in participants if p in contacts]

                    # Add it to the results depending what we're displaying by
                    if categorize == form.PARTICIPANT:
                        results[None] = results[None] | set(intersection)
                    elif categorize == form.EVENT:
                        # catagorise by event
                        results[event] += intersection
                    elif categorize == form.INSTITUTION:
                        results[institution] = results[institution] | set(intersection)
        elif categorize == form.EVENT:
            results = event_participants
        elif categorize == form.PARTICIPANT:
            results = set()
            for event, participants in event_participants.items():
                results = results | set(participants)
            results = {None: results}

        # Remove any without participants
        results = dict(((s, p) for s, p in results.items() if p))

        # Return the response.
        return TemplateResponse(
            request,
            self.search_template,
            {
                "form": form,
                "advanced": True,
                "search_results": results,
            }
        )

class ContactInline(admin.TabularInline):
    model = models.Institution.contacts.through
    extra = 0
    verbose_name = "Key Contact"
    verbose_name_plural = "Key Contacts"
    template = "admin/institution_contacts_inline_tabular.html"
    form = st_forms.autocomplete_modelform_factory(
        model=models.Institution.contacts.through,
        exclude=tuple()
    )

class ParticipantAdmin(mixins.AdminArchiveMixin, mixins.SignInSheetAdminMixin, watson.SearchAdmin):
    """ Admin UI for participant including listing event history """
    search_fields = ("name", "primary_phone", "title", "email",
                     "participant_street_address",
                     "participant_city_address",
                     "participant_state_address",
                     "participant_zipcode_address")
    list_filter = (admin_filters.ArchiveFilter,)
    list_display = ("name", "US_primary_phone", "institution", "participant_street_address",)
    readonly_fields = ("action_history", "event_history_name")
    fieldsets = (
        (None, {
            "fields": ("name", "primary_phone",
                       "institution", "title", "secondary_phone", "email",
                       "participant_street_address",
                       "participant_city_address",
                       "participant_state_address",
                       "participant_zipcode_address")
        }),
    )

    change_fieldsets = (
        (None, {
            "fields": ("name", "primary_phone",
                       "institution", "title", "secondary_phone", "email",
                       "participant_street_address",
                       "participant_city_address",
                       "participant_state_address",
                       "participant_zipcode_address")
        }),
        ("Personal Action History", {
            "fields": ("action_history",),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if obj:
            return self.change_fieldsets
        return super(ParticipantAdmin, self).get_fieldsets(request, obj)
    change_form_template = "admin/change_participant_form.html"
    form = st_forms.autocomplete_modelform_factory(
        model=models.Participant,
        exclude=("archived",)
    )
    actions = None

    @property
    def event_history_name(self, obj):
        """ Name of event history fieldset """
        return "Actions that {name} attended".format(
            name=obj.name
        )

    def action_history(self, obj):
        """ HTML history of the events attended by the participant """
        template_name = "admin/includes/event_history.html"
        action_history_template = loader.get_template(template_name)
        context = template.Context({
            "events": obj.events,
        })
        return action_history_template.render(context)

    # To prevent django from distorting how the event_history method looks tell
    # it to allow HTML using the allow_tags method attribute.
    action_history.allow_tags = True

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

class AjaxyInlineAdmin(watson.SearchAdmin):
    """
    Base class for those using the ajax'y inline form stuff.

    If you use this, you MUST set inline_form_config!
    """
    # TODO: eventually make this a method so we can use the URL dispatcher?
    inline_form_config = None
    def _can_user_edit_ajaxily(self, user):
        # Cheap version, but we can make this more fine grained depending on
        # appropriate groups
        return user.is_superuser or user.is_staff

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if self.inline_form_config is None:
            raise ValueError("inline_form_config not set D:")

        extra_context = extra_context or {}
        # We copy this so we can modify special dynamic stuff...
        inline_form_config = copy.copy(self.inline_form_config)

        # Can the user access the inline add/edit permissions?
        inline_form_config["user_can_edit"] = self._can_user_edit_ajaxily(
            request.user)

        # Add the full list of user permissions to the inline config.
        # (commented out for now; leaving in code in case proves useful later).
        # inline_form_config["user_permissions"] = list(request.user.get_group_permissions());

        # Add the current user's group to the inline config.
        userGroups = list(request.user.groups.values_list('name',flat=True))
        inline_form_config["user_group"] = userGroups[0] if len(userGroups) > 0 else "developer"

        extra_context["user_can_edit_inline"] = inline_form_config["user_can_edit"]
        extra_context["inline_form_config"] = json.dumps(
            inline_form_config)
        return super(AjaxyInlineAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context)


class EventAdmin(mixins.AdminArchiveMixin, AjaxyInlineAdmin):
    search_fields = ("name", "location")
    list_filter = (admin_filters.ArchiveFilter, "tags__name")
    list_display = ("name", "location", "date", "attendee_count",)
    change_form_template = "admin/event_change_form.html"
    form = st_forms.autocomplete_modelform_factory(
        model=models.Event,
        exclude=("participants", "archived")
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
        "existing_inlined_model_profile_url": [
            "/swoptact/participant/", "<inlined_model_id>", "/"],
        "new_inlined_model_url": "/api/participants/",
        "inlined_model_name_plural": "Attendees",
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

    def __init__(self, *args, **kwargs):
        super(EventAdmin, self).__init__(*args, **kwargs)
        main.EMPTY_CHANGELIST_VALUE = ''

    def _can_user_edit_ajaxily(self, user):
        if user.is_superuser:
            return True

        return user.is_staff and user.has_perms(
            ["swoptact.change_event", "swoptact.change_participant",
             "swoptact.change_contact", "swoptact.change_institution",
             "swoptact.add_event", "swoptact.add_participant",
             "swoptact.add_contact", "swoptact.add_institution"])


class InstitutionAdmin(mixins.AdminArchiveMixin, AjaxyInlineAdmin):
    search_filter = ("name", "inst_street_address", "inst_city_address", "inst_state_address"
                     "inst_zipcode_address")
    list_filter = (admin_filters.ArchiveFilter,)
    list_display = ("name", )
    change_form_template = "admin/ajax_inline_change_form.html"
    form = st_forms.autocomplete_modelform_factory(
        model=models.Institution,
        exclude=("archived", "contacts",)
    )
    actions = None
    change_list_template = "admin/change_list_without_header.html"
    inline_form_config = {
        "autocomplete_url": "/autocomplete/ContactAutocomplete/",
        "current_inlines_for_page_url": [
            "/api/institutions/", "<page_model_id>", "/contacts"],
        "link_limit": settings.CONTACT_LIMIT,
        "link_inlined_model_url": [
            "/api/institutions/", "<page_model_id>",
            "/contacts/", "<inlined_model_id>", "/"],
        "existing_inlined_model_url": [
            "/api/participants/contact/", "<inlined_model_id>", "/"],
        "existing_inlined_model_profile_url": [
            "/swoptact/participant/", "<inlined_model_id>", "/"],
        "new_inlined_model_url": "/api/contacts/",
        "inlined_model_name_plural": "Contacts",
        "fields": [
            {"descriptive_name": "Name",
             "form_name": "name",
             "input_type": "text"},
            {"descriptive_name": "Title",
             "form_name": "title",
             "input_type": "text"},
            {"descriptive_name": "Phone Number",
             "form_name": "primary_phone",
             "input_type": "text"},
         ],
    }

    def _can_user_edit_ajaxily(self, user):
        if user.is_superuser:
            return True

        return user.is_staff and user.has_perms(
            ["swoptact.change_participant",
             "swoptact.change_contact", "swoptact.change_institution,"
             "swoptact.add_participant",
             "swoptact.add_contact", "swoptact.add_institution"])


class TagAdmin(mixins.AdminArchiveMixin, watson.SearchAdmin):
    search_fields = ("name",)
    list_filter = (admin_filters.ArchiveFilter,)
    list_display = ("name", "description", "group")
    actions = None
    readonly_fields = ("date_created",)
    form = st_forms.TagAdminForm
    change_form_template = "admin/change_tag_form.html"
    excludes = ("archived",)

    def __init__(self,*args,**kwargs):
        super(TagAdmin, self).__init__(*args, **kwargs)
        main.EMPTY_CHANGELIST_VALUE = ''

class LogAdmin(admin.ModelAdmin):
    actions = None

class UserAdmin(auth.admin.UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (_("Permissions"), {"fields": ("is_active", "is_superuser", "groups",
                                       "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    list_display = ("username", "email", "first_name", "last_name")
    list_filter = ("is_superuser", "is_active", "groups")
    actions = None

# Create the admin site
site = SWOPTACTAdminSite()

# Register auth AdminModels
site.register(auth.admin.Group, auth.admin.GroupAdmin)
site.register(auth.admin.User, UserAdmin)

# Register SWOPTACT AdminModels
site.register(models.Participant, ParticipantAdmin)
site.register(models.Event, EventAdmin)
site.register(models.Institution, InstitutionAdmin)
site.register(models.Tag, TagAdmin)
site.register(models.ActivityLog, LogAdmin)
