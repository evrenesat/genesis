from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.
from lab.models import Admission, AnalyseType, Institution
from lab.models import Analyse
from lab.models import Patient

PAYMENT_METHODS = (
    (10, _('None')),
    (20, _('Open Account')),
    (30, _('Cash')),
    (40, _('Credit Card')),
    # (40, _('Short-term Open Account')),
)


class InstitutePricing(models.Model):
    """
    base price discounts per institute
    """
    institution = models.OneToOneField(Institution, models.PROTECT, verbose_name=_('Institution'))
    discount_rate = models.DecimalField(_('Discount rate'), max_digits=6, decimal_places=2)
    use_alt_pricing = models.BooleanField(_('Use alternative price'), default=False)
    preferred_payment_method = models.SmallIntegerField(_('Preferred payment method'),
                                                        choices=PAYMENT_METHODS, default=10)
    timestamp = models.DateTimeField(_('Definition date'), editable=False, auto_now_add=True)

    class Meta:
        verbose_name = _('Institue Pricing')
        verbose_name_plural = _('Institue Pricings')

    def __str__(self):
        return "%s %s" % (self.institution.name, self.discount_rate)


class AnalysePricing(models.Model):
    """

    """
    pricing = models.ForeignKey(InstitutePricing, models.PROTECT,
                                verbose_name=_('Institute pricing'))
    institution = models.ForeignKey(Institution, models.PROTECT, verbose_name=_('Institution'))
    analyse_type = models.ForeignKey(AnalyseType, verbose_name=_('Analyse Type'))
    price = models.DecimalField(_('Exact price'), max_digits=8, decimal_places=2)
    discount_rate = models.DecimalField(_('Discount rate'), max_digits=6, decimal_places=2)
    timestamp = models.DateTimeField(_('Definition date'), editable=False, auto_now_add=True)

    class Meta:
        verbose_name = _('Analyse Pricing')
        verbose_name_plural = _('Analyse Pricings')

    def __str__(self):
        return "%s > %s" % (self.analyse_type.name, self.institution.name)


PAYMENT_TYPES = (
    (10, _('Customer debt (-)')),
    (20, _('Customer payment (+)')),
)


class Payment(models.Model):
    admission = models.ForeignKey(Admission, models.PROTECT, null=True, blank=True,
                                  verbose_name=_('Admission'))
    patient = models.ForeignKey(Patient, models.PROTECT,
                                verbose_name=_('Patient'), null=True, blank=True)
    institution = models.ForeignKey(Institution, models.PROTECT,
                                    verbose_name=_('Institution'), null=True, blank=True)
    type = models.SmallIntegerField(_('Record type'), choices=PAYMENT_METHODS)
    method = models.SmallIntegerField(_('Payment method'), choices=PAYMENT_TYPES, default=10)
    amount = models.DecimalField(_('Amount'), max_digits=8, decimal_places=2, null=True, blank=True)
    timestamp = models.DateTimeField(_('Definition date'), editable=False, auto_now_add=True)

    class Meta:
        verbose_name = _('Payment Record')
        verbose_name_plural = _('Payment Records')

    def __str__(self):
        return "%s %s" % (self.patient.name, self.price)


class AdmissionPricing(models.Model):
    admission = models.ForeignKey(Admission, models.PROTECT, verbose_name=_('Admission'))
    timestamp = models.DateTimeField(_('Definition date'), editable=False, auto_now_add=True)
    list_price = models.DecimalField(_('List price'), max_digits=8, decimal_places=2,
                                     editable=False)
    discount_percentage = models.DecimalField(_('Discount percentage'), max_digits=8, null=True,
                                              decimal_places=2, editable=False, blank=True)
    discount_amount = models.DecimalField(_('Discount amount'), max_digits=8, decimal_places=2,
                                          editable=False, null=True, blank=True)
    final_amount = models.DecimalField(_('Final amount'), max_digits=8, decimal_places=2, null=True,
                                       blank=True)

    class Meta:
        verbose_name = _('Admission Pricing')
        verbose_name_plural = _('Admission Pricings')

    def __str__(self):
        return "%s %s" % (self.patient.name, self.price)


class Invoice(models.Model):
    admission = models.ManyToManyField(Admission, verbose_name=_('Admission'), editable=False)
    name = models.CharField(_('Name'), null=True, blank=True, max_length=250)
    address = models.CharField(_('Address'), null=True, blank=True, max_length=250)
    amount = models.DecimalField(_('Amount'), max_digits=8, decimal_places=2, editable=False,
                                 null=True, blank=True)
    tax = models.IntegerField(_('Tax amount'), null=True, blank=True)
    total = models.DecimalField(_('Price'), max_digits=8, decimal_places=2)
    timestamp = models.DateTimeField(_('Definition date'), editable=False, auto_now_add=True)

    class Meta:
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')

    def __str__(self):
        return "%s - %s | %s" % (self.admission, self.admission.institution.name, self.price)


class InvoiceItem(models.Model):
    admission = models.ForeignKey(Admission, models.PROTECT, verbose_name=_('Admission'))
    invoice = models.ForeignKey(Invoice, models.SET_NULL, verbose_name=_('Invoice'),
                                null=True, blank=True)
    name = models.TextField(_('Name'))
    amount = models.IntegerField(_('Amount'))
    quantity = models.IntegerField(_('Quantity'), default=1)
    total = models.IntegerField(_('Line total'))
    timestamp = models.DateTimeField(_('Definition date'), editable=False, auto_now_add=True)

    class Meta:
        verbose_name = _('Invoice Item')
        verbose_name_plural = _('Invoice Items')

    def __str__(self):
        return "%s | %s " % (self.name, self.total)
