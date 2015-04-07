from django import template
from django.contrib import admin, staticfiles
from django.template import loader
from django.conf.urls import patterns, url
from django.shortcuts import render_to_response

from django_google_maps import widgets as map_widgets
from django_google_maps import fields as mapfields

from swoptact.models import Address, Participant, Event, Institution

class SignInSheetAdminMixin(object):
    """ Provides a special case sign in sheet view

    This will be inherited by ParticipantAdmin and is only a seporate
    class to make it easier to think about. You should prefix your
    attributes and method names with "sheet_" to avoid conflict.
    """
    sheet_template = "admin/sign_in_sheet.html"

    def get_urls(self, *args, **kwargs):
        # Get the URLs of the superclass.
        urls = super(SignInSheetAdminMixin, self).get_urls(*args, **kwargs)

        # Define the sign in sheet URL
        sheet_view = self.admin_site.admin_view(self.sheet_view)
        sheet_url = patterns("",
            url(r"sign-in-sheet/$", sheet_view, name="sign-in-sheet"),
        )

        return sheet_url + urls


    def sheet_view(self, request):
        return render_to_response(self.sheet_template, {})

class ParticipantAdmin(SignInSheetAdminMixin, admin.ModelAdmin):
    """ Admin UI for participant including listing event history """
    list_display = ("name", "phone_number",  "institution", "address",)
    readonly_fields = ("event_history", "event_history_name", )
    fieldsets = (
        (None, {
            "fields": ("first_name", "last_name", "phone_number", "institution", "secondary_phone", "email",
                        "address")
        }),
        ("Personal Event History", {
            "fields": ("event_history",),
        })
    )

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

class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "date", "attendee_count",)

class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name", )

class AddressAdmin(admin.ModelAdmin):

    def get_model_perms(self, *args, **kwargs):
        """ Hide the address from the admin index """
        return {}

admin.site.register(Address, AddressAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Institution, InstitutionAdmin)
