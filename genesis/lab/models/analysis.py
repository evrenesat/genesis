import json
from collections import defaultdict
from datetime import datetime

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache
# Create your models here.


from ..utils import pythonize, lazy_property

from .patient import Admission, ExternalLab


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(_('Biography'), max_length=500, blank=True, null=True)
    title = models.CharField(_('Title'), max_length=30, blank=True, null=True)
    prefix = models.CharField(_('Title prefix'), max_length=30, blank=True, null=True)
    address = models.TextField(_('Address'), max_length=500, blank=True, null=True)
    phone = models.CharField(_('Phone'), max_length=30, blank=True, null=True)
    signature = models.ImageField(_('Signature image'), null=True, blank=True,
                                  upload_to='static/signatures')

    class Meta:
        verbose_name = _('Person')
        verbose_name_plural = _('Persons')

    def __str__(self):
        return self.user.get_full_name()


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

    def get_code(self):
        return self.code or self.name[:3].upper()


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

    def get_code(self):
        return self.code or self.name[:3].upper()





class AnalyseType(models.Model):
    subtypes = models.ManyToManyField('self', verbose_name=_('Sub types'), related_name='main_type',
                                      null=True, blank=True)
    group_type = models.BooleanField(_('Group'), default=False, editable=False,
                                     help_text=_(
                                         'This is a group type, consist of other analyse types'))

    category = models.ForeignKey(Category, models.PROTECT, verbose_name=_('Category'), null=True,
                                 blank=True)
    method = models.ForeignKey(Method, models.SET_NULL, verbose_name=_('Method'), null=True,
                               blank=True)
    sample_type = models.ManyToManyField(SampleType, verbose_name=_('Sample Type'))
    name = models.CharField(_('Name'), max_length=100, unique=True)
    code = models.CharField(_('Code name'), max_length=10, null=True, blank=True)
    footnote = models.TextField(_('Report footnote'), blank=True, null=True,
                                help_text=_('This will be shown under the report'))
    external = models.BooleanField(_('Goes to external lab'), default=False,
                                   help_text=_('Analysed by an external lab'))
    external_lab = models.ForeignKey(ExternalLab, models.SET_NULL, null=True, blank=True,
                                     verbose_name=_('External lab'))
    external_price = models.DecimalField(_('External lab price'), max_digits=6, decimal_places=2,
                                         default=0)
    price = models.DecimalField(_('Price'), max_digits=6, decimal_places=2, default=0)
    alternative_price = models.DecimalField(_('Alternative price'), max_digits=6, decimal_places=2,
                                            help_text=_('Alternative price definition. '
                                                        'Can be used for foregeign currencies etc.')
                                            , default=0)
    process_logic = models.TextField(_('Process logic code'), null=True, blank=True,
                                     help_text=_('This code will be used to calculate the analyse '
                                                 'result according to entered data'))
    process_time = models.SmallIntegerField(_('Process Time'))

    def is_sample_type_compatible(self, sample_type):
        return sample_type in self.sample_type.all()

    class Meta:
        verbose_name = _('Analyse Type')
        verbose_name_plural = _('Analyse Types')

    def __str__(self):
        return "%s | %s %s" % (self.name,
                               self.category.get_code() if self.category else '',
                               ('%s:%s' % (_('Ext.Lab'),
                                           self.external_lab.get_code()
                                           ) if self.external else ''))

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)


class ReportTemplate(models.Model):
    analyse_type = models.ManyToManyField(AnalyseType, verbose_name=_('Analyse Type'))
    name = models.CharField(_('Name'), max_length=20, null=True, blank=True)
    priority = models.PositiveSmallIntegerField(_('Priority'),
                                                choices=[(n, n) for n in range(0, 50, 5)],
                                                default=5)
    title = models.CharField(_('Report title'), null=True, blank=True, max_length=30)
    combo = models.BooleanField(_('Combo'), default=False,
                                help_text=_('Supports combined reporting of multiple analyses'))
    generic = models.BooleanField(_('Generic'), default=False,
                                  help_text=_('Use generic reporting'))
    template = models.TextField(_('Template'))

    # operator = models.ForeignKey(User, verbose_name=_('Operator'), editable=False)

    class Meta:
        verbose_name = _('Report Template')
        verbose_name_plural = _('Report Templates')
        ordering = ('-priority',)

    def __str__(self):
        return "%s" % (self.name,)


