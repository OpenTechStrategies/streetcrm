from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from swoptact.models import Tag
from django.contrib.auth.models import Group

class DropdownFilter(SimpleListFilter):
    template = 'admin/dropdown_filter.html'

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            selected = (str(self.value()) == str(lookup))
            yield {
                'selected': selected,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

class ArchivedFilter(DropdownFilter):
    title = _("")
    parameter_name = "archive_status"

    def lookups(self, request, model_admin):
        active_count = str(model_admin.model.objects.filter(archived__isnull=True).count())
        archived_count = str(model_admin.model.objects.exclude(archived__isnull=True).count())
        all_count = str(model_admin.model.objects.all().count())
        return (
            (None, _("Show only active" + " (" + active_count + ")")),
            ("archived", _("Show only archived"  + " (" + archived_count + ")")),
            ("all", _("Show all"  + " (" + all_count + ")")),
        )
    def queryset(self, request, queryset):
        if self.value() == None:
            return queryset.filter(archived__isnull=True)
        if self.value() == "archived":
            return queryset.exclude(archived__isnull=True)
        if self.value() == "all":
            return queryset




class TagFilter(DropdownFilter):
    title = _("tag")
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

class GroupFilter(DropdownFilter):
    title = _("Group")
    parameter_name = "groups__name"

    def lookups(self, request, model_admin):
        tag_set = Group.objects.all().order_by("name")
        all_count = str(model_admin.model.objects.all().count())
        choices_set = [("all", _("All"  + " (" + all_count + ")")),]
        for name in tag_set:
            count = str(model_admin.model.objects.filter(groups__name=name).count())
            choices_set.append((name, _(str(name) + " (" + count + ")")))
        return choices_set
            
    def queryset(self, request, queryset):
        if not self.used_parameters:
            self.used_parameters = {'groups__name': 'all'}
        try:
            if self.used_parameters["groups__name"] == 'all':
                return queryset
            else:
                return queryset.filter(**self.used_parameters)
        except ValidationError as e:
            raise IncorrectLookupParameters(e)

