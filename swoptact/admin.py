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
import functools
from collections import namedtuple

from django import template
from django.conf import settings
from django.core import exceptions
from django.contrib import admin, auth
from django.template import loader
from django.conf.urls import url
from django.contrib.admin.views import main
from django.db.models import Q
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

import watson
import autocomplete_light

from swoptact import forms as st_forms
from swoptact import mixins, models, admin_filters


class SWOPTACTAdminSite(admin.AdminSite):

    login_form = st_forms.AdminLoginForm
    search_engine = watson.admin.admin_search_engine
    search_template = "admin/search.html"

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
        urls.extend([
            url(r"^search/$", wrap(self.search_view), name="search"),
            url(r"^missing_data/$", wrap(self.missing_data_view),
                name="missing_data"),
        ])

        return urls

    def missing_data_view(self, request):
        """
        Missing data report
        """
        # This is an admittedly long and kind of complex looking function.
        # Maybe this documentation will help, o future hacker!
        #
        # However, there's reason for it.  Some details about this function:
        #  - We have some one-off datastructures via namedtuples to keep
        #    things organized.  The nice thing about this is that things
        #    become reasonably declarative towards the end of the function
        #    so adjusting the fields is pretty easy.
        #
        #  - So as to not have unnecessarily duplicate queries (which
        #    will then be hard to reconcile as to which object is the
        #    canonical representation of the same row) we query all at
        #    once for all possible missing fields (hence the
        #    _construct_query stuff).  So we then later walk over the
        #    objects we got back to find out what all of the missing
        #    fields (as per our nice CheckField specifications) were.
        #
        # Hope that helps!

        context = {}

        # Simple structure for organizing fields we check
        CheckField = namedtuple(
            "CheckField", ["field_name", "null", "empty_string"])
        TableResults = namedtuple(
            "TableResults", ["table_name", "results"])
        MissingField = namedtuple(
            "MissingField", ["field_name", "human_readable"])
        ModelWithMissingFields = namedtuple(
            "ModelWithMissingFields",
            ["model", "human_readable", "missing_fields", "admin_uri"])

        def _construct_query(fields):
            """Construct a query based on list of CheckFields

            We're just trying to find out which fields are missing data,
            and depending on the CheckField specification, "missing data"
            may be either or both of NULL or an empty string.

            Piping together Q objects is a way of OR'ing them, so
            this way we've built up a nice list of possibilities on
            how a model's 
            """
            # We're wrapping this in a mutable list because of hacks
            # in setting values in closures in python :\
            # So this kind of acts as a mutable "box".
            # But all we care about is query[0]
            query = [None]

            def _join_query(q):
                if query[0] is None:
                    # Assigning it here would have confused python
                    # had we just done "query = q", hence the box...
                    query[0] = q
                else:
                    # ... here too of course.
                    query[0] = query[0] | q

            for field in fields:
                if field.null:
                    _join_query(Q(**{"%s__isnull" % field.field_name: True}))
                if field.empty_string:
                    _join_query(Q(**{field.field_name: ""}))

            return query[0]

        def gather_results(this_model, fields, change_uri_reverser):
            results = []

            query = _construct_query(fields)
            objects = this_model.objects.filter(query)

            for obj in objects:
                missing_fields = []
                for field in fields:
                    if ((field.null and getattr(obj, field.field_name) is None)
                        or (field.empty_string and
                            getattr(obj, field.field_name) == "")):
                        human_readable = obj._meta.get_field(
                            field.field_name).verbose_name.title()
                        missing_fields.append(
                            MissingField(field.field_name, human_readable))

                # If there are missing fields, append to the results
                if missing_fields:
                    # Could make this more extensible if obj.id was ever
                    admin_uri = change_uri_reverser(obj)
                    results.append(
                        ModelWithMissingFields(obj, str(obj),
                                               missing_fields, admin_uri))

            return results

        def _gen_change_uri_func(reverse_name):
            """
            Handy function for generating uri reversers
            for objects in some table
            """
            # Make a one argument closure which takes the object and return it
            def reverser(obj):
                return reverse(reverse_name, args=(obj.id,))
            return reverser

        event_results = gather_results(
            models.Event,
            [CheckField("name", null=False, empty_string=True),
             CheckField("description", null=True, empty_string=True),
             CheckField("date", null=True, empty_string=False),
             CheckField("time", null=True, empty_string=False),
             CheckField("organizer", null=True, empty_string=False),
             CheckField("location", null=True, empty_string=True),
             CheckField("issue_area", null=True, empty_string=True)],
            _gen_change_uri_func("admin:swoptact_event_change"))

        participant_results = gather_results(
            models.Participant,
            [CheckField("name", null=False, empty_string=True),
             CheckField("primary_phone", null=True, empty_string=False),
             CheckField("email", null=True, empty_string=True),
             CheckField("participant_street_address",
                        null=True, empty_string=True),
             CheckField("participant_city_address",
                        null=True, empty_string=True),
             CheckField("participant_state_address",
                        null=True, empty_string=True),
             CheckField("participant_zipcode_address",
                        null=True, empty_string=True),
             CheckField("institution",
                        null=True, empty_string=False),
             CheckField("title",
                        null=True, empty_string=True)],
            _gen_change_uri_func("admin:swoptact_participant_change"))

        institution_results = gather_results(
            models.Institution,
            [CheckField("name", null=True, empty_string=True),
             CheckField("inst_street_address",
                        null=True, empty_string=True),
             CheckField("inst_city_address",
                        null=True, empty_string=True),
             CheckField("inst_state_address",
                        null=True, empty_string=True),
             CheckField("inst_zipcode_address",
                        null=True, empty_string=True)],
            _gen_change_uri_func("admin:swoptact_institution_change"))

        results = [
            TableResults("Events", event_results),
            TableResults("Participants", participant_results),
            TableResults("Institutions", institution_results)]

        context = dict(
            # Django docs say these are common variables
            # for rendering the admin template. :)
            self.each_context(request),
            # Other args
            results=results)

        return TemplateResponse(
            request,
            "admin/missing_data_report.html",
            context)

    def search_view(self, request):
        """
        View for searching for objects
        """
        search_query = request.GET.get("q")
        context = {"search_query": search_query}

        # If there is no term provided just display the template
        if search_query is None:
            return TemplateResponse(
                request,
                self.search_template,
                context
            )

        # Peform the search
        context["search_results"] = self.search_engine.search(
            search_query
        )
        context["search_results_amount"] = len(context["search_results"])

        # Display the results
        return TemplateResponse(
            request,
            self.search_template,
            context
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
        exclude=("participants", "archived"),
        form=st_forms.TagSkippingAutoCompleteModelForm,
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
        exclude=("archived", "contacts",),
        form=st_forms.TagSkippingAutoCompleteModelForm,
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
