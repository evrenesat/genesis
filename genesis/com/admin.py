from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.db.models.signals import post_save
from django.dispatch import receiver
from grappelli_autocomplete_fk_edit_link import AutocompleteEditLinkAdminMixin

from .models import *
from lab.admin import AdminAdmission, post_admission_save


@receiver(post_admission_save, sender=Admission)
def create_payment_objects(sender, instance, **kwargs):
    if not hasattr(instance, 'admissionpricing'):
        AdmissionPricing(admission=instance).save()
    instance.analyse_set.filter(group_relation='GRP').delete()



class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ('type', 'method', 'amount', 'institution', 'patient')
    classes = ('grp-collapse',)


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    max_num = 0
    fields = ('name', 'amount', 'quantity', 'total')
    readonly_fields = ('name', 'amount', 'quantity', 'total')
    classes = ('grp-collapse', 'grp-closed')


class AdmissionPricingInline(admin.TabularInline):
    model = AdmissionPricing
    extra = 0
    max_num = 0
    fields = ('tax_included', 'final_amount', 'list_price', 'discount_percentage', 'discount_amount')
    readonly_fields = ('list_price', 'discount_percentage', 'discount_amount')
    # readonly_fields = ('list_price', 'amount', 'quantity', 'total')
    classes = ('grp-collapse',)


AdminAdmission.inlines.extend([AdmissionPricingInline, PaymentInline, InvoiceItemInline])



class InvoiceItemFullInline(admin.TabularInline):
    model = InvoiceItem
    # extra = 0
    # max_num = 0
    fields = ('name', 'amount', 'quantity', 'total')
    # readonly_fields = ('name', 'amount', 'quantity', 'total')
    # classes = ('grp-collapse', 'grp-closed')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    # list_filter = ('group_type', 'category',)
    search_fields = ('name','patient__name', 'patient__surname', 'institution__name')
    list_display = ('name', 'amount', 'total', 'timestamp')
    inlines = [InvoiceItemFullInline, ]
    fields = ('id', 'name', 'address', 'amount', 'tax', 'total')
    readonly_fields = ('id', )









app_models = apps.get_app_config('com').get_models()
for model in app_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
