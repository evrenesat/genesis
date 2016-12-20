from decimal import Decimal
from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from django.db import IntegrityError

# Create your models here.
from lab.models import Admission, AnalyseType, Institution
from lab.models import Analyse
from lab.models import Patient


class InstitutePricing(models.Model):
    """
    base price discounts per institute
    """
    institution = models.OneToOneField(Institution, models.PROTECT, verbose_name=_('Institution'))
    discount_rate = models.DecimalField(_('Discount rate'), max_digits=6, decimal_places=2,
                                        null=True, blank=True)
    use_alt_pricing = models.BooleanField(_('Alt. Pricing'), default=False,
                                          help_text=_('Use alternative price'))
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
    (5, _('Expense (-)')),
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
    admission = models.ForeignKey(Admission, models.CASCADE, null=True, blank=True,
                                  verbose_name=_('Admission'))
    patient = models.ForeignKey(Patient, models.PROTECT,
                                verbose_name=_('Patient'), null=True, blank=True)
    institution = models.ForeignKey(Institution, models.PROTECT,
                                    verbose_name=_('Institution'), null=True, blank=True)
    method = models.SmallIntegerField(_('Payment method'), choices=PAYMENT_METHODS, default=30)
    type = models.SmallIntegerField(_('Record type'), choices=PAYMENT_TYPES, default=20)
    amount = models.DecimalField(_('Amount'), max_digits=8, decimal_places=2, null=True, blank=True)
    timestamp = models.DateTimeField(_('Definition date'), editable=False, auto_now_add=True)

    class Meta:
        verbose_name = _('Payment Record')
        verbose_name_plural = _('Payment Records')

    def save(self, *args, **kwargs):
        if (not self.id and self.type == 10 and self.method == 10 and Payment.objects.filter(
                admission=self.admission, type=10, method=10).exists()):
            raise IntegrityError(_('Only one sell payment can exist per admission'))
        if (hasattr(self.admission.institution, 'institutepricing') and
                self.admission.institution.institutepricing.open_account):
            self.institution = self.admission.institution
        else:
            self.patient = self.admission.patient
        if self.type == 10 and (self.amount and self.amount > 0):
            self.amount = 0 - self.amount
        super().save(*args, **kwargs)

    def __str__(self):
        if self.patient:
            return "%s %s" % (self.patient.name, self.amount)
        else:
            return "%s %s" % (self.institution.name, self.amount)


class AdmissionPricing(models.Model):
    admission = models.OneToOneField(Admission, models.CASCADE, verbose_name=_('Admission'))
    tax_included = models.BooleanField(_('Tax included'), default=False)
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

    # final_amount_shadow = models.DecimalField(editable=False, max_digits=8, decimal_places=2,
    #                                           null=True, blank=True)

    class Meta:
        verbose_name = _('Admission Pricing')
        verbose_name_plural = _('Admission Pricings')

    def __str__(self):
        return "%s %s" % (self.admission, self.final_amount)

    def charge_customer(self):
        if (hasattr(self.admission.institution, 'institutepricing') and
                self.admission.institution.institutepricing.open_account):
            institution = self.admission.institution
            patient = None
        else:
            patient = self.admission.patient
            institution = None
        payment, is_new = Payment.objects.update_or_create({'amount': self.final_amount,
                                                            'institution': institution, },
                                                           admission=self.admission,
                                                           patient=patient,
                                                           method=10, type=10)

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
        for analyse in self.admission.analyse_set.all():
            if not hasattr(analyse,'type'):
                continue
            if not analyse.group_relation or analyse.group_relation == 'GRP':
                # this is not a group member (sub-analysis) so we should count it in our price calc.
                discounted_price, list_price, discount_rate = self.calculate_pricing_for(analyse)
                InvoiceItem.objects.get_or_create(admission=self.admission, name=analyse.type.name,
                                                  defaults=dict(amount=discounted_price,
                                                                quantity=1, total=discounted_price))

        self.list_price = InvoiceItem.objects.filter(admission=self.admission).aggregate(Sum('total'))['total__sum']
        if not self.final_amount:
            self.final_amount = self.list_price

    def _calculate_discount(self):
        if not self.list_price or not self.final_amount:
            return
        if not self.tax_included:
            self.discount_amount = self.list_price - self.final_amount
        else:
            self.discount_amount = self.list_price - self.final_amount * Decimal(0.92)  # FIXME: TAX_RATE
        if self.final_amount and self.discount_amount:
            self.discount_percentage = Decimal(float(str(self.final_amount)) /
                                               float(str(self.list_price)))

            # def save(self, *args, **kwargs):
            #     super().save(*args, **kwargs)
            # if not self.final_amount:

    def process_payments(self):
        self.process_amounts_and_create_invoiceitems()
        self.charge_customer()
        self._calculate_discount()
        self.save()


DEFAULT_INVOICE_UNIT = 'Adet'


class Invoice(models.Model):
    admission = models.ManyToManyField(Admission, verbose_name=_('Admission'), editable=False)
    name = models.CharField(_('Name'), null=True, blank=True, max_length=250)
    address = models.TextField(_('Address'), null=True, blank=True, max_length=250)

    amount = models.DecimalField(_('Total'), max_digits=8, decimal_places=2,
                                 null=True, blank=True)
    discount = models.DecimalField(_('Discount'), max_digits=6, decimal_places=2, null=True,
                                   blank=True)
    subtotal = models.DecimalField(_('SubTotal'), max_digits=8, decimal_places=2,
                                   null=True, blank=True)
    tax = models.DecimalField(_('Tax amount'), null=True, blank=True, max_digits=8,
                              decimal_places=2)
    total = models.DecimalField(_('Grand Total'), max_digits=8, decimal_places=2,
                                null=True, blank=True)
    timestamp = models.DateTimeField(_('Definition date'), auto_now_add=True)

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "amount__iexact", "name__icontains", "address__icontains")

    class Meta:
        verbose_name = _('Invoice')
        verbose_name_plural = _('Invoices')

    def __str__(self):
        return "%s - %s" % (self.name, self.total)


class InvoiceItem(models.Model):
    admission = models.ForeignKey(Admission, models.CASCADE, verbose_name=_('Admission'))
    invoice = models.ForeignKey(Invoice, models.SET_NULL, verbose_name=_('Invoice'),
                                null=True, blank=True)
    name = models.CharField(_('Item name'), max_length=255)
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
