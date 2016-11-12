from datetime import datetime

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.forms import BaseInlineFormSet
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _

# Register your models here.

from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from grappelli_autocomplete_fk_edit_link import AutocompleteEditLinkAdminMixin

from .models import *
from com.models import *

from django.contrib.auth.admin import UserAdmin

from django.contrib.auth.models import Permission

admin.site.register(Permission)

UserAdmin.add_fieldsets = (
    (None, {
        'classes': ('wide',),
        'fields': ('username', 'password1', 'password2', 'first_name', 'last_name')}
     ),
)


class ParameterValueInline(admin.TabularInline):
    classes = ('grp-collapse grp-closed',)
    model = ParameterValue
    extra = 0
    ordering = ('code',)
    readonly_fields = ('key', 'code')
    max_num = 0
    fields = ('key', 'value', 'code')

    def has_add_permission(self, request, obj=None):
        return False


class ParameterKeyInline(admin.TabularInline):
    model = ParameterKey
    extra = 0
    classes = ('grp-collapse grp-closed',)


class AdmissionSampleInline(admin.TabularInline):
    model = AdmissionSample
    extra = 1
    classes = ('grp-collapse',)


class ParameterInline(admin.TabularInline):
    model = Parameter.analyze_type.through
    extra = 0
    classes = ('grp-collapse',)  # grp-closed


@admin.register(AnalyseType)
class AnalyseTypeAdmin(admin.ModelAdmin):
    list_filter = ('category',)
    search_fields = ('name',)
    list_display = ('name', 'group_type', 'price')
    filter_horizontal = ('subtypes',)
    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'method', 'sample_type',
                       'code', 'process_time', 'footnote', 'price', 'alternative_price')
        }),
        (_('Subtypes'),
         {'classes': ('grp-collapse', 'grp-closed'),
          'fields': ('subtypes',)
          }),
        (_('Advanced'),
         {'classes': ('grp-collapse', 'grp-closed'),
          'fields': ('process_logic',)
          })
    )
    inlines = [ParameterInline, ]

    def save_model(self, request, obj, form, change):
        obj.save()
        # if obj.parameter_definition.strip():
        #     obj.create_update_parameter_keys()


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


def _approve_analyse(state, request):
    if not request.user.has_perm('lab.can_approve_analysis'):
        raise ValidationError('-')  # PermissionDenied(
        # _("You don't have required permissions to mark an analyse as approved"))
    else:
        state.analyse.approved = True
        state.analyse.approve_time = datetime.now()
        state.analyse.approver = request.user.profile
        state.analyse.save()


def _finish_analyse(state, request):
    if not request.user.has_perm('lab.can_finish_analyse'):
        raise PermissionDenied(
            _("You don't have required permissions to  mark an analyse as finished"))
    else:
        state.analyse.finished = True
        state.analyse.completion_time = datetime.now()
        state.analyse.analyser = request.user.profile
        state.analyse.save()


class StateFormSet(BaseInlineFormSet):
    def save_new(self, form, commit=True):
        obj = super().save_new(form, commit=False)
        # here you can add anything you need from the request
        if obj.definition.finish:
            _finish_analyse(obj, self.request)
        if obj.definition.approve:
            _approve_analyse(obj, self.request)
        if commit:
            obj.save()

        return obj

        # def clean(self):
        #     super().clean()
        #     for form in self.forms:
        #         if not hasattr(form, 'cleaned_data'):
        #             continue
        #         if form.cleaned_data.get('DELETE'):
        #             raise ValidationError('Error')


class StateInline(admin.TabularInline):
    model = State
    extra = 1

    formset = StateFormSet

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.request = request
        return formset

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):

        field = super().formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == 'definition':
            if request._obj_ is not None:
                field.queryset = field.queryset.filter(id__in=request._obj_.applicable_states_ids())
            else:
                field.queryset = field.queryset.none()
        return field


