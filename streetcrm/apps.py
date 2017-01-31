from django.apps import AppConfig
from watson import search as watson

class StreetCRMConfig(AppConfig):
    name = 'StreetCRM'
    

    def ready(self):
        Institution = self.get_model("Institution")
        watson.register(Institution, fields=("name",))
        watson.register(Participant, fields=("name", "primary_phone",
                                             "title", "email", "participant_street_address",
                                             "participant_city_address",
                                             "participant_state_address",
                                             "participant_zipcode_address"))
        watson.register(Event, fields=("name", "location",))
        watson.register(Tag, fields=("name",))
