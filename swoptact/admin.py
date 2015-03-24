from django import template
from django.contrib import admin, staticfiles
from django.template import loader
from swoptact.models import Address, Participant, Event

from django_google_maps import widgets as map_widgets
from django_google_maps import fields as mapfields

class ParticipantAdmin(admin.ModelAdmin):
    """ Admin UI for participant including listing event history """
    list_display = ("name", "phone_number", "address", "email",)
    readonly_fields = ("event_history", "event_history_name", )
    fieldsets = (
        (None, {
            "fields": ("first_name", "last_name", "phone_number", "email",
                        "address", "map_display")
        }),
        ("Personal Event History",   {
            "fields": ("event_history",),
        })
    )
    formfield_overrides = {
        mapfields.AddressField: {'widget': map_widgets.GoogleMapsAddressWidget},    
    }

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
    list_display = ("name", "site", "address", "date", "attendee_count",)
    filter_horizontal = ("participants",)
    formfield_overrides = {
        mapfields.AddressField: {'widget': map_widgets.GoogleMapsAddressWidget},    
    }



admin.site.register(Address)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Event, EventAdmin)
