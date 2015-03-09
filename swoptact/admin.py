from django import template
from django.contrib import admin, staticfiles
from django.template import loader
from swoptact.models import Address, Participant, Event

class ParticipantAdmin(admin.ModelAdmin):
    """ Admin UI for participant including listing event history """
    list_display = ("name", "email", "phone_number")
    readonly_fields = ("event_history",)
    fieldsets = (
        (None, {
            "fields": ("first_name", "last_name", "phone_number", "email",
                        "address")
        }),
        ("Events", {
            "fields": ("event_history",),
        })
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




admin.site.register(Address)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Event)
