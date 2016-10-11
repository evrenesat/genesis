import json

from django import forms
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.
from ..utils import pythonize

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
    order = models.PositiveSmallIntegerField(_('Order'), null=True, blank=True)

    class Meta:
        verbose_name = _('Analyse State Definition')
        verbose_name_plural = _('Analyse State Definitions')
        ordering = ('order', )

    def __str__(self):
        return self.name


class Analyse(models.Model):
    type = models.ForeignKey(AnalyseType, models.PROTECT, verbose_name=_('Analyse Type'))
    admission = models.ForeignKey(Admission, models.PROTECT, verbose_name=_('Patient Admission'))
    timestamp = models.DateTimeField(_('Definition date'), editable=False, auto_now_add=True)
    result = models.TextField(_('Analyse result'), blank=True, null=True)
    finished = models.BooleanField(_('Finished'), default=False)

    def applicable_states_ids(self):
        return self.type.statedefinition_set.values_list('id', flat=True)

    class Meta:
        verbose_name = _('Analyse')
        verbose_name_plural = _('Analysis')

    def __str__(self):
        return "%s %s" % (self.type, self.admission)


class State(models.Model):
    analyse = models.ForeignKey(Analyse, models.PROTECT, verbose_name=_('Analyse'))
    definition = models.ForeignKey(StateDefinition, models.PROTECT, verbose_name=_('State'))
    comment = models.CharField(_('Comment'), max_length=50, null=True, blank=True)
    timestamp = models.DateTimeField(_('Timestamp'), editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(_('Update date'), editable=False, auto_now=True)

    class Meta:
        verbose_name = _('Analyse State')
        verbose_name_plural = _('Analyse States')
        ordering = ('timestamp',)

    def __str__(self):
        return "%s %s" % (self.analyse, self.definition)


PARAMETER_TYPES = (
    ('keyval_s', _('Simple Key & Value')),
    ('keyval_t', _('Tabular Key & Value')),
    ('matrix_bool', _('Boolean Matrix')),
    ('matrix_str', _('String Matrix')),
    ('matrix_num', _('Numeric Matrix')),
)
PARAM_DEF_HELP_TEXT = _("""
<hr />
<strong>Data Definition Help</strong><br />
Matrices:<br />
cols = N/N, Mt/N, Mt/Mt<br />
rows = Faktör V Leiden PCR, Faktör V HR2 PCR<br />
<hr />
Key/Values:<br />
key<br />
key2<br />
key_with_preset=val1,val2,val3
""")


class Parameter(models.Model):
    name = models.CharField(_('Name'), max_length=50)
    type = models.CharField(_('Parameter type'), max_length=12, choices=PARAMETER_TYPES)
    analyze_type = models.ManyToManyField(AnalyseType, verbose_name=_('Analyse Type'))
    updated_at = models.DateTimeField(_('Update date'), editable=False, auto_now=True)
    process_logic = models.TextField(_('Process logic code'), null=True, blank=True)
    parameter_definition = models.TextField(_('Parameter definition'), null=True, blank=True,
                                            help_text=PARAM_DEF_HELP_TEXT)

    def create_parameter_key(self, key_name, row_no=None, col_no=None, preset=None):
        code = pythonize(key_name)
        param_type, data_type = self.type.split('_')
        if param_type != 'matrix':
            data_type = None
        ParameterKey.objects.update_or_create({'code': code,
                                               'row_no': row_no,
                                               'col_no': col_no,
                                               'presets': preset,
                                               'type': data_type,
                                               },
                                              parameter=self,
                                              name=key_name
                                              )

    def _create_matrix_params(self, rows, cols):
        for row_no, row in enumerate(map(str.strip, rows.split(','))):
            for col_no, col in enumerate(map(str.strip, cols.split(','))):
                self.create_parameter_key('%s__%s' % (row, col), row_no, col_no)

    def _handle_matrix_params(self, line, line_no):
        """creates ParameterKey objects for each matrix cell

        self.first_line a cache for first loop
        """
        try:
            typ, vals = map(str.strip, line.split('='))
            self.first_line  # testing if this is our second run
            if typ == 'rows':
                self._create_matrix_params(vals, self.first_line[1])
            else:  # then it should be cols
                self._create_matrix_params(self.first_line[1], vals)
        except AttributeError:
            self.first_line = (typ, vals)

    def _handle_keyval_params(self, line, line_no):
        if '=' in line:
            key, preset = map(str.strip, line.split('='))
        else:
            key = line.strip()
            preset = None
        self.create_parameter_key(key, row_no=line_no, preset=preset)

    def create_update_parameter_keys(self):
        for i, line in enumerate(self.parameter_definition.split('\n')):
            line = line.strip()
            if line:
                getattr(self, '_handle_%s_params' % self.type[:6])(line, i)


    def create_empty_values(self, analyse):
        for pk in self.parameterkey_set.all():
            pk.create_empty_value(analyse)

    class Meta:
        verbose_name = _('Parameter Definition')
        verbose_name_plural = _('Parameter Definitions')

    def __str__(self):
        return self.name


PARAMETER_VALUE_TYPES = (
    ('str', _('String')),
    ('num', _('Numeric')),
    ('bool', _('Boolean')),
)


class ParameterKey(models.Model):
    parameter = models.ForeignKey(Parameter, verbose_name=_('Parameter Definition'))
    name = models.CharField(_('Name'), max_length=50)
    code = models.CharField(_('Code name'), max_length=50, null=True, blank=True)
    help = models.CharField(_('Help text'), max_length=255, blank=True, null=True)
    type = models.CharField(_('Parameter type'), max_length=5,
                            choices=PARAMETER_VALUE_TYPES, default=1)
    presets = models.TextField(_('Presets'), blank=True, null=True)
    row_no = models.IntegerField(_('Row number'), default=0)
    col_no = models.IntegerField(_('Row number'), null=True, blank=True)

    def create_empty_value(self, analyse):
        ParameterValue.objects.get_or_create(parameter=self.parameter, key=self,
                                             name=self.name, analyse=analyse,
                                             type=self.type)

    def _jsonify_presets(self):
        if self.presets and self.presets.strip():
            try:
                json.loads(self.presets)
            except ValueError:
                self.presets = json.dumps(list(map(str.strip, self.presets.split(','))))

    def save(self, *args, **kwargs):
        self._jsonify_presets()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Parameter Key')
        verbose_name_plural = _('Parameter Keys')

    def __str__(self):
        return self.name


class ParameterValue(models.Model):
    parameter = models.ForeignKey(Parameter, verbose_name=_('Parameter Definition'))
    key = models.ForeignKey(ParameterKey, verbose_name=_('Parameter Key'))
    analyse = models.ForeignKey(Analyse, verbose_name=_('Analyse'))
    name = models.CharField(_('Name'), max_length=30, editable=False)
    value = models.CharField(_('Value'), max_length=30, blank=True, null=True)
    value_int = models.IntegerField(_('Int Value'), editable=False, default=0)
    value_float = models.IntegerField(_('Float Value'), editable=False, default=.0)

    type = models.CharField(_('Parameter type'), max_length=5, choices=PARAMETER_VALUE_TYPES)

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
