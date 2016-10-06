from django.contrib import admin

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

    # raw_id_fields = ("type",)
    # list_filter = ('category__name',)
    # autocomplete_lookup_fields = {
    #     'fk': ['type'],
    # }


@admin.register(AnalyseType)
class AnalyseTypeAdmin(admin.ModelAdmin):
    list_filter = ('category__name',)
    search_fields = ('name',)


@admin.register(Analyse)
class AnalyseAdmin(admin.ModelAdmin):
    raw_id_fields = ("type",)
    search_fields = ('admission__id',)
    autocomplete_lookup_fields = {
        'fk': ['type'],
    }

    inlines = [
        ParameterValueInline,
    ]


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    search_fields = ('name', 'id', 'surname', 'tcno')

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
              ('week','upd_week', 'lmp_date'),
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
