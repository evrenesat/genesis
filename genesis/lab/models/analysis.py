from django.db import models
from django.utils.translation import ugettext_lazy as _


# Create your models here.

class MediumType(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3)

    class Meta:
        verbose_name = _('Medium Type')
        verbose_name_plural = _('Medium Types')

    def __unicode__(self):
        return self.code


class SampleType(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3)
    medium = models.ManyToManyField(MediumType)

    class Meta:
        verbose_name = _('Sample Type')
        verbose_name_plural = _('Sample Types')

    def __unicode__(self):
        return self.code


class Method(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5, null=True, blank=True)

    class Meta:
        verbose_name = _('Analyse Method')
        verbose_name_plural = _('Analyse Methods')

    def __unicode__(self):
        return self.name


class AnalyseGroup(models.Model):
    name = models.CharField(max_length=30)
    code = models.CharField(max_length=5, null=True, blank=True)

    class Meta:
        verbose_name = _('Analyse')
        verbose_name_plural = _('Analysis')

    def __unicode__(self):
        return self.name


class AnalyseType(models.Model):
    group = models.ForeignKey(AnalyseGroup, models.PROTECT)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5, null=True, blank=True)

    class Meta:
        verbose_name = _('Analyse')
        verbose_name_plural = _('Analysis')

    def __unicode__(self):
        return self.name