@admin.register(Analyse)
class AnalyseAdmin(AutocompleteEditLinkAdminMixin, admin.ModelAdmin):
    raw_id_fields = ("type", 'admission')
    date_hierarchy = 'timestamp'
    search_fields = ('admission__id', 'type__name', 'admission__patient__name',
                     'admission__patient__tcno', 'admission__patient__surname')
    readonly_fields = (
        'id', 'approver', 'approved', 'approve_time', 'finished', 'analyser', 'completion_time')
    autocomplete_lookup_fields = {
        'fk': ['type', 'admission'],
    }
    fieldsets = ((None,
                  {'fields': ('id', 'type', 'admission', ('short_result', 'comment'),
                              ('sample_type', 'sample_amount',),
                              ('finished', 'analyser', 'completion_time'),
                              ('approved', 'approver', 'approve_time'),
                              )}),
                 (_('Advanced'),
                  {'classes': ('grp-collapse', 'grp-closed'),
                   'fields': ('result', 'template')
                   },
                  ))

    list_filter = ('finished', 'timestamp', 'type')
    list_display = ('type', 'admission', 'timestamp', 'finished', 'approved')
    inlines = [
        StateInline, ParameterValueInline
    ]

    def save_model(self, request, obj, form, change):
        # is_new = not bool(obj.id)
        # if is_new:
        obj.create_empty_values()
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formset, change):
        super().save_related(request, form, formset, change)
        obj = form.instance
        if obj.finished:
            obj.save_result()

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == "template":
            kwargs["queryset"] = request._obj_.type.reporttemplate_set.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

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
class ReportTemplateAdmin(admin.ModelAdmin):
    filter_horizontal = ('analyse_type',)
    save_as = True

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


class InstitutePricingInline(admin.TabularInline):
    model = InstitutePricing
    classes = ('grp-collapse',)


class AnalysePricingInline(admin.TabularInline):
    model = AnalysePricing
    classes = ('grp-collapse',)
    fields = ('analyse_type', 'price', 'discount_rate')


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    search_fields = ('name', 'id', 'code')
    inlines = [InstitutePricingInline, AnalysePricingInline]


class AnalyseInline(admin.TabularInline):
    model = Analyse
    classes = ('grp-collapse',)
    # autocomplete_lookup_fields = {
    #     'type_fk': ['type'],
    # }
    # show_change_link = True
    raw_id_fields = ("type",)
    readonly_fields = ('finished', 'approved')
    fields = ('finished', 'approved', 'type', 'sample_type')
    # list_filter = ('category__name',)
    autocomplete_lookup_fields = {
        'fk': ['type'],
    }

    def get_extra(self, request, obj=None, **kwargs):
        return 0 if obj else self.extra


class AdmissionStateInline(admin.TabularInline):
    model = AdmissionState
    extra = 1
    classes = ('grp-collapse',)


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ('type', 'method', 'amount', 'institution', 'patient')
    classes = ('grp-collapse',)


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    classes = ('grp-collapse', 'grp-closed')


class AdmissionPricingInline(admin.TabularInline):
    model = AdmissionPricing
    extra = 0
    max_num = 0
    classes = ('grp-collapse', )


@admin.register(Admission)
class AdmissionAdmin(AutocompleteEditLinkAdminMixin, admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    search_fields = ('patient__name', 'patient__tcno', 'patient__surname')
    list_display = ('patient', 'institution', 'analyse_state', 'timestamp')
    readonly_fields = ('id', 'timestamp')
    raw_id_fields = ('patient', 'institution', 'doctor')
    fields = (('id', 'timestamp'), ('patient', 'is_urgent'), ('doctor', 'institution'),
              ('week', 'upd_week', 'lmp_date'),
              ('indications', 'history'),
              )
    autocomplete_lookup_fields = {
        'fk': ['patient', 'institution', 'doctor'],
    }

    inlines = [
        AnalyseInline, AdmissionPricingInline, PaymentInline, InvoiceItemInline,  AdmissionSampleInline, AdmissionStateInline
    ]

    def get_form(self, request, obj=None, **kwargs):
        # just save obj reference for future processing in Inline
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.save()
        # if obj.parameter_definition.strip():
        #     obj.create_update_parameter_keys()

    def _create_payment_item(self):
        pass

    def _save_analyses(self, admission, analyses):
        for analyse in analyses:
            if analyse.type.group_type:
                for sub_analyse in analyse.type.subtype_set.all():
                    Analyse(type=sub_analyse,
                            sample_type=analyse.sample_type,
                            admission=admission).save()
            else:
                analyse.save()

    def save_related(self, request, form, formsets, change):
        """
        - expand group-type analyses
        - create payment and payment-items
        """
        form.save_m2m()
        if not change:
            adm = form.instance
            payment = Payment(admission=adm, patient=adm.patient)
            if adm.institution.preferred_payment_method == 20:
                payment.institution = adm.institution
            else:
                payment.patient = adm.patient
        for formset in formsets:
            if formset.model == Analyse:
                self._save_analyses(formset.instance, formset.save(commit=False))
            else:
                formset.save()



app_models = apps.get_app_config('lab').get_models()
for model in app_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
