import autocomplete_light

from swoptact import models

class BaseAutocomplete(autocomplete_light.AutocompleteModelBase):
    attrs = {
        "placeholder": "",
        "data-autocomplete-minimum-characters": 1,
    }


# Register the Address
class AddressAutocomplete(BaseAutocomplete):
    search_fields = ["name"]
    model = models.Address

autocomplete_light.register(AddressAutocomplete)

# Register the Institution
class InstitutionAutocomplete(BaseAutocomplete):
    search_fields = ["name"]
    model = models.Institution

autocomplete_light.register(InstitutionAutocomplete)