from django.utils import timezone

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
                    (40, _('Lab')),
                    (50, _('Supplier')),
                    (99, _('Internal')),
                    )


class Institution(models.Model):
    name = models.CharField(_('Name'), max_length=100)
    code = models.CharField(_('Code'), max_length=5, null=True, blank=True)
    type = models.SmallIntegerField(_('Institution type'), choices=INSTITUTION_TYPE)
    phone = models.CharField(_('Phone'), max_length=30, null=True, blank=True)
    cellular = models.CharField(_('Cellular phone'), max_length=30, null=True, blank=True)
    timestamp = models.DateTimeField(_('Timestamp'), editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(_('Update date'), editable=False, auto_now=True)
    email = models.EmailField(_('Email'), null=True, blank=True)
    address = models.CharField(_('Address'), max_length=100, null=True, blank=True)
    tax_no = models.CharField(_('Tax no'), max_length=11, null=True, blank=True)
    tax_office = models.CharField(_('Tax office'), max_length=40, null=True, blank=True)

    # operator = models.ForeignKey(User, verbose_name=_('Operator'), editable=False)

    class Meta:
        verbose_name = _('Institution')
        verbose_name_plural = _('Institutions')

    def __str__(self):
        return self.name

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains", "code__startswith")

class ExternalLab(models.Model):
    name = models.CharField(_('Name'), max_length=30, unique=True)
    code = models.CharField(_('Code'), max_length=5, null=True, blank=True)
    institution = models.ForeignKey(Institution, models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name = _('External Lab')
        verbose_name_plural = _('External Labs')

    def __str__(self):
        return self.name

    def get_code(self):
        return self.code or self.name[:3].upper()

class Doctor(models.Model):
    title = models.CharField(_('Title'), max_length=20)
    name = models.CharField(_('Name'), max_length=50)
    surname = models.CharField(_('Surname'), max_length=50)
    institution = models.ForeignKey(Institution, models.SET_NULL, blank=True, null=True,
                                    verbose_name=_('Institution'),
                                    help_text=_("If left blank, an institution record will be created for this doctor"))
    timestamp = models.DateTimeField(_('Timestamp'), editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(_('Timestamp'), editable=False, auto_now=True)
    email = models.EmailField(_('Email'), null=True, blank=True)
    # operator = models.ForeignKey(User, verbose_name=_('Operator'), editable=False)

    def full_name(self):
        return '%s %s' % (self.name, self.surname or '')

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
    address = models.CharField(_('Address'), max_length=100, null=True, blank=True)

    # operator = models.ForeignKey(User, verbose_name=_('Operator'), editable=False)

    def full_name(self, abr_limit=20):
        full_name = "%s %s" % (self.name, self.surname)
        if len(full_name) <= abr_limit:
            return full_name
        names = full_name.split(' ')
        first_name = names.pop(0)
        last_name = names.pop(-1)
        middle = ''.join(['%s.' % a[0] for a in names])

        return '%s %s %s' % (first_name, middle, last_name)

    class Meta:
        verbose_name = _('Patient')
        verbose_name_plural = _('Patients')

    def __str__(self):
        return "%s | %s | %s " % (self.full_name(15), self.tcno, self.id)

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "tcno__startswith", "name__icontains", "surname__icontains")


class Admission(models.Model):
    patient = models.ForeignKey(Patient, models.PROTECT, verbose_name=_('Patient'))
    institution = models.ForeignKey(Institution, models.PROTECT, verbose_name=_('Institution'))
    doctor = models.ForeignKey(Doctor, models.PROTECT, verbose_name=_('Doctor'), null=True,
                               blank=True)
    is_urgent = models.BooleanField(_('Urgent'), default=False)
    indications = models.TextField(_('Indications'), null=True, blank=True)
    history = models.TextField(_('Reproductive story / Family Tree'), null=True, blank=True)
    week = models.CharField(_('Pregnancy week'), null=True, blank=True, max_length=7)
    upd_week = models.CharField(_('UPD'), null=True, blank=True, max_length=7)
    lmp_date = models.DateField(_('LMP'), null=True, blank=True)
    timestamp = models.DateTimeField(_('Admission date'), default=timezone.now)
    updated_at = models.DateTimeField(_('Timestamp'), editable=False, auto_now=True)

    # operator = models.ForeignKey(User, verbose_name=_('Operator'), editable=False)


    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "patient__name__icontains")

    def is_approved(self):
        return all(self.analyse_set.values_list('approved', flat=True))

    def analyse_state(self, raw=False):
        total, approved, finished = 0,0,0
        for fin,app in self.analyse_set.values_list('finished', 'approved'):
            total +=1
            if app:
                approved+=1
            if fin:
                finished +=1
        if raw:
            return total, finished, approved
        return "{}/{}/{}".format(total, finished, approved)

    analyse_state.short_description = _('Analyse State')

    class Meta:
        verbose_name = _('Patient Admission')
        verbose_name_plural = _('Patient Admissions')

    def __str__(self):
        return "%s %s" % (self.patient, str(self.timestamp)[:19])


class AdmissionStateDefinition(models.Model):
    name = models.CharField(_('Name'), max_length=50)
    explanation = models.TextField(_('Explanation'), null=True, blank=True)
    hardcoded = models.BooleanField(_('Cannot be deleted'), default=False, editable=False)
    first = models.BooleanField(_('First state'), default=False)
    reject = models.BooleanField(_('Reject state'), default=False)
    finished = models.BooleanField(_('Finish state'), default=False)
    order = models.PositiveSmallIntegerField(_('Order'), null=True, blank=True)

    class Meta:
        verbose_name = _('Admission State Definition')
        verbose_name_plural = _('Admission State Definitions')
        ordering = ('order',)

    def __str__(self):
        return self.name


class AdmissionState(models.Model):
    admission = models.ForeignKey(Admission, models.CASCADE, verbose_name=_('Admission'))
    definition = models.ForeignKey(AdmissionStateDefinition, models.PROTECT, verbose_name=_('State'))
    comment = models.CharField(_('Comment'), max_length=50, null=True, blank=True)
    timestamp = models.DateTimeField(_('Timestamp'), editable=False, auto_now_add=True)
    updated_at = models.DateTimeField(_('Update date'), editable=False, auto_now=True)

    class Meta:
        verbose_name = _('Admission State')
        verbose_name_plural = _('Admission States')
        ordering = ('timestamp',)

    def __str__(self):
        return "%s: %s" % (self.admission, self.definition.name)



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
