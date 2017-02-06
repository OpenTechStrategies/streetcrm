# StreetCRM is a list of contacts with a history of their event attendance
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

import collections
import copy
import json
import datetime
import functools
from collections import namedtuple

from django import template
from django.conf import settings
from django.core import exceptions
from django.contrib import admin, auth
from django.template import loader
from django.conf.urls import url
from django.contrib.admin.views import main
from django.contrib.admin.models import LogEntry

# The LogEntry model defines three action_flags: ADDITION = 1,
# CHANGE = 2, DELETION = 3.  I'm adding SEARCH so we can easily find all
# the searches that have been logged.
SEARCH=4

from django.db.models import Q
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from watson import search as watson
from watson import admin as watson_admin
from watson.admin import SearchAdmin

import autocomplete_light

from streetcrm import forms as st_forms
from streetcrm import mixins, models, admin_filters


class STREETCRMAdminSite(admin.AdminSite):

    login_form = st_forms.AdminLoginForm
    search_engine = watson_admin.admin_search_engine
    search_template = "admin/search.html"
    advanced_search_template = "admin/advanced_search.html"

    def _nested_search(self, haystack, test):
        """
        Find unique objects exist in the values of the structure

        This takes a dictionary or dictionary of nested dictionaries, it
        recursively goes over them and peforms the test on them, if so adds
        them to a set which will be returned.

        The test parameter is a callable test which takes one parameter and
        returns a boolean on if it's to be included.
        """
        results = set()
        for k, v in haystack.items():
            if isinstance(v, dict):
                results = results | self._nested_search(v, test)

            # Apply the test to the key
            if hasattr(k, "__iter__"):
                results = results | k if test(k) else results
            else:
                results = results | {k} if test(k) else results

            # Apply the tests to the value
            if hasattr(v, "__iter__"):
                results = results | v if test(v) else results
            else:
                results = results | {v} if test(v) else results

        return results

    def _remove_empty_values(self, structure):
        """ Takes in a dict and removes empty values of all nested dicts """
        processed = collections.OrderedDict()
        for k, v in structure.items():
            if isinstance(v, dict):
                v = self._remove_empty_values(v)

            if v:
                processed[k] = v

        return processed

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

        return super(STREETCRMAdminSite, self).password_change(
            request,
            *args,
            **kwargs
        )

    def get_urls(self, *args, **kwargs):
        urls = super(STREETCRMAdminSite, self).get_urls(*args, **kwargs)

        def wrap(view, cacheable=False):
            def wrapper(*args, **kwargs):
                return self.admin_view(view, cacheable)(*args, **kwargs)
            wrapper.admin_site = self
            return functools.update_wrapper(wrapper, view)

        # Add a URL for the search results

        urls.append(
            url(r"^search/$", wrap(self.search_dispatcher), name="search"),
        )

        urls.extend([
            url(r"^missing_data/$", wrap(self.missing_data_view),
                name="missing_data"),
        ])

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
            # Show results from basic search, but still show the
            # advanced form when requested
            if request.method == "GET" and not advanced:
                search_query = request.GET.get("q")
                
                # If a search term is provided, show results
                if search_query is not None and search_query is not "":
                    return self.basic_search_view(request, form, search_query)

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

    def log_basic_search(self, request, search_query):
        # this is a crazy test.
        # save the search:
        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=None,
            object_id=None,
            object_repr=search_query,
            action_flag=SEARCH,
            change_message="Basic search.")
        return;

    def basic_search_view(self, request, form, search_query=None):
        """
        View for the basic search for objects
        """
        # Perform the search, whether passed from header or the basic
        # form
        if not search_query:
            search_query = form.cleaned_data["query"]

        self.log_basic_search(request, search_query)

        results = self.search_engine.search(search_query)
        
        # Process the results into their objects
        results = [result.object for result in results]

        # Display the results
        return TemplateResponse(
            request,
            self.search_template,
            {
                "search_results": {"results": results},
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
        event_filtered = False
        if data["event_tags"]:
            event_filtered = True
            event_query = event_query.filter(tags__in=data["event_tags"])

        # If they've specified an organizer lets filter by that too.
        if isinstance(data["event_organizer"], str):
            event_filtered = True
            event_query = event_query.filter(
                organizer__name__contains=data["event_organizer"]
            )
        elif isinstance(data["event_organizer"], models.Participant):
            event_filtered = True
            event_query = event_query.filter(organizer=data["event_organizer"])

        # If they've searched on a major event then we also filter by that.
        if isinstance(data["connected_action"], str):
            event_filtered = True
            event_query = event_query.filter(
                major_action__name__contains=data["connected_action"]
            )
        elif isinstance(data["connected_action"], models.Event):
            event_filtered = True
            event_query = event_query.filter(major_action=data["connected_action"])

            
        # Filter by the datetime constraints if they have been given
        if data["start_date"] is not None:
            event_filtered = True
            event_query = event_query.filter(date__gte=data["start_date"])
        if data["end_date"] is not None:
            event_filtered = True
            event_query = event_query.filter(date__lte=data["end_date"])

        if isinstance(data["event"], str):
            event_filtered = True
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
            event_filtered = True
            event_query = event_query.filter(pk=data["event"].pk)

        major_events += event_query.filter(is_prep=True)
        minor_events += event_query.filter(is_prep=False)

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

        # Find the participants which aren't related to any of the events.
        if not event_filtered:
            unique_participants = set()
            for p in event_participants.values():
                participant_ids = [p1.id for p1 in p]
                unique_participants = unique_participants | set(participant_ids)
        
            non_event_participants = models.Participant.objects.exclude(
                pk__in=unique_participants
            )

            if isinstance(data.get("participant"), str):
                non_event_participants = non_event_participants.filter(
                    name__contains=data["participant"]
                )
            elif isinstance(data.get("participant"), models.Participant):
                non_event_participants = non_event_participants.filter(
                    pk=data["participant"].pk
                )

            event_participants[None] = non_event_participants

        # If there has been a query on the institution we need to filter on that
        # unfortunately I can't think of any other way to do this so it'll be in
        # python, which will make it a little slower than the rest.
        institutions = []
        institution_query = models.Institution.objects.all()
        institution_filtered = False 
        # Narrow the institutions down if there have been tags selected
        if data["institution_tags"]:
            institution_filtered = True
            institution_query = institution_query.filter(
                tags__in=data["institution_tags"]
            )

        if isinstance(data.get("institution"), str):
            # Perform a search for the institution(s) which match
            institution_filtered = True
            institutions += institution_query.filter(
                name__contains=data["institution"]
            )
        elif isinstance(data.get("institution"), models.Institution):
            institution_filtered = True
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
            # Look at the intersection between event_participants and contacts
            for event, participants in event_participants.items():
                for participant in participants:
                    # If it's not in the institutions, skip it.
                    if participant.institution not in institutions:
                        continue
   
                    # Add it to the results depending what we're displaying by
                    if categorize == form.PARTICIPANT:
                        results[None].add(participant)
                    elif categorize == form.EVENT:
                        results[event].append(participant)
                    elif categorize == form.INSTITUTION:
                        results[participant.institution].add(participant)

            if categorize == form.INSTITUTION and not institution_filtered:
                institution_participants = set()
                for participants in results.values():
                    pks = [p.pk for p in participants]
                    institution_participants = institution_participants | set(pks)
                non_institution_participants = models.Participant.objects.exclude(
                    pk__in=institution_participants
                )
                if isinstance(data["participant"], str):
                    non_institution_participants = non_institution_participants.filter(
                        name__contains=data["participant"]
                    )
                elif isinstance(data["participant"], models.Participant):
                    non_institution_participants = non_institution_participants.filter(
                        pk=data["participant"].pk
                    )
                results[_("No Institution")] = non_institution_participants
        elif categorize == form.PARTICIPANT:
            results = set()
            for event, participants in event_participants.items():
                results = results | set(participants)
            results = {None: results}
        if categorize == form.EVENT:
            # Seperate the events up (yes i know we merged them above).
            major = {}
            minor = {}
            no_event = []
            for event, participants in event_participants.items():
                if event is None:
                    no_event += participants
                elif event.is_prep:
                    minor[event] = participants
                else:
                    major[event] = participants

            results = collections.OrderedDict((
                (_("Major"), major),
                (_("Minor"), minor),
                (_("No Event"), no_event),
            ))

        # Remove any without participants
        # results = self._remove_empty_values(results)

        # Build the counts
        major_event_count = None
        prep_event_count = None
        institution_count = None
        result_count = None
        participant_count = None
        if categorize == form.PARTICIPANT:
            participant_count = len(results[None])
            result_count = participant_count
        
        if categorize == form.EVENT:
            prep_event_count = len(self._nested_search(
                results,
                lambda o: isinstance(o, models.Event) and o.is_prep
            ))
            major_event_count = len(self._nested_search(
                results,
                lambda o: isinstance(o, models.Event) and not o.is_prep
            ))
            result_count = len(self._nested_search(
                results,
                lambda o: isinstance(o, models.Event)
            ))
        elif categorize == form.INSTITUTION:
            institution_count = len(self._nested_search(
                results,
                lambda i: isinstance(i, models.Institution)
            ))

        # Return the response.
        return TemplateResponse(
            request,
            self.search_template,
            {
                "form": form,
                "advanced": True,
                "search_results": results,
                "major_event_count": major_event_count,
                "prep_event_count": prep_event_count,
                "institution_count": institution_count,
                "participant_count": participant_count,
                "result_count": result_count
            }
        )


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
                if  obj.archived:
                    continue
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
             CheckField("location", null=True, empty_string=True)],
            _gen_change_uri_func("admin:streetcrm_event_change"))

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
            _gen_change_uri_func("admin:streetcrm_participant_change"))

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
            _gen_change_uri_func("admin:streetcrm_institution_change"))

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