class Analyse(models.Model):
    type = models.ForeignKey(AnalyseType, models.PROTECT, verbose_name=_('Analyse Type'), null=True,
                             blank=True)
    admission = models.ForeignKey(Admission, models.CASCADE, verbose_name=_('Patient Admission'))

    result_copy = models.TextField(_('Copy of result'), blank=True, null=True, editable=False)
    result = models.TextField(_('Result parameters'), blank=True, null=True,
                              help_text=_("Can be used to override entered/calculated result "
                                          "parameters<br>Format:<br> key=val<br />key2=val2"))
    comment = models.TextField(_('Interpretation'), blank=True, null=True,
                               help_text=_('Interpretation of analyse results'))
    short_result = models.TextField(_('Result'), blank=True, null=True,
                                    help_text=_('Normal Karyotype, Trisomy 21'))
    result_json = models.TextField(_('Analyse result dict'), editable=False, null=True)
    sample_amount = models.CharField(_('Sample Amount'), max_length=20, null=True, blank=True)
    sample_type = models.ForeignKey(SampleType, models.PROTECT, verbose_name=_('Sample type'),
                                    null=True, blank=True)
    template = models.ForeignKey(ReportTemplate, models.PROTECT, verbose_name=_('Report template'),
                                 null=True, blank=True, help_text=_(
            'Instead of default one, use this template to create the analyse report.'))
    group_relation = models.CharField(null=True, blank=True, max_length=50)

    finished = models.BooleanField(_('Finished'), default=False)
    timestamp = models.DateTimeField(_('Definition date'), editable=False, auto_now_add=True)

    external = models.BooleanField(_('Goes to external lab'), default=False,
                                   help_text=_('Analysed by an external lab'))
    external_lab = models.ForeignKey(ExternalLab, models.SET_NULL, null=True, blank=True, verbose_name=_('External lab'))

    completion_time = models.DateTimeField(_('Completion time'), editable=False, null=True)
    approve_time = models.DateTimeField(_('Approve time'), editable=False, null=True)
    analyser = models.ForeignKey(Profile, models.PROTECT, verbose_name=_('Analyser'), null=True,
                                 blank=True, related_name='analyses')
    approved = models.BooleanField(_('Approved'), default=False)
    approver = models.ForeignKey(Profile, models.PROTECT, verbose_name=_('Approver'), null=True,
                                 blank=True, related_name='approved_analyses')

    def _set_state_for(self, approve=False, finish=False):
        state_set = self.state_set.all()
        if not state_set or (state_set[0].definition.finish != finish
                             or state_set[0].definition.approve != approve):
            state = self.type.statedefinition_set.get(finish=finish, approve=approve)
            self.state_set.create(definition=state)

    def mark_approved(self, request, set_state=False):
        if not request.user.has_perm('lab.can_approve_analysis'):
            raise ValidationError('-')  # PermissionDenied(
            # _("You don't have required permissions to mark an analyse as approved"))
        else:
            self.approved = True
            self.approve_time = datetime.now()
            self.approver = request.user.profile
            self.save()
        if set_state:
            self._set_state_for(approve=True)

    def mark_finished(self, request, set_state=False):
        if not request.user.has_perm('lab.can_finish_analyse'):
            raise PermissionDenied(
                _("You don't have required permissions to  mark an analyse as finished"))
        else:
            self.finished = True
            self.completion_time = datetime.now()
            self.analyser = request.user.profile
            self.save()
        if set_state:
            self._set_state_for(finish=True)

    @lazy_property
    def get_code(self):
        return self.type.code or self.type.name[:3]

    @lazy_property
    def result_dict(self):
        d = {}
        for par_val in self.parametervalue_set.all():
            d[par_val.code] = par_val.val
        return d

    def create_empty_values(self):
        for prm in self.type.parameter_set.all():
            prm.create_empty_values(self)

    def calculate_result(self):
        """executes result process logic with result"""
        context = self.result_dict.copy()
        context['result_set'] = self.result_dict.copy()
        if self.type.process_logic:
            context['result'] = ''
            context['comment'] = ''
            exec(self.type.process_logic, context)
            if context['result']:
                self.short_result = context['result']
            if context['comment']:
                self.comment = context['comment']
        return context['result_set']

    def get_result_dict(self):
        """
        If there is a "process_logic" code defined in analyse type,
        then calculated result returned as is.
        Otherwise entered results parameters
        Returns:
            Composed analyse result dict.
        """
        if not self.result_json:
            return {}
        calculated_result = json.loads(self.result_json)
        # if self.type.process_logic:
        #     calculated_result['title'] = self.type.name
        #     calculated_result['analyse_id'] = self.id
        # return calculated_result
        results = defaultdict(dict)
        # results.update(calculated_result)
        titles = {}
        for par_val in self.parametervalue_set.all():
            titles[par_val.code] = par_val.key.name
        for k, v in calculated_result.items():
            k = k.strip()
            if k.startswith('_'):
                continue
            results[k]['value'] = v
            results[k]['title'] = titles[k]
            results[k]['code'] = k
        results['title'] = self.type.name
        results['analyse_id'] = self.id
        return dict(results)

    def save_result(self):
        """saves serialized calculation result to self.result_json
        allows manual result data entry through self.result to override calculation result"""
        result_data = self.calculate_result()
        if self.result and self.result.strip() and self.result != self.result_copy:
            manual_result_data = dict([tuple(line.split('=')) for line in
                                       self.result.strip().split('\n')])
            result_data.update(manual_result_data)
        elif result_data:
            self.result = '\n'.join(['%s = %s' % (k, v) for k, v in result_data.items()])
        self.result_copy = self.result
        self.result_json = json.dumps(result_data)
        self.save()
        # if self.type.process_logic.strip():
        #     self.result = '\n'.join(['%s = %s' % (k, v) for k, v in result_data.values()])

    def applicable_sample_type_ids(self):
        return self.type.sample_type.values_list('id', flat=True)

    def applicable_states_ids(self):
        return self.type.statedefinition_set.values_list('id', flat=True)

    def clean(self):
        if not self.type.is_sample_type_compatible(self.sample_type):
            raise ValidationError(
                str(_('Improper Sample Type for the selected analyse %s.' % self.type)) +
                str(_('Following sample types can be selected;')) +
                "\n%s" % ', '.join([st.name for st in self.type.sample_type.all()])
            )

    class Meta:
        verbose_name = _('Analyse')
        verbose_name_plural = _('Analysis')
        permissions = (
            ("can_approve_analysis", "Can approve analysis"),
            ("can_finish_analyse", "Can finish analysis"),
            ("can_enter_data_to_analyse", "Can enter data to analysis"),
        )

    def __str__(self):
        return "%s %s" % (self.type, self.admission)


