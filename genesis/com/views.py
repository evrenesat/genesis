# -*- coding: utf-8 -*-
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
# Create your views here.
from com.models import Invoice, Payment
from com.num2text import num2text
from lab.models import Admission
# from num2words.lang_TR import Num2Word_TR as N2W

TAX_RATE = Decimal(8)




def add_tax_to(admission, invoice):
    payment = Payment.objects.get(admission=admission, method=10, type=10)
    taxed_amount = (admission.admissionpricing.final_amount * (100 + TAX_RATE)) / 100
    payment.amount = -taxed_amount
    payment.save()
    invoice.amount = admission.admissionpricing.final_amount
    invoice.tax = taxed_amount - admission.admissionpricing.final_amount
    invoice.total = taxed_amount
    invoice.save()



@login_required
def print_invoice(request, pk):
    error = None
    invoice = None
    admission = Admission.objects.get(pk=pk)
    if not admission.patient.address:
        error = _('Customer address is missing')
    if error is None:
        invoice_set = list(admission.invoice_set.all())
        if invoice_set:
            invoice = invoice_set[0]
        else:
            invoice = Invoice(name=admission.patient.full_name(50),
                              address=admission.patient.address)
            add_tax_to(admission, invoice)
            invoice.admission.add(admission)
            for item in admission.invoiceitem_set.all():
                item.invoice = invoice
                item.save()
        integ, decim = str(invoice.total).split('.')
        text_total_int = num2text(int(integ))
        text_total_decimal = num2text(int(decim))
    return render(request, 'invoice.html', {
        'error': error,
        'admission': admission,
        'items': admission.invoiceitem_set.all(),
        'invoice': invoice,
        'text_total_int': text_total_int,
        'text_total_decimal': text_total_decimal,
    })