class LeaderGrowthInline(admin.TabularInline):
    model =  models.LeadershipGrowth
    extra = 1
    template = "admin/leader_stage_inline_tabular.html"    
    verbose_name = "leader stage"
    verbose_name_plural = "Leader Stages"
    readonly_fields = ("date_reached", )
    
class ParticipantAdmin(mixins.AdminArchiveMixin, mixins.SignInSheetAdminMixin, SearchAdmin):
    """ Admin UI for participant including listing event history """
    search_fields = ("name", "primary_phone", "title", "email",
                     "participant_street_address",
                     "participant_city_address",
                     "participant_state_address",
                     "participant_zipcode_address")
    list_filter = (admin_filters.ArchivedFilter,)
    list_display = ("name", "US_primary_phone", "institution", "participant_street_address", "participant_city_address",)
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

    inlines = [LeaderGrowthInline,]

    def get_fieldsets(self, request, obj=None):
        if obj:
            return self.change_fieldsets
        return super(ParticipantAdmin, self).get_fieldsets(request, obj)
    change_form_template = "admin/change_participant_form.html"
    form = st_forms.ParticipantForm
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
        if obj.primary_phone is None or obj.primary_phone == "":
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

class AjaxyInlineAdmin(SearchAdmin):
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
    list_filter = (admin_filters.TagFilter,)
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
            "/streetcrm/participant/", "<inlined_model_id>", "/"],
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
            ["streetcrm.change_event", "streetcrm.change_participant",
             "streetcrm.change_contact", "streetcrm.change_institution",
             "streetcrm.add_event", "streetcrm.add_participant",
             "streetcrm.add_contact", "streetcrm.add_institution"])