class StateDefinition(models.Model):
    type = models.ManyToManyField(AnalyseType, verbose_name=_('Analyse Type'))
    name = models.CharField(_('Name'), max_length=50)
    explanation = models.TextField(_('Explanation'), null=True, blank=True)
    finish = models.BooleanField(_('Finished state'), default=False)
    approve = models.BooleanField(_('Approved state'), default=False)
    order = models.PositiveSmallIntegerField(_('Order'), null=True, blank=True)

    class Meta:
        verbose_name = _('Analyse State Definition')
        verbose_name_plural = _('Analyse State Definitions')
        ordering = ('order',)

    def __str__(self):
        return self.name


class State(models.Model):
    analyse = models.ForeignKey(Analyse, models.CASCADE, verbose_name=_('Analyse'))
    definition = models.ForeignKey(StateDefinition, models.CASCADE, verbose_name=_('State'))
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
<br><br>Note: Parameters that their code name starts with underscore "_" will be excluded from reports.
""")


class Parameter(models.Model):
    name = models.CharField(_('Name'), max_length=50)
    type = models.CharField(_('Parameter type'), max_length=12, default='keyval_s',
                            choices=PARAMETER_TYPES)
    analyze_type = models.ManyToManyField(AnalyseType, verbose_name=_('Analyse Type'))
    updated_at = models.DateTimeField(_('Update date'), editable=False, auto_now=True)
    parameter_definition = models.TextField(_('Parameter definition'), null=True, blank=True,
                                            help_text=PARAM_DEF_HELP_TEXT)

    def create_parameter_key(self, key_name, row_no=None, col_no=None, preset=None):
        code = pythonize(key_name)
        param_type, data_type = self.type.split('_')
        if param_type != 'matrix':
            data_type = 1
        # FIXME: update requires a  double save
        obj, created = ParameterKey.objects.update_or_create({'code': code.strip(),
                                                              'row_no': row_no,
                                                              'col_no': col_no,
                                                              'presets': preset,
                                                              'type': data_type,
                                                              },
                                                             parameter=self,
                                                             name=key_name.strip()
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
    ('num', _('Integer')),
    ('dec', _('Decimal')),
    ('bool', _('Boolean')),
)


class ParameterKey(models.Model):
    parameter = models.ForeignKey(Parameter, verbose_name=_('Parameter Definition'))
    name = models.CharField(_('Name'), max_length=50)
    default_value = models.TextField(_('Default value'), null=True, blank=True)
    code = models.CharField(_('Code name'), max_length=50, null=True, blank=True,
                            help_text=_(
                                'Parameters that their code name starts with underscore "_" will be excluded from reports.'))
    help = models.CharField(_('Help text'), max_length=255, blank=True, null=True)
    type = models.CharField(_('Parameter type'), max_length=5,
                            choices=PARAMETER_VALUE_TYPES, default=1)
    presets = models.TextField(_('Presets'), blank=True, null=True)
    row_no = models.IntegerField(_('Row number'), default=0)
    col_no = models.IntegerField(_('Column number'), null=True, blank=True)

    def preset_choices(self):
        return [(v, v) for v in json.loads(self.presets)] if self.presets else None

    def create_empty_value(self, analyse):
        pv, new = ParameterValue.objects.get_or_create(parameter=self.parameter, key=self,
                                                       code=self.code, analyse=analyse,
                                                       type=self.type)
        if new and self.default_value:
            if self.type == 'num':
                pv.value_int = int(self.default_value)
            elif self.type == 'str':
                pv.value = self.default_value
            elif self.type == 'bool':
                pv.value_int = 1 if self.default_value.strip() == '1' else 0
            elif self.type == 'dec':
                pv.value_float = float(self.default_value)
            pv.save()

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
    code = models.CharField(_('Code name'), max_length=30, )
    value = models.CharField(_('Value'), max_length=30, blank=True, null=True)
    value_int = models.IntegerField(_('Int Value'), editable=False, default=0)
    value_float = models.FloatField(_('Float Value'), editable=False, default=.0)

    type = models.CharField(_('Parameter type'), max_length=5, choices=PARAMETER_VALUE_TYPES)

    def keyid(self):
        ckey = "PKEYDATA:%s" % self.key_id
        data = cache.get(ckey, None)
        if data is None:
            data = {'auto_preset': False, 'presets': []}
            if self.key.presets:
                data['presets'] = json.loads(self.key.presets)
            else:
                data['auto_preset'] = True
                data['presets'] = list(
                    filter(None, self.key.parametervalue_set.distinct().values_list('value',
                                                                                    flat=True)))
            cache.set(ckey, data, 30)
        return "<input class=keydata type=hidden value='%s'>" % json.dumps(data)

    keyid.allow_tags = True

    def analyse_name(self):
        return self.analyse.type.name

    analyse_name.short_description = _('Analyse name')
    analyse_name.admin_order_field = 'analyse__type__name'

    def analyse_state(self):
        state = self.analyse.state_set.all()
        return state[0].definition.name if state else '-'

    analyse_state.short_description = _('Analyse state')
    analyse_state.admin_order_field = 'analyse__finished'

    def patient_name(self):
        return self.analyse.admission.patient.full_name()

    patient_name.short_description = _('Patient name')
    patient_name.admin_order_field = 'analyse__patient__name'

    @property
    def val(self):
        return self.value_float or self.value_int or self.value

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
        return "%s: %s" % (self.code, self.value)
