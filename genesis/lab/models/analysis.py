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


class StateDefinition(models.Model):
    type = models.ForeignKey(AnalyseType, models.PROTECT, verbose_name=_('Analyse Type'))
    name = models.CharField(_('Name'), max_length=50)

    class Meta:
        unique_together = ('type', 'name')
        verbose_name = _('Analyse State Definition')
        verbose_name_plural = _('Analyse State Definitions')

    def __str__(self):
        return self.name


class Analyse(models.Model):
    type = models.ForeignKey(AnalyseType, models.PROTECT, verbose_name=_('Analyse Type'))
    admission = models.ForeignKey(Admission, models.PROTECT, verbose_name=_('Patient Admission'))
    timestamp = models.DateTimeField(_('Definition Date'), editable=False, auto_now_add=True)


    class Meta:
        verbose_name = _('Analyse')
        verbose_name_plural = _('Analysis')

    def __str__(self):
        return "%s %s" % (self.type, self.admission)


class State(models.Model):
    type = models.ForeignKey(Analyse, models.PROTECT, verbose_name=_('Analyse'))
    comment = models.CharField(_('Comment'), max_length=50)
    timestamp = models.DateTimeField(_('Timestamp'), editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(_('Update date'), editable=False, auto_now=True)


    class Meta:
        verbose_name = _('Analyse State')
        verbose_name_plural = _('Analyse States')

    def __str__(self):
        return self.type




class ParameterDefinition(models.Model):
    analyze_type = models.ManyToManyField(AnalyseType, verbose_name=_('Analyse Type'))
    name = models.CharField(_('Name'), max_length=50)
    process_logic = models.TextField(_('Process Logic Code'))
    updated_at = models.DateTimeField(_('Update date'), editable=False, auto_now=True)


    class Meta:
        verbose_name = _('Parameter Definition')
        verbose_name_plural = _('Parameter Definitions')

    def __str__(self):
        return self.name


