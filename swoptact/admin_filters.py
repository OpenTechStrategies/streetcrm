
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _

class ArchiveFilter(SimpleListFilter):
    title = _("Archive Status")
    parameter_name = "archive_status"

    def lookups(self, request, model_admin):
        return (
            (None, _("Active")),
            ("archived", _("Archived")),
            ("all", _("All")),
        )

    def queryset(self, request, queryset):
        if self.value() == None:
            return queryset.filter(archived__isnull=True)
        if self.value() == "archived":
            return queryset.exclude(archived__isnull=True)
        if self.value() == "all":
            return queryset

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }
