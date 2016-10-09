from django import forms
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.
from .patient import Admission


class MediumType(models.Model):
    name = models.CharField(_('Name'), max_length=100, unique=True)
    code = models.CharField(_('Code'), max_length=3)

    class Meta:
        verbose_name = _('Medium Type')
        verbose_name_plural = _('Medium Types')

    def __str__(self):
        return self.name


class SampleType(models.Model):
    name = models.CharField(_('Name'), max_length=100, unique=True)
    code = models.CharField(_('Code'), max_length=3)
    amount = models.CharField(_('Amount'), max_length=20, null=True, blank=True)
    medium = models.ManyToManyField(MediumType, verbose_name=_('Medium Type'))

    class Meta:
        verbose_name = _('Sample Type')
        verbose_name_plural = _('Sample Types')

    def __str__(self):
        return self.name


class Method(models.Model):
    name = models.CharField(_('Name'), max_length=100, unique=True)
    code = models.CharField(_('Code'), max_length=5, null=True, blank=True)

    class Meta:
        verbose_name = _('Analyse Method')
        verbose_name_plural = _('Analyse Methods')

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(_('Name'), max_length=30, unique=True)
    code = models.CharField(_('Code'), max_length=5, null=True, blank=True)

    class Meta:
        verbose_name = _('Analyse Group')
        verbose_name_plural = _('Analyse Groups')

    def __str__(self):
        return self.name


class AnalyseType(models.Model):
    category = models.ForeignKey(Category, models.PROTECT, verbose_name=_('Group'))
    method = models.ForeignKey(Method, models.PROTECT, verbose_name=_('Method'))
    sample_type = models.ManyToManyField(SampleType, verbose_name=_('Sample Type'))
    name = models.CharField(_('Name'), max_length=100, unique=True)
    code = models.CharField(_('Code'), max_length=10, null=True, blank=True)
    price = models.DecimalField(_('Price'), max_digits=6, decimal_places=2)
    process_time = models.SmallIntegerField(_('Process Time'))

    class Meta:
        verbose_name = _('Analyse Type')
        verbose_name_plural = _('Analyse Types')

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)


class ReportTemplate(models.Model):
    analyse_type = models.ManyToManyField(AnalyseType, verbose_name=_('Analyse Type'))
    name = models.CharField(_('Name'), max_length=20, null=True, blank=True)
    template = models.TextField(_('Template'))

    # operator = models.ForeignKey(User, verbose_name=_('Operator'), editable=False)

    class Meta:
        verbose_name = _('Report Template')
        verbose_name_plural = _('Report Templates')

    def __str__(self):
        return "%s %s" % (self.patient, str(self.timestamp)[:19])


class StateDefinition(models.Model):
    type = models.ManyToManyField(AnalyseType, verbose_name=_('Analyse Type'))
    name = models.CharField(_('Name'), max_length=50)

    class Meta:
        verbose_name = _('Analyse State Definition')
        verbose_name_plural = _('Analyse State Definitions')

    def __str__(self):
        return self.name


class Analyse(models.Model):
    type = models.ForeignKey(AnalyseType, models.PROTECT, verbose_name=_('Analyse Type'))
    admission = models.ForeignKey(Admission, models.PROTECT, verbose_name=_('Patient Admission'))
    timestamp = models.DateTimeField(_('Definition date'), editable=False, auto_now_add=True)
    result = models.TextField(_('Analyse result'), blank=True, null=True    )


    class Meta:
        verbose_name = _('Analyse')
        verbose_name_plural = _('Analysis')

    def __str__(self):
        return "%s %s" % (self.type, self.admission)


class State(models.Model):
    analyse = models.ForeignKey(Analyse, models.PROTECT, verbose_name=_('Analyse'))
    definition = models.ForeignKey(StateDefinition, models.PROTECT, verbose_name=_('Analyse'))
    comment = models.CharField(_('Comment'), max_length=50)
    timestamp = models.DateTimeField(_('Timestamp'), editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(_('Update date'), editable=False, auto_now=True)

    class Meta:
        verbose_name = _('Analyse State')
        verbose_name_plural = _('Analyse States')

    def __str__(self):
        return self.type



PARAMETER_TYPES = (
    (1, _('Simple Key & Value')),
    (2, _('Tabular Key & Value')),
    (5, _('Boolean Matrix')),
    (10, _('String Matrix')),
    (15, _('Numeric Matrix')),
)
PARAM_DEF_HELP_TEXT = _("""
<hr />
<strong>Data Definition Help</strong><br />
Matrices:<br />
x = N/N, Mt/N, Mt/Mt<br />
y = Faktör V Leiden PCR, Faktör V HR2 PCR<br />
<hr />
Key/Values:<br />
key<br />
key2<br />
key_with_preset=val1,val2,val3
""")


class Parameter(models.Model):
    name = models.CharField(_('Name'), max_length=50)
    type = models.SmallIntegerField(_('Parameter type'), choices=PARAMETER_TYPES)
    analyze_type = models.ManyToManyField(AnalyseType, verbose_name=_('Analyse Type'))
    updated_at = models.DateTimeField(_('Update date'), editable=False, auto_now=True)
    process_logic = models.TextField(_('Process logic code'))
    parameter_definition = models.TextField(_('Parameter definition'), null=True, blank=True,
                                            help_text=PARAM_DEF_HELP_TEXT)

    def _handle_matrix_kv(self):
        pass

    def _handle_simple_kv(self):
        pass

    def create_update_parameter_keys(self):
        for lines in self.parameter_definition.split('\n'):
            pass

    class Meta:
        verbose_name = _('Parameter Definition')
        verbose_name_plural = _('Parameter Definitions')

    def __str__(self):
        return self.name


PARAMETER_VALUE_TYPES = (
    (1, _('String')),
    (5, _('Integer')),
    (10, _('Float')),
    (15, _('Boolean')),
)


class ParameterKey(models.Model):
    parameter = models.ForeignKey(Parameter, verbose_name=_('Parameter Definition'))
    name = models.CharField(_('Name'), max_length=30)
    code = models.CharField(_('Code name'), max_length=6, null=True, blank=True)
    help = models.CharField(_('Help text'), max_length=255, blank=True, null=True)
    type = models.SmallIntegerField(_('Parameter type'), choices=PARAMETER_VALUE_TYPES, default=1)
    presets = models.TextField(_('Presets'), blank=True, null=True)

    class Meta:
        verbose_name = _('Parameter Key')
        verbose_name_plural = _('Parameter Keys')

    def __str__(self):
        return self.name


class ParameterValue(models.Model):
    parameter = models.ForeignKey(Parameter, verbose_name=_('Parameter Definition'))
    key = models.ForeignKey(ParameterKey, verbose_name=_('Parameter Key'))
    analyse = models.ForeignKey(Analyse, verbose_name=_('Analyse'))
    name = models.CharField(_('Name'), max_length=30)
    value = models.CharField(_('Value'), max_length=30, blank=True)
    value_int = models.IntegerField(_('Int Value'), editable=False, default=0)
    value_float = models.IntegerField(_('Float Value'), editable=False, default=.0)

    type = models.SmallIntegerField(_('Parameter type'), choices=PARAMETER_TYPES)

    def _sync_values(self):
        if self.value_float:
            self.value = str(self.value_float)
        elif self.value_int:
            self.value = str(self.value_int)

    def save(self, *args, **kwargs):
        self._sync_values()
        super(ParameterValue, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('Result Value')
        verbose_name_plural = _('Result Values')

    def __str__(self):
        return self.name
