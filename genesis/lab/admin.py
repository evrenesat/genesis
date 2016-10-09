from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

# Register your models here.

from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from .models import *


class AnalyseInline(admin.TabularInline):
    model = Analyse

    # autocomplete_lookup_fields = {
    #     'type_fk': ['type'],
    # }
    raw_id_fields = ("type",)
    # list_filter = ('category__name',)
    autocomplete_lookup_fields = {
        'fk': ['type'],
    }


class ParameterValueInline(admin.TabularInline):
    model = ParameterValue


class StateInline(admin.TabularInline):
    model = State


class ParameterKeyInline(admin.TabularInline):
    model = ParameterKey
    classes = ('grp-collapse grp-closed',)


@admin.register(AnalyseType)
class AnalyseTypeAdmin(admin.ModelAdmin):
    list_filter = ('category__name',)
    search_fields = ('name',)


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
            'classes': ('grp-collapse',), # grp-closed
            'fields': ('parameter_definition',),
        }),
        ('Edit result calculation logic', {
            'classes': ('grp-collapse grp-closed',),
            'fields': ('process_logic',),
        }),
    )


@admin.register(Analyse)
class AnalyseAdmin(admin.ModelAdmin):
    raw_id_fields = ("type",)
    search_fields = ('admission__id',)
    autocomplete_lookup_fields = {
        'fk': ['type'],
    }

    inlines = [
        StateInline, ParameterValueInline
    ]


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
            ins = Institution(name=obj.name, type=30)
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
        AnalyseInline,
    ]


app_models = apps.get_app_config('lab').get_models()
for model in app_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
