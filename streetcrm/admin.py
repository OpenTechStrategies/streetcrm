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
from datetime import datetime

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

from django.db.models import Q, Count
from django.db.models.functions import Lower
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from watson import search as watson
from watson import admin as watson_admin
from watson.admin import SearchAdmin

import autocomplete_light

from streetcrm import forms as st_forms
from streetcrm import mixins, models, admin_filters

from django import http
import csv


class STREETCRMAdminSite(admin.AdminSite):

    login_form = st_forms.AdminLoginForm
    search_engine = watson_admin.admin_search_engine
    search_template = "admin/search.html"
    advanced_search_template = "admin/advanced_search.html"

    # Thanks to
    # http://stackoverflow.com/questions/11225163/how-to-change-dynamically-site-administration-string-in-djangos-admin
    # for explaining how to change the title on the admin index page.
    def index(self, *args, **kwargs):
        return admin.site.__class__.index(self, extra_context={'title':''}, *args, **kwargs)
    admin.site.index = index.__get__(admin.site, admin.site.__class__)
    
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
        urls.append(
            url(r"^search/export$", wrap(self.export_search), name="export"),
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

        if request.method == "GET" and not advanced:
            search_query = request.GET.get("q")
        else:
            search_query = None

        # If it's a GET request or the form is invalid, return now.
        if request.method == "GET" or not form.is_valid():
            # Show results from basic search, but still show the
            # advanced form when requested
            
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

        # if it's an export, do that
        if request.POST.get("export_btn"):
            return self.export_search(request, form, advanced, search_query)
        
        # If it's advanced send it that view, else send it to the basic view
        if advanced:
            return self.advanced_search_view(request, form)
        else:
            return self.basic_search_view(request, form)

    def log_basic_search(self, request, search_query):
        # save the search:
        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=None,
            object_id=None,
            object_repr=search_query,
            action_flag=SEARCH,
            change_message="Basic search.")
        return;

    def basic_search_do(self, request, search_query):
        """
        Return results from a basic search
        """
        # Perform the search, whether passed from header or the basic
        # form

        results = self.search_engine.search(search_query)

        # Alphabetize basic search results by name (no matter what their
        # object type: Participant, Event, or Institution)
        results = results.order_by('title')

        # Process the results into their objects
        results = [result.object for result in results]
        
        return results

    def basic_search_view(self, request, form, search_query=None):
        """
        Produce view for the basic search
        """

        if not search_query:
            search_query = form.cleaned_data["query"]
        else:
            # Set the form query input to be equal to the search query, for
            # more reliable export
            form.fields['query'].initial = search_query

        results = self.basic_search_do(request, search_query)
        self.log_basic_search(request, search_query)

        # Display the results
        return TemplateResponse(
            request,
            self.search_template,
            {
                "search_results": results,
                "form": form,
                "query": search_query,
            }
        )

    def advanced_search_counts(self, results, form):
        """
        Returns counts of different result types for advanced search.
        """
        data = form.get_processed_data()
        categorize = data["search_for"]

        major_event_count = None
        prep_event_count = None
        institution_count = None
        result_count = None
        participant_count = None
        unique_participant_count = None
        if categorize == form.PARTICIPANT:
            participant_count = len(results)
            result_count = participant_count
        
        if categorize == form.EVENT:
            prep_event_count = len([
                o for o in results if isinstance(o, models.Event) and o.is_prep
            ])
            major_event_count = len([
                o for o in results if isinstance(o, models.Event) and not o.is_prep
            ])
            result_count = len([
                o for o in results if isinstance(o, models.Event)
            ])
            unique_participant_count = len({
                p.id for event in results for p in event.participants.all() if isinstance(event, models.Event)
            })
        elif categorize == form.INSTITUTION:
            institution_count = len(self._nested_search(
                results,
                lambda i: isinstance(i, models.Institution)
            ))

        count_set = {
            "major_event_count": major_event_count,
            "prep_event_count": prep_event_count,
            "institution_count": institution_count,
            "participant_count": participant_count,
            "unique_participant_count": unique_participant_count,
            "result_count": result_count
        }
        return count_set

    def advanced_search_do(self, request, form, export):
        """
        This provides advanced searching options by parsing the processed form 
        into kwargs for a Django queryset
        """
        data = form.get_processed_data()
        categorize = data["search_for"]
        # Creating query dict to be passed as kwargs in queryset
        query_dict = {}
        
        # Check each relevant form field depending on the search model, and 
        # convert each into the syntax required for the queryset
        if categorize == form.PARTICIPANT:
            if isinstance(data["institution"], str):
                query_dict["institution__name__icontains"] = data["institution"]
            elif isinstance(data["institution"], models.Institution):
                query_dict["institution"] = data["institution"]

            if data.get("institution_tags"):
                query_dict["institution__tags"] = data["institution_tags"]

            if isinstance(data["leader_stage"], models.LeaderStage):
                query_dict["leadership"] = data["leader_stage"]

            if isinstance(data["event"], str):
                query_dict["event__name__icontains"] = data["event"]
            elif isinstance(data["event"], models.Event):
                query_dict["event"] = data["event"]

            if isinstance(data["event_organizer"], str):
                query_dict["event__organizer__name__icontains"] = data["event_organizer"]
            elif isinstance(data["event_organizer"], models.Participant):
                query_dict["event__organizer"] = data["event_organizer"]

            if data.get("event_tags"):
                query_dict["event__tags"] = data["event_tags"]

            if data.get("start_date"):
                query_dict["event__date__gte"] = data["start_date"]
            if data.get("end_date"):
                query_dict["event__date__lte"] = data["end_date"]

            results = models.Participant.objects.annotate(
                    event_count=Count("event")
                ).filter(**query_dict
                ).select_related("institution").prefetch_related(
                    "event_set", "institution__tags", "tracked_growth", "tracked_growth__stage"
                ).order_by(Lower("name"))

            if data.get("event_count"):
                results = results.filter(event_count__gte=data.get("event_count"))
        elif categorize == form.EVENT:
            if isinstance(data["participant"], str):
                query_dict["participants__name__icontains"] = data["participant"]
            elif isinstance(data["participant"], models.Participant):
                query_dict["participants"] = data["participant"]

            if isinstance(data["event_organizer"], str):
                query_dict["organizer__name__icontains"] = data["event_organizer"]
            elif isinstance(data["event_organizer"], models.Participant):
                query_dict["organizer"] = data["event_organizer"]

            if isinstance(data["connected_action"], str):
                query_dict["major_action__name__icontains"] = data["connected_action"]
            elif isinstance(data["connected_action"], models.Event):
                query_dict["major_action"] = data["connected_action"]

            if data.get("event_tags"):
                query_dict["tags"] = data["event_tags"]

            if data.get("start_date"):
                query_dict["date__gte"] = data["start_date"]
            if data.get("end_date"):
                query_dict["date__lte"] = data["end_date"]

            results = models.Event.objects.filter(**query_dict
                ).select_related("organizer", "secondary_organizer"
                ).prefetch_related("participants"
                ).order_by(Lower("name"))

        # If this is not an export, get counts:
        if not export:
            count_set = self.advanced_search_counts(results, form)
            results_package = {"form": form,
                               "search_results": results,
                               "major_event_count": count_set['major_event_count'],
                               "prep_event_count": count_set['prep_event_count'],
                               "institution_count": count_set['institution_count'],
                               "participant_count": count_set['participant_count'],
                               "unique_participant_count": count_set['unique_participant_count'],
                               "result_count": count_set['result_count']
            }
        else:
            search_params = []
            for key, value in data.items():
                if isinstance(value, datetime):
                    search_params.append('{} = {}'.format(key, value.strftime('%Y-%m-%d')))
                elif isinstance(value, str) and len(value):
                    search_params.append('{} = {}'.format(key, value))
                elif isinstance(value, bool) and value:
                    search_params.append(key)
                elif hasattr(value, '__iter__') and len(value):
                    search_params.append('{} = {}'.format(key, ','.join([str(v) for v in value])))
                elif hasattr(value, 'pk'):
                    search_params.append('{} = {}'.format(key, str(value)))

            search_header = ', '.join(search_params)

            results_package = {"form": form,
                               "search_results": results,
                               "search_header": search_header
            }

        return results_package

    def advanced_search_view(self, request, form):
        """
        Return template for advanced search results.
        """

        adv_results = self.advanced_search_do(request, form, export=False)
        
        # Return the response.
        return TemplateResponse(
            request,
            self.search_template,
            {
                "form": adv_results['form'],
                "advanced": True,
                "search_results": adv_results['search_results'],
                "major_event_count": adv_results['major_event_count'],
                "prep_event_count": adv_results['prep_event_count'],
                "institution_count": adv_results['institution_count'],
                "participant_count": adv_results['participant_count'],
                "unique_participant_count": adv_results['unique_participant_count'],
                "result_count": adv_results['result_count']
            }
        )
    
    @staticmethod
    def export_search(request, form, advanced, search_query):
        """
        Export the set of search results in a CSV.
        """
        # Start CSV
        response = http.HttpResponse(content_type='text/csv')
        filetime = datetime.now()
        filename="search-results-" + str(filetime.year) + "-" + str(filetime.month) + "-" + str(filetime.day) + "-" + str(filetime.hour) + str(filetime.minute) + str(filetime.second) + ".csv"
        response['Content-Disposition'] = 'attachment; filename='+filename
        writer = csv.writer(response)

        if not search_query:
            search_query = form.cleaned_data["query"]

        if advanced:
            results_package = STREETCRMAdminSite.advanced_search_do(STREETCRMAdminSite, request, form, export=True)
            search_results = results_package["search_results"]
            search_header = results_package["search_header"]
        else:
            search_results = STREETCRMAdminSite.basic_search_do(STREETCRMAdminSite, request, search_query)
            search_header = search_query

        # Special columns include: institution_id, organizer_id, and
        # major_action_id.  These should all display the name of the
        # related object, not its id.
        participant_header=[
            {"column": "id", "heading": "ID"},
            {"column": "name", "heading": "Participant name"},
            {"column": "primary_phone", "heading": "Phone number"},
            {"column": "email", "heading": "Email address"},
            {"column": "participant_street_address", "heading":
            "Address"},
            {"column": "institution_id", "heading": "Institution"},
            {"column": "leadership", "heading": "Leadership level"},
            {"column": "event_count", "heading": "Count attendances"}
        ]
        institution_header=[
            {"column": "id", "heading": "ID"},
            {"column": "name", "heading": "Institution name"},
            {"column": "inst_street_address", "heading": "Address"},
            {"column": "is_member", "heading": "Is a member institution?"}
        ]
        event_header=[
            {"column": "id", "heading": "ID"},
            {"column": "name", "heading": "Action name"},
            {"column": "description", "heading": "Description"},
            {"column": "date", "heading": "Date"},
            {"column": "organizer_id", "heading": "Organizer"},
            {"column": "location", "heading": "Location"},
            {"column": "narrative", "heading": "Narrative"},
            {"column": "major_action_id", "heading": "Major action"},
            {"column": "attendance_count", "heading": "Count attendances"}
        ]
        
        last_header=[]
        header=[]
        
        search_title = [
            'Exported on {}'.format(filetime.strftime('%Y-%m-%d')),
            'Search terms: {}'.format(search_header)
        ]
        writer.writerow(search_title)
        
        for result in search_results:
            if result is None:
                continue
            # Convert the result object (participant, institution, etc.)
            # to a row.

            # intended behavior: each model type is grouped together
            # under one header row.  This header row matches the columns
            # of data that are displayed.  Eventually, this will be
            # user-editable.
            
            # The objects are already arranged by type.  So, check type
            # and if it isn't the same insert the new header row.
            last_header=header
            if result._meta.model_name == 'participant':
                header=participant_header
            elif result._meta.model_name == 'institution':
                header=institution_header
            elif result._meta.model_name == 'event':
                header=event_header


            if header != last_header:
                heading_list=[]
                for col in header:
                    heading_list.append(col['heading'])
                writer.writerow([])
                writer.writerow(heading_list)
                
            new_row = []
            for col in header:
                # Display names of related objects, not IDs
                if col['column'] == 'institution_id' and result.__dict__[col['column']] != None:
                    this_inst = models.Institution.objects.get(id=result.__dict__[col['column']])
                    new_row.append(this_inst.name)
                elif col['column'] == 'organizer_id' and result.__dict__[col['column']] != None:
                    this_organizer = models.Participant.objects.get(id=result.__dict__[col['column']])
                    new_row.append(this_organizer.name)
                elif col['column'] == 'major_action_id' and result.__dict__[col['column']] != None:
                    this_action = models.Event.objects.get(id=result.__dict__[col['column']])
                    new_row.append(this_action.name)
                elif col['column'] == 'leadership':
                    # If there are any leadership stages, convert them to a list so that the database
                    # isn't queried again and pull the most recent
                    if result.tracked_growth.all():
                        stages = sorted([growth for growth in result.tracked_growth.all()], key=lambda g: g.date_reached)
                        new_row.append(stages[-1].stage.name)
                elif col['column'] == 'attendance_count':
                    new_row.append(result.participants.all().count())
                else:
                    new_row.append(result.__dict__[col['column']])
            writer.writerow(new_row)

        return response

    
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
    ordering = ("-date", )
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
        "popup_fields": [
            {"field_name": "name",
             "descriptive_name": "Participant Name"},
            {"field_name": "primary_phone",
             "descriptive_name": "Participant Phone"},
            {"field_name": "institution.name",
             "descriptive_name": "Institution"},
            {"field_name": "title",
             "descriptive_name": "Participant's Title"},
            {"field_name": "secondary_phone",
             "descriptive_name": "Secondary Participant Phone"},
            {"field_name": "email",
             "descriptive_name": "Participant Email"},
            {"field_name": "participant_street_address",
             "descriptive_name": "Participant Street Address"},
            {"field_name": "participant_city_address",
             "descriptive_name": "City"},
            {"field_name": "participant_state_address",
             "descriptive_name": "State"},
            {"field_name": "participant_zipcode_address",
             "descriptive_name": "Participant Zip Code"}
        ],
        "fields": [
            {"descriptive_name": "Name",
             "form_name": "name",
             "input_type": "text"},
            {"descriptive_name": "Institution",
             "form_name": "institution",
             "input_type": "fkey_autocomplete_name",
             "autocomplete_uri": "/autocomplete/InstitutionAutocomplete/"},
            {"descriptive_name": "Phone Number",
             "form_name": "primary_phone",
             "input_type": "text"},
            {"descriptive_name": "Email",
             "form_name": "email",
             "input_type": "text"}
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
    list_filter = (admin_filters.ArchivedFilter, admin_filters.TagFilter,)
    list_display = ("name", )
    ordering = ("name", )
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
