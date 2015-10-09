
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from swoptact.models import Tag

class ArchiveFilter(SimpleListFilter):
    title = _("Archive Status")
    parameter_name = "archive_status"

    def lookups(self, request, model_admin):
        active_count = str(model_admin.model.objects.filter(archived__isnull=True).count())
        archived_count = str(model_admin.model.objects.exclude(archived__isnull=True).count())
        all_count = str(model_admin.model.objects.all().count())
        return (
            (None, _("Active" + " (" + active_count + ")")),
            ("archived", _("Archived"  + " (" + archived_count + ")")),
            ("all", _("All"  + " (" + all_count + ")")),
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


class TagFilter(SimpleListFilter):
    title = _("Tag")
    parameter_name = "tags__name"

    def lookups(self, request, model_admin):
        tag_set = Tag.objects.all().order_by("name")
        all_count = str(model_admin.model.objects.all().count())
        choices_set = [("all", _("All"  + " (" + all_count + ")")),]
        for name in tag_set:
            count = str(model_admin.model.objects.filter(tags__name=name).count())
            choices_set.append((name, _(str(name) + " (" + count + ")")))
        return choices_set
            
    def queryset(self, request, queryset):
        if not self.used_parameters:
            self.used_parameters = {'tags__name': 'all'}
        try:
            if self.used_parameters["tags__name"] == 'all':
                return queryset
            else:
                return queryset.filter(**self.used_parameters)
        except ValidationError as e:
            raise IncorrectLookupParameters(e)

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }
            
