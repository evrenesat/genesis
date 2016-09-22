from django.contrib import admin

# Register your models here.

from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

from .models import Analyse, PatientAdmission, AnalyseType


class AnalyseInline(admin.TabularInline):
    model = Analyse

    # autocomplete_lookup_fields = {
    #     'type_fk': ['type'],
    # }
    raw_id_fields = ("type",)
    list_filter = ('group__name',)
    autocomplete_lookup_fields = {
        'fk': ['type'],
    }


@admin.register(AnalyseType)
class AnalyseTypeAdmin(admin.ModelAdmin):
    list_filter = ('group__name',)
    search_fields = ('name', )

@admin.register(Analyse)
class AnalyseAdmin(admin.ModelAdmin):
    raw_id_fields = ("type",)
    search_fields = ('name',)
    autocomplete_lookup_fields = {
        'fk': ['type'],
    }



# class AnalyseTypeAdmin(admin.ModelAdmin):
#     autocomplete_lookup_fields = {
#         'fk': ['type'],
#     }

@admin.register(PatientAdmission)
class PatientAdmissionAdmin(admin.ModelAdmin):
    inlines = [
        AnalyseInline,
    ]


app_models = apps.get_app_config('lab').get_models()
for model in app_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
