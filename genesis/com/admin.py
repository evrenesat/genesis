from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.db.models.signals import post_save
from django.dispatch import receiver
from grappelli_autocomplete_fk_edit_link import AutocompleteEditLinkAdminMixin

from .models import *
from lab.admin import AdmissionAdmin


@receiver(post_save, sender=Admission)
def create_payment_objects(sender, instance, created, raw, **kwargs):
    # if created and not raw:
    if not instance.admissionpricing_set.exists() and not raw:
        AdmissionPricing(admission=instance).save()


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ('type', 'method', 'amount', 'institution', 'patient')
    classes = ('grp-collapse',)


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    fields = ('name', 'amount', 'quantity', 'total')
    readonly_fields = ('name', 'amount', 'quantity', 'total')
    classes = ('grp-collapse', 'grp-closed')


class AdmissionPricingInline(admin.TabularInline):
    model = AdmissionPricing
    extra = 0
    max_num = 0
    fields = ('final_amount', 'list_price', 'discount_percentage', 'discount_amount')
    readonly_fields = ('list_price', 'discount_percentage', 'discount_amount')
    # readonly_fields = ('list_price', 'amount', 'quantity', 'total')
    classes = ('grp-collapse',)


AdmissionAdmin.inlines.extend([AdmissionPricingInline, PaymentInline, InvoiceItemInline])

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
