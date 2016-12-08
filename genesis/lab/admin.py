from datetime import datetime

# import dbsettings
from functools import partial
from uuid import uuid4

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.dispatch import receiver
from django.forms import BaseInlineFormSet
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
import django.dispatch
# Register your models here.

from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django_ace import AceWidget
from grappelli_autocomplete_fk_edit_link import AutocompleteEditLinkAdminMixin

from .models import *
from com.models import *

from django.contrib.auth.admin import UserAdmin

from django.contrib.auth.models import Permission

#
# class AppConfig(dbsettings.Group):
#     barcode_printer = dbsettings.StringValue('Barcode printer')
#     report_printer = dbsettings.StringValue('Report printer')
#     invoice_printer = dbsettings.StringValue('Invoice printer')

# app_settings = AppConfig()

admin.site.register(Permission)

UserAdmin.add_fieldsets = (
    (None, {
        'classes': ('wide',),
        'fields': ('username', 'password1', 'password2', 'first_name', 'last_name')}
     ),
)
# admin.ModelAdmin.change_list_template = "admin/change_list_filter_sidebar.html"

def finish_selected_value(modeladmin, request, queryset):
    for value_item in queryset:
        value_item.analyse.mark_finished(request, True)


finish_selected_value.short_description = _("Mark selected analyses as Finished")


def approve_selected_value(modeladmin, request, queryset):
    for value_item in queryset:
        value_item.analyse.mark_approved(request, True)


approve_selected_value.short_description = _("Mark selected analyses as Approved")


def finish_selected(modeladmin, request, queryset):
    for analyse in queryset:
        analyse.mark_finished(request, True)


finish_selected.short_description = _("Mark selected analyses as Finished")


def approve_selected(modeladmin, request, queryset):
    for analyse in queryset:
        analyse.mark_approved(request, True)


approve_selected.short_description = _("Mark selected analyses as Approved")


