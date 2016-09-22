from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.
from .patient import PatientAdmission


class MediumType(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3)

    class Meta:
        verbose_name = _('Medium Type')
        verbose_name_plural = _('Medium Types')

    def __str__(self):
        return self.code


class SampleType(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3)
    medium = models.ManyToManyField(MediumType)

    class Meta:
        verbose_name = _('Sample Type')
        verbose_name_plural = _('Sample Types')

    def __str__(self):
        return self.code


class Method(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5, null=True, blank=True)

    class Meta:
        verbose_name = _('Analyse Method')
        verbose_name_plural = _('Analyse Methods')

    def __str__(self):
        return self.name


class AnalyseGroup(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=5, null=True, blank=True)

    class Meta:
        verbose_name = _('Analyse Group')
        verbose_name_plural = _('Analyse Groups')

    def __str__(self):
        return self.name


class AnalyseType(models.Model):
    group = models.ForeignKey(AnalyseGroup, models.PROTECT)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5, null=True, blank=True)

    class Meta:
        verbose_name = _('Analyse Type')
        verbose_name_plural = _('Analyse Types')

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)

class AnalyseStateDefinition(models.Model):
    type = models.ForeignKey(AnalyseType, models.PROTECT, )
    name = models.CharField(max_length=50)

    class Meta:
        verbose_name = _('Analyse State Definition')
        verbose_name_plural = _('Analyse State Definitions')

    def __str__(self):
        return self.name


class Analyse(models.Model):
    type = models.ForeignKey(AnalyseType, models.PROTECT)
    admission = models.ForeignKey(PatientAdmission, models.PROTECT)
    name = models.CharField(max_length=100)
    timestamp = models.DateTimeField(_('Definition Date'), editable=False, auto_now_add=True)

    class Meta:
        verbose_name = _('Analyse')
        verbose_name_plural = _('Analysis')

    def __str__(self):
        return self.name

class AnalyseState(models.Model):
    type = models.ForeignKey(Analyse, models.PROTECT)
    comment = models.CharField(max_length=50)

    class Meta:
        verbose_name = _('Analyse State Entry')
        verbose_name_plural = _('Analyse State Entries')

    def __str__(self):
        return self.name
