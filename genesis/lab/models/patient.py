from django.contrib.auth.models import User
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

INSTITUTION_TYPE = ((10, _('Government Hospital')),
                    (20, _('Private Hospital')),
                    (30, _('Clinic')),
                    (99, _('Internal')),
                    )


class Institution(models.Model):
    name = models.CharField(_('Name'), max_length=100)
    code = models.CharField(_('Code'), max_length=5, null=True, blank=True)
    type = models.SmallIntegerField(_('Institution type'), choices=INSTITUTION_TYPE)
    phone = models.CharField(_('Phone'), max_length=30, null=True, blank=True)
    cellular = models.CharField(_('Cellular phone'), max_length=30, null=True, blank=True)
    address = models.CharField(_('Cellular phone'), max_length=100, null=True, blank=True)
    timestamp = models.DateTimeField(_('Timestamp'), editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(_('Update date'), editable=False, auto_now=True)
    # operator = models.ForeignKey(User, verbose_name=_('Operator'), editable=False)

    class Meta:
        verbose_name = _('Institution')
        verbose_name_plural = _('Institutions')

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains", "code__startswith")


class Doctor(models.Model):
    name = models.CharField(_('Name'), max_length=50)
    surname = models.CharField(_('Surname'), max_length=50)
    institution = models.ForeignKey(Institution, models.SET_NULL, blank=True, null=True)
    timestamp = models.DateTimeField(_('Timestamp'), editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(_('Timestamp'), editable=False, auto_now=True)
    # operator = models.ForeignKey(User, verbose_name=_('Operator'), editable=False)

    class Meta:
        verbose_name = _('Doctor')
        verbose_name_plural = _('Doctors')

    def __str__(self):
        return "%s %s" % (self.name, self.surname)

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains", "surname__icontains")


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
    # operator = models.ForeignKey(User, verbose_name=_('Operator'), editable=False)

    @property
    def full_name(self):
        return '%s %s' % (self.name, self.surname)

    class Meta:
        verbose_name = _('Patient')
        verbose_name_plural = _('Patients')

    def __str__(self):
        return "%s %s | %s | %s " % (self.name, self.surname, self.tcno, self.id)

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "tcno__startswith", "name__icontains", "surname__icontains")


class Admission(models.Model):
    patient = models.ForeignKey(Patient, models.PROTECT, verbose_name=_('Patient'))
    institution = models.ForeignKey(Institution, models.PROTECT, verbose_name=_('Institution'))
    doctor = models.ForeignKey(Doctor, models.PROTECT, verbose_name=_('Doctor'), null=True,
                               blank=True)
    indications = models.TextField(_('Indications'), null=True, blank=True)
    history = models.TextField(_('Reproductive story / Family Tree'), null=True, blank=True)
    week = models.CharField(_('Pregnancy week'), null=True, blank=True, max_length=7)
    upd_week = models.CharField(_('UPD'), null=True, blank=True, max_length=7)
    lmp_date = models.DateField(_('LMP'), null=True, blank=True)
    timestamp = models.DateTimeField(_('Creation Date'), editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(_('Timestamp'), editable=False, auto_now=True)
    # operator = models.ForeignKey(User, verbose_name=_('Operator'), editable=False)

    class Meta:
        verbose_name = _('Patient Admission')
        verbose_name_plural = _('Patient Admissions')

    def __str__(self):
        return "%s %s" % (self.patient, str(self.timestamp)[:19])

class AdmissionSample(models.Model):
    admission = models.ForeignKey(Admission, models.PROTECT, verbose_name=_('Patient Admission'))
    timestamp = models.DateTimeField(_('Creation Date'), editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(_('Timestamp'), editable=False, auto_now=True)
    amount = models.PositiveSmallIntegerField(_('Amount'), default=1)
    type = models.ForeignKey('SampleType', models.PROTECT, verbose_name=_('Sample type'))
    # operator = models.ForeignKey(User, verbose_name=_('Operator'), editable=False)

    class Meta:
        verbose_name = _('Sample')
        verbose_name_plural = _('Samples')

    def __str__(self):
        return "%s %s" % (self.admission, str(self.timestamp)[:19])
