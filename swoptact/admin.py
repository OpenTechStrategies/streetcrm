from django.contrib import admin, staticfiles
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
        # Table contents
        table = []

        # Add the headers
        table.append('<table class="table table-bordered">')
        table.append("<tr>")
        table.append("<th>Event</td>")
        table.append("<th>Date</td>")
        table.append("</tr>")

        # Add the data
        for event in obj.events:
            table.append("<tr>")
            table.append("<td><a href = '../../event/{id}/'>{name}</a></td>".format(name=event.name, id=Event.id(event)))
            table.append("<td>{date}</td>".format(date=event.date))
            table.append("</tr>")

        # And the closing tags
        table.append("</table>")
        return "".join(table)




admin.site.register(Address)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(Event)
