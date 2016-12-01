from decimal import Decimal
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.
from lab.models import Admission, AnalyseType, Institution
from lab.models import Analyse
from lab.models import Patient


class InstitutePricing(models.Model):
    """
    base price discounts per institute
    """
    institution = models.OneToOneField(Institution, models.PROTECT, verbose_name=_('Institution'))
    discount_rate = models.DecimalField(_('Discount rate'), max_digits=6, decimal_places=2)
    use_alt_pricing = models.BooleanField(_('Use alternative price'), default=False)
    open_account = models.BooleanField(_('Open account'), default=False,
                                       help_text=_('This institution makes mountly payments'))
    timestamp = models.DateTimeField(_('Definition date'), editable=False, auto_now_add=True)

    class Meta:
        verbose_name = _('Institue Pricing')
        verbose_name_plural = _('Institue Pricings')

    def __str__(self):
        return "%s %s" % (self.institution.name, self.discount_rate)


class AnalysePricing(models.Model):
    """
    per analyse pricing or percentage discounts for an institution.

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
        unique_together = (('institution', 'analyse_type'), ('pricing', 'analyse_type'),)

    def __str__(self):
        return "%s > %s" % (self.analyse_type.name, self.institution.name)


PAYMENT_TYPES = (
    (10, _('Customer debt (-)')),
    (20, _('Customer payment (+)')),
)

PAYMENT_METHODS = (
    (10, _('Sell')),
    (30, _('Cash')),
    (40, _('Credit Card')),
    (50, _('Bank transfer')),
)


class Payment(models.Model):
    """
    this is a payment record for an admission.
    there can be multiple payments for one admission (multiple credit card payments + cash)
    """
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
        return "%s %s" % (self.patient.name, self.amount)


class AdmissionPricing(models.Model):
    admission = models.OneToOneField(Admission, models.PROTECT, verbose_name=_('Admission'))
    timestamp = models.DateTimeField(_('Definition date'), editable=False, auto_now_add=True)
    list_price = models.DecimalField(_('List price'), max_digits=8, decimal_places=2,
                                     editable=False, null=True, blank=True)
    discount_percentage = models.DecimalField(_('Discount percentage'), max_digits=8, null=True,
                                              decimal_places=2, editable=False, blank=True)
    discount_amount = models.DecimalField(_('Discount amount'), max_digits=8, decimal_places=2,
                                          editable=False, null=True, blank=True)
    final_amount = models.DecimalField(_('Customer price'), max_digits=8, decimal_places=2,
                                       null=True,
                                       blank=True)

    class Meta:
        verbose_name = _('Admission Pricing')
        verbose_name_plural = _('Admission Pricings')

    def __str__(self):
        return "%s %s" % (self.admission, self.final_amount)

    def charge_customer(self):
        payment, is_new = Payment.objects.get_or_create(admission=self.admission,
                                                        patient=self.admission.patient,
                                                        method=10, type=10,
                                                        institution=self.admission.institution,
                                                        defaults=dict(amount=self.final_amount))

    def calculate_pricing_for(self, analyse):
        """
        Get analyse price and discount rate for this admission.institute

        Args:
            analyse: Analyse object

        Returns:
            tuple, (discounted price, list price, discount rate)
        """
        institute = self.admission.institution
        analyse_price = institute.analysepricing_set.filter(analyse_type=analyse.type)
        if analyse_price:
            return analyse_price[0].price, analyse_price[0].discount_rate
        use_alt_pricing = False
        institute_discount_rate = None
        if hasattr(institute, 'institutepricing'):
            use_alt_pricing = institute.institutepricing.use_alt_pricing
            # TODO: convert percentage to decimal
            institute_discount_rate = institute.institutepricing.discount_rate
        list_price = analyse.type.alternative_price if use_alt_pricing else analyse.type.price
        discounted_price = list_price * (institute_discount_rate or 1)
        return discounted_price, list_price, institute_discount_rate

    def process_amounts_and_create_invoiceitems(self):
        self.final_amount = Decimal(0)
        self.list_price = Decimal(0)
        for analyse in self.admission.analyse_set.all():
            if analyse.group_relation != 30:  # if this is not a group member (sub-analysis)
                discounted_price, list_price, discount_rate = self.calculate_pricing_for(analyse)
                InvoiceItem.objects.get_or_create(admission=self.admission, name=analyse.type.name,
                                                  defaults=dict(amount=discounted_price,
                                                                quantity=1, total=discounted_price))
                self.final_amount += discounted_price
                self.list_price += list_price
            if analyse.group_relation == 20:  # if this is a group, delete it
                analyse.delete()

    def _calculate_discount(self):
        self.discount_amount = self.list_price - self.final_amount
        if self.final_amount and self.discount_amount:
            self.discount_percentage = Decimal(float(str(self.final_amount)) /
                                               float(str(self.list_price)))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.final_amount:
            self.process_amounts_and_create_invoiceitems()
            self.charge_customer()
        self._calculate_discount()
        super().save(*args, **kwargs)


DEFAULT_INVOICE_UNIT = 'Adet'


class Invoice(models.Model):
    admission = models.ManyToManyField(Admission, verbose_name=_('Admission'), editable=False)
    name = models.CharField(_('Name'), null=True, blank=True, max_length=250)
    address = models.TextField(_('Address'), null=True, blank=True, max_length=250)

    amount = models.DecimalField(_('Total'), max_digits=8, decimal_places=2,
                                 null=True, blank=True)
    tax = models.DecimalField(_('Tax amount'), null=True, blank=True, max_digits=8,
                              decimal_places=2)
    total = models.DecimalField(_('Grand Total'), max_digits=8, decimal_places=2,
                                null=True, blank=True)
    timestamp = models.DateTimeField(_('Definition date'), auto_now_add=True)

    class Meta:
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')

    def __str__(self):
        return "%s - %s" % (self.name, self.total)


class InvoiceItem(models.Model):
    admission = models.ForeignKey(Admission, models.PROTECT, verbose_name=_('Admission'))
    invoice = models.ForeignKey(Invoice, models.SET_NULL, verbose_name=_('Invoice'),
                                null=True, blank=True)
    name = models.CharField(_('Name'), max_length=255)
    amount = models.DecimalField(_('Amount'), max_digits=6, decimal_places=2)
    quantity = models.IntegerField(_('Quantity'), default=1)
    unit = models.CharField(_('Unit'), default=DEFAULT_INVOICE_UNIT, max_length=30)
    total = models.DecimalField(_('Line total'), max_digits=6, decimal_places=2)
    timestamp = models.DateTimeField(_('Definition date'), editable=False, auto_now_add=True)

    class Meta:
        verbose_name = _('Invoice Item')
        verbose_name_plural = _('Invoice Items')

    def __str__(self):
        return "%s | %s " % (self.name, self.total)
