from django.db import models
from django.utils.translation import ugettext_lazy as _

SEX = ((1, _('Female')),
       (2, _('Male')),
       )

RELATION = ((1, _('Self')),
            (2, _('Father')),
            (3, _('Mother')),
            # (3, _('Child')),
            )


class Institution(models.Model):
    name = models.CharField(_('Name'), max_length=50)
    governmental = models.BooleanField(_('Government Agency?'), default=False)
    surname = models.CharField(_('Surname'), max_length=50)
    timestamp = models.DateTimeField(_('Timestamp'), editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(_('Timestamp'), editable=False, auto_now=True)
    relation = models.SmallIntegerField(_('Patient Relation'), choices=RELATION)
    birthdate = models.DateField(_('Birthdate'))

    class Meta:
        verbose_name = _('Patient')
        verbose_name_plural = _('Patients')

    def __unicode__(self):
        return self.name

class Patient(models.Model):
    tcno = models.CharField(_('TC No'), max_length=11)
    name = models.CharField(_('Name'), max_length=50)
    newborn = models.BooleanField(_('Is newborn?'), default=False)
    surname = models.CharField(_('Surname'), max_length=50)
    sex = models.SmallIntegerField(_('Sex'), choices=SEX)
    timestamp = models.DateTimeField(_('Timestamp'), editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(_('Timestamp'), editable=False, auto_now=True)
    relation = models.SmallIntegerField(_('Patient Relation'), choices=RELATION)
    birthdate = models.DateField(_('Birthdate'))

    class Meta:
        verbose_name = _('Patient')
        verbose_name_plural = _('Patients')

    def __unicode__(self):
        return self.name

class PatientAdmission(models.Model):
    patient = models.ForeignKey(Patient, models.PROTECT)
    institution = models.ForeignKey(Institution, models.PROTECT)
    timestamp = models.DateTimeField(_('Creation Date'), editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(_('Timestamp'), editable=False, auto_now=True)

    class Meta:
        verbose_name = _('Patient Admission')
        verbose_name_plural = _('Patient Admissions')

    def __unicode__(self):
        return "%s %s" (self.patient, self.timestamp)


class Analyse(models.Model):
    admission = models.ForeignKey(PatientAdmission, models.PROTECT)
    name = models.CharField(max_length=100)
    timestamp = models.DateTimeField(_('Definition Date'), editable=False, auto_now_add=True)

    class Meta:
        verbose_name = _('Analyse')
        verbose_name_plural = _('Analysis')

    def __unicode__(self):
        return self.name