@admin.register(ParameterValue)
class AdminParameterValue(admin.ModelAdmin):
    list_editable = ('value',)
    actions = [finish_selected_value, approve_selected_value]
    list_display = ('code', 'patient_name', 'analyse_name', 'key', 'value', 'analyse_state', 'keyid')
    search_fields = ('analyse__group_relation', 'analyse__type__name', 'analyse__admission__id')

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions



    def get_search_results(self, request, queryset, search_term):
        # integer search_term means we want to list values of a certain admission
        try:
            search_term_as_int = int(search_term)
            return ParameterValue.objects.filter(analyse__admission=search_term_as_int), False
        except ValueError:
            return super().get_search_results(request, queryset, search_term)

    def message_user(self, *args, **kwargs):
        super().message_user(*args, **kwargs)
        # this is a pure hack!
        # we are harnessing the fact that message_user will be called
        # for once after all objects are saved
        if hasattr(self, 'updated_analysis'):
            for analyse in self.updated_analysis[0].admission.analyse_set.all():
                analyse.save_result()

    def log_change(self, request, object, message):
        # by overriding log_change we can catch the changed objects
        # and accumulate their analyse ids
        if request.method == "POST" and '_save' in request.POST:
            if not hasattr(self, 'updated_analyses'):
                self.updated_analysis = []
            self.updated_analysis.append(object.analyse)
            super().log_change(request, object, message)

    def get_form(self, request, obj=None, **kwargs):
        kwargs['formfield_callback'] = partial(self.formfield_for_dbfield, request=request, obj=obj)
        return super().get_form(request, obj, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        kwargs['formfield_callback'] = partial(self.formfield_for_dbfield, request=request, obj=obj)
        return super().get_formset(request, obj, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        p_value = kwargs.pop('obj', None)
        if p_value and db_field.name == "value" and p_value.key.presets:
            db_field.choices = p_value.key.preset_choices()
        return super().formfield_for_dbfield(db_field, **kwargs)

    # def formfield_for_choice_field(self, db_field, request=None, **kwargs):
        # if db_field.name == "value":
        #     kwargs['choices'] = (
        #         ('accepted', 'Accepted'),
        #         ('denied', 'Denied'),
        #     )
        # return super().formfield_for_choice_field(db_field, request, **kwargs)


class ParameterValueInline(admin.TabularInline):
    classes = ('grp-collapse',)
    model = ParameterValue
    extra = 0
    ordering = ('code',)
    readonly_fields = ('key',  'keydata')
    max_num = 0
    fields = ('key', 'value', 'keydata')

    def has_add_permission(self, request, obj=None):
        return False

    def keydata(self, obj):
        return obj.keyid()
    keydata.allow_tags = True


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


class AnalyseTypeForm(forms.ModelForm):
    class Meta:
        model = AnalyseType
        widgets = {
            'process_logic': AceWidget(mode='python', theme='twilight', width="700px",
                                       height="400px"),
        }
        fields = '__all__'



@admin.register(AnalyseType)
class AdminAnalyseType(admin.ModelAdmin):
    form = AnalyseTypeForm
    list_filter = ('group_type', 'category',)
    search_fields = ('name',)
    list_display = ('name', 'code', 'group_type', 'category', 'method', 'price', 'external')
    list_editable = ('category', 'method', 'price', 'code')
    filter_horizontal = ('subtypes',)
    readonly_fields = ('group_type',)
    fieldsets = (
        (None, {
            'fields': ('group_type', 'name', 'category', 'method', 'sample_type',
                       'code', 'process_time', 'footnote', 'price','external_price', 'external',
                       'external_lab', 'alternative_price')
        }),
        (_('Subtypes'),
         {'classes': ('grp-collapse',),
          'fields': ('subtypes',)
          }),
        (_('Advanced'),
         {'classes': ('grp-collapse', 'grp-closed'),
          'fields': ('process_logic',)
          })
    )
    inlines = [ParameterInline, ]

    class Media:
        js = [
            '/static/tinymce/tinymce.min.js',
            '/static/tinymce/setup.js',
        ]

    def save_related(self, request, form, formset, change):
        super().save_related(request, form, formset, change)
        if form.instance.subtypes.exists() and not form.instance.group_type:
            form.instance.group_type = True
            form.instance.save()

            # if obj.parameter_definition.strip():
            #     obj.create_update_parameter_keys()


@admin.register(StateDefinition)
class AdminStateDefinition(admin.ModelAdmin):
    list_filter = ('type',)
    search_fields = ('name',)
    filter_horizontal = ('type',)


@admin.register(Parameter)
class AdminParameter(admin.ModelAdmin):
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


class StateFormSet(BaseInlineFormSet):
    def save_new(self, form, commit=True):
        obj = super().save_new(form, commit=False)
        # here you can add anything you need from the request
        if obj.definition.finish:
            obj.analyse.mark_finished(self.request)
        if obj.definition.approve:
            obj.analyse.mark_approved(self.request)
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


class AnalyseAdminForm(forms.ModelForm):
    class Meta:
        model = Analyse
        widgets = {
            'group_relation': forms.HiddenInput()
        }
        fields = '__all__'


class StateInline(admin.TabularInline):
    model = State
    extra = 1
    can_delete = False
    formset = StateFormSet
    fields = ('definition', 'comment', 'timestamp', 'updated_at')
    readonly_fields = ('timestamp', 'updated_at')
    ordering = ("-timestamp",)

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
class AdminAnalyse(admin.ModelAdmin):
    form = AnalyseAdminForm
    raw_id_fields = ("type", 'admission')
    actions = [finish_selected, approve_selected]
    date_hierarchy = 'timestamp'
    search_fields = ('admission__id', 'type__name', 'admission__patient__name',
                     'admission__patient__tcno', 'admission__patient__surname')
    readonly_fields = ('id', 'approver', 'approved', 'approve_time', 'finished', 'analyser',
        'completion_time', 'doctor_institution', 'patient', 'analyse_type')
    autocomplete_lookup_fields = {
        'fk': ['type', 'admission'],
    }
    fieldsets = (
        (_('Admission'),
         {'classes': ('grp-collapse',),
          'fields': (('analyse_type','doctor_institution', 'patient'), )
          },
         ),
        ("State Inline", {"classes": ("placeholder state_set-group",), "fields": ()}),
        (None,
                  {'fields': (('short_result', 'comment'),
                              ('sample_type', 'sample_amount',),
                              ('finished', 'analyser', 'completion_time'),
                              ('approved', 'approver', 'approve_time'),
                              )}),
                 (_('Advanced'),
                  {'classes': ('grp-collapse', 'grp-closed'),
                   'fields': ('result', 'template', 'group_relation','admission', 'type', 'external', 'external_lab')
                   },
                  ))

    list_filter = ('finished', 'timestamp', 'type')
    list_display = ('type', 'admission', 'timestamp', 'finished', 'approved')
    inlines = [
        StateInline, ParameterValueInline
    ]

    def get_search_results(self, request, queryset, search_term):
        # integer search_term means we want to list values of a certain record
        try:
            search_term_as_int = int(search_term)
            return Analyse.objects.filter(pk=search_term_as_int), False
        except ValueError:
            if len(search_term) == 32 and ' ' not in search_term:
                # checking if the search term is a hash or not,
                # a weak solution but should work for most cases
                return Analyse.objects.filter(group_relation=search_term), False
            return super().get_search_results(request, queryset, search_term)


    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


    def doctor_institution(self, obj):
        adm  = obj.admission
        return '%s / %s' % (adm.institution.name, adm.doctor.full_name() if adm.doctor else '')
    doctor_institution.short_description = _("Institution / Doctor")

    def patient(self, obj):
        return '<a href="/admin/lab/admission/%s/">%s - %s</a>' % (obj.admission.id,
                                                                   obj.admission.patient.full_name(30),
                                                                   obj.admission.timestamp)
    patient.short_description = _("Patient info")
    patient.allow_tags = True

    def analyse_type(self, obj):
        external = ' | %s:%s' % (_('Ext.Lab'), obj.external_lab) if obj.external else ''
        return '<span style="font-size:16px">#%s</span> / %s %s' % (obj.id, obj.type.name, external)
    analyse_type.short_description = _("Analyse")
    analyse_type.allow_tags = True

    def save_model(self, request, obj, form, change):
        # is_new = not bool(obj.id)
        # if is_new:
        obj.create_empty_values()
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formset, change):
        super().save_related(request, form, formset, change)
        form.instance.save_result()

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(group_relation='GRP')

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

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(group_relation='GRP')


class AdmissionStateInline(admin.TabularInline):
    model = AdmissionState
    extra = 1
    classes = ('grp-collapse',)


post_admission_save = django.dispatch.Signal(providing_args=["instance", ])


@admin.register(Admission)
class AdmissionAdmin(AutocompleteEditLinkAdminMixin, admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    search_fields = ('id', 'patient__name', 'patient__tcno', 'patient__surname')
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

    inlines = [AnalyseInline,  AdmissionStateInline]  # AdmissionSampleInline,

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

    def get_search_results(self, request, queryset, search_term):
        # integer search_term means we want to list values of a certain admission
        try:
            search_term_as_int = int(search_term)
            if len(search_term.strip()) < 7:
                return Admission.objects.filter(pk=search_term_as_int), False
        except ValueError:
            return super().get_search_results(request, queryset, search_term)


    def _save_analyses(self, admission, analyses):
        for analyse in analyses:
            if analyse.type.group_type:
                analyse.group_relation = 'GRP'  # this is a group
                rand_group_code = uuid4().hex
                for sub_analyse_type in analyse.type.subtypes.all():
                    Analyse(type=sub_analyse_type,
                            sample_type=analyse.sample_type,
                            group_relation=rand_group_code,
                            external=sub_analyse_type.external,
                            external_lab=sub_analyse_type.external_lab,
                            admission=admission).save()
            if analyse.type.external:
                analyse.external = analyse.type.external
                analyse.external_lab = analyse.type.external_lab
            analyse.save()
        post_admission_save.send(sender=Admission, instance=admission)

    def save_related(self, request, form, formsets, change):
        """
        - expand group-type analyses
        - create payment and payment-items
        """
        form.save_m2m()
        if not change:
            adm = form.instance
            # payment = Payment(admission=adm, patient=adm.patient)
            # if adm.institution.preferred_payment_method == 20:
            #     payment.institution = adm.institution
            # else:
            #     payment.patient = adm.patient
        for formset in formsets:
            if formset.model == Analyse:
                self._save_analyses(formset.instance, formset.save(commit=False))
            formset.save()



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code',)

@admin.register(Method)
class MethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'code',)

app_models = apps.get_app_config('lab').get_models()
for model in app_models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass


@receiver(post_admission_save, sender=Admission)
def create_payment_objects(sender, instance, **kwargs):
    # instance.analyse_set.filter(group_relation='GRP').delete()
    for analyse in instance.analyse_set.exclude(group_relation='GRP'):
        analyse.create_empty_values()