class InstitutionAdmin(mixins.AdminArchiveMixin, AjaxyInlineAdmin):
    search_fields = ("name",)
    search_filter = ("name", "inst_street_address", "inst_city_address", "inst_state_address"
                     "inst_zipcode_address")
    list_filter = (admin_filters.ArchivedFilter, admin_filters.TagFilter,)
    list_display = ("name", )
    change_form_template = "admin/ajax_inline_change_form.html"
    form = st_forms.autocomplete_modelform_factory(
        model=models.Institution,
        exclude=("archived", "contacts",),
        form=st_forms.TagSkippingAutoCompleteModelForm,
    )
    actions = None
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
            "/streetcrm/participant/", "<inlined_model_id>", "/"],
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
            ["streetcrm.change_participant",
             "streetcrm.change_contact", "streetcrm.change_institution,"
             "streetcrm.add_participant",
             "streetcrm.add_contact", "streetcrm.add_institution"])


class TagAdmin(mixins.AdminArchiveMixin, SearchAdmin):
    search_fields = ("name",)
    list_filter = (admin_filters.ArchivedFilter,)
    list_display = ("name", "description",)
    actions = None
    readonly_fields = ("date_created",)
    form = st_forms.TagAdminForm
    change_form_template = "admin/change_tag_form.html"
    exclude = ("archived",)

    def __init__(self,*args,**kwargs):
        super(TagAdmin, self).__init__(*args, **kwargs)
        main.EMPTY_CHANGELIST_VALUE = ''

class LogAdmin(admin.ModelAdmin):
    actions = None
    readonly_fields = ("user", "content_type", "object_id", "object_repr", "action_flag",)
    list_display = ("object_repr", "change_message", "user", "action_time",)
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

class UserAdmin(auth.admin.UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (_("Permissions"), {"fields": ("is_active", "is_superuser", "groups",
                                       "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    list_display = ("username", "email", "first_name", "last_name")
    list_filter = (admin_filters.GroupFilter,)
    actions = None
    filter_horizontal = tuple()
    filter_vertical = ('groups', 'user_permissions',)

class GroupAdmin(auth.admin.GroupAdmin):
    filter_horizontal = tuple()
    filter_vertical = ('permissions',)
    actions = None

class LeaderStageAdmin(admin.ModelAdmin):
    actions = None

# Create the admin site
site = STREETCRMAdminSite()

# Register auth AdminModels
site.register(auth.admin.Group, GroupAdmin)
site.register(auth.admin.User, UserAdmin)

# Register STREETCRM AdminModels
site.register(models.Participant, ParticipantAdmin)
site.register(models.Event, EventAdmin)
site.register(models.Institution, InstitutionAdmin)
site.register(models.Tag, TagAdmin)
site.register(models.ActivityLog, LogAdmin)
