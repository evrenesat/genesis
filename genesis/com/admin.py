from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from grappelli_autocomplete_fk_edit_link import AutocompleteEditLinkAdminMixin

from .models import *



# class PaymentItemInline(admin.TabularInline):
#     model = PaymentItem
#     extra = 0
#     classes = ('grp-collapse', )
#
#
# @admin.register(Payment)
# class PaymentAdmin(AutocompleteEditLinkAdminMixin, admin.ModelAdmin):
#     date_hierarchy = 'timestamp'
#     # search_fields = ('patient__name', 'patient__tcno', 'patient__surname')
#     # list_display = ('patient', 'institution', 'analyse_state', 'timestamp')
#     # readonly_fields = ('id', 'timestamp')
#     # raw_id_fields = ('patient', 'institution', 'doctor')
#     # fields = (('id', 'timestamp'), ('patient', 'is_urgent'), ('doctor', 'institution'),
#     #           ('week', 'upd_week', 'lmp_date'),
#     #           ('indications', 'history'),
#     #           )
#     # autocomplete_lookup_fields = {
#     #     'fk': ['patient', 'institution', 'doctor'],
#     # }
#
#     inlines = [
#      PaymentItemInline
#     ]
#
#








app_models = apps.get_app_config('com').get_models()
for model in app_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
