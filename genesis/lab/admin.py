from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

# Register your models here.

from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from grappelli_autocomplete_fk_edit_link import AutocompleteEditLinkAdminMixin

from .models import *


class AnalyseInline(AutocompleteEditLinkAdminMixin, admin.TabularInline):
    model = Analyse
    classes = ('grp-collapse',)
    # autocomplete_lookup_fields = {
    #     'type_fk': ['type'],
    # }
    # show_change_link = True
    raw_id_fields = ("type",)
    readonly_fields = ('finished', )
    fields = ('type', 'finished')
    # list_filter = ('category__name',)
    autocomplete_lookup_fields = {
        'fk': ['type'],
    }


class ParameterValueInline(admin.TabularInline):
    model = ParameterValue
    extra = 0
    readonly_fields = ('key', 'code')
    max_num = 0
    fields = ('key', 'code', 'value')


class StateInline(admin.TabularInline):
    model = State
    extra = 1

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):

        field = super().formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == 'definition':
            if request._obj_ is not None:
                field.queryset = field.queryset.filter(id__in=request._obj_.applicable_states_ids())
            else:
                field.queryset = field.queryset.none()

        return field


class ParameterKeyInline(admin.TabularInline):
    model = ParameterKey
    extra = 0
    classes = ('grp-collapse grp-closed',)

class AdmissionSampleInline(admin.TabularInline):
    model = AdmissionSample
    extra = 1
    classes = ('grp-collapse',)


@admin.register(AnalyseType)
class AnalyseTypeAdmin(admin.ModelAdmin):
    list_filter = ('category',)
    search_fields = ('name',)
    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'method', 'sample_type', 'code', 'process_time', 'price')
        }),
        (_('Advanced'),
         {'classes': ('grp-collapse', 'grp-closed'),
          'fields': ('process_logic', )
          })
    )


@admin.register(StateDefinition)
class AnalyseTypeAdmin(admin.ModelAdmin):
    list_filter = ('type',)
    search_fields = ('name',)
    filter_horizontal = ('type',)


@admin.register(Parameter)
class ParameterAdmin(admin.ModelAdmin):
    # list_filter = (,)
    # search_fields = (,)

    def save_model(self, request, obj, form, change):
        obj.save()
        if obj.parameter_definition.strip():
            obj.create_update_parameter_keys()

    filter_horizontal = ('analyze_type',)

    inlines = (ParameterKeyInline,)

    fieldsets = (
        (None, {
            'fields': ('name', 'type', 'analyze_type')
        }),
        (_('Quick parameter definition'), {
            'classes': ('grp-collapse',),  # grp-closed
            'fields': ('parameter_definition',),
        }),

    )


@admin.register(Analyse)
class AnalyseAdmin(admin.ModelAdmin):
    raw_id_fields = ("type",)
    date_hierarchy = 'timestamp'
    search_fields = ('admission__id', 'type__name')
    readonly_fields = ('id', )
    autocomplete_lookup_fields = {
        'fk': ['type'],
    }

    list_filter = ('finished', 'timestamp', 'type')
    list_display = ('type', 'admission',  'timestamp', 'finished')
    inlines = [
        StateInline, ParameterValueInline
    ]
    def save_model(self, request, obj, form, change):
        is_new = not bool(obj.id)
        if is_new:
            obj.create_empty_values()

    def save_related(self, request, form, formset, change):
        super().save_related(request, form, formset, change)
        obj = form.instance
        if obj.finished:
            obj.save_result()

    def get_form(self, request, obj=None, **kwargs):
        # just save obj reference for future processing in Inline
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)

    # def changelist_view(self, request, extra_context=None):
    #     if not request.META['QUERY_STRING'] and \
    #             not request.META.get('HTTP_REFERER', '').startswith(request.build_absolute_uri()):
    #         return HttpResponseRedirect(request.path + "?finished__exact=0")
    #     return super().changelist_view(request, extra_context=extra_context)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    search_fields = ('name', 'id', 'surname', 'tcno')


@admin.register(ReportTemplate)
class PatientAdmin(admin.ModelAdmin):
    class Media:
        js = [
            '/static/tinymce/tinymce.min.js',
            '/static/tinymce/setup.js',
        ]


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    search_fields = ('name', 'surname')

    def save_model(self, request, obj, form, change):
        if not obj.institution:
            # create a clinic record for doctors who doesn't
            #  belong to an institution
            ins = Institution(name="%s %s" % (obj.name, obj.surname), type=30)
            ins.save()
            obj.institution = ins
        obj.save()


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    search_fields = ('name', 'id', 'code')


@admin.register(Admission)
class AdmissionAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    raw_id_fields = ('patient', 'institution', 'doctor')
    fields = ('id', 'patient', ('institution', 'doctor'),
              ('week', 'upd_week', 'lmp_date'),
              ('indications', 'history'),
              )
    autocomplete_lookup_fields = {
        'fk': ['patient', 'institution', 'doctor'],
    }

    inlines = [
        AnalyseInline, AdmissionSampleInline
    ]


app_models = apps.get_app_config('lab').get_models()
for model in app_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
