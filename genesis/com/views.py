# -*- coding: utf-8 -*-
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
# Create your views here.
from com.models import Invoice, Payment
from com.num2text import num2text
from lab.models import Admission

# from num2words.lang_TR import Num2Word_TR as N2W

TAX_RATE = Decimal(8)


def add_tax_to(admission, invoice):

    pricing = admission.admissionpricing
    invoice.amount = pricing.list_price
    if pricing.tax_included:
        invoice.total = pricing.final_amount
        invoice.subtotal = (pricing.final_amount * Decimal(100)) / (Decimal(100) + TAX_RATE)
    else:
        # if pricing.final_amount != pricing.list_price:  # pre-tax discount applied
        invoice.subtotal = pricing.final_amount
        invoice.total = (invoice.subtotal * (100 + TAX_RATE)) / 100
        payment = Payment.objects.get(admission=admission, method=10, type=10)
        payment.amount = -invoice.total
        payment.save()
    invoice.tax = invoice.total - invoice.subtotal
    invoice.discount = invoice.subtotal - invoice.amount
    invoice.save()


def prepare_invoice_for(admission):
    invoice = None
    error = None
    if not admission.patient.address:
        error = _('Customer address is missing')
    if error is None:
        invoice_set = list(admission.invoice_set.all())
        if invoice_set:
            invoice = invoice_set[0]
            add_tax_to(admission, invoice)
        else:
            invoice = Invoice(name=admission.patient.full_name(50),
                              address=admission.patient.address)
            add_tax_to(admission, invoice)
            invoice.admission.add(admission)
        for item in admission.invoiceitem_set.all():
            if not item.invoice:
                item.invoice = invoice
                item.save()
    return invoice, error


@login_required
def invoice_id_of_admission(request, pk):
    admission = Admission.objects.get(pk=pk)
    invoice_set = list(admission.invoice_set.all())
    if invoice_set:
        invoice_id = invoice_set[0].id
    else:
        invoice_id = 0
    return JsonResponse({'id': invoice_id})


@login_required
def print_invoice_by_admission(request, pk):
    admission = Admission.objects.get(pk=pk)
    invoice, error = prepare_invoice_for(admission)
    return print_invoice(invoice, request, error)


@login_required
def print_invoice_by_id(request, pk):
    invoice = Invoice.objects.get(pk=pk)
    return print_invoice(invoice, request)


@login_required
def next_invoice_id(request):
    c = connection.cursor()
    c.execute("select nextval('com_invoice_id_seq');")
    next_invoice_id = c.fetchone()[0]
    return JsonResponse({'id': next_invoice_id})


def print_invoice(invoice, request, error=None):
    if error:
        return render(request, 'invoice.html', {'error': error})
    integ, decim = str(invoice.total).split('.')
    text_total_int = num2text(int(integ))
    text_total_decimal = num2text(int(decim))
    return render(request, 'invoice.html', {
        'error': error,
        # 'admission': admission,
        'items': invoice.invoiceitem_set.all(),
        'invoice': invoice,
        'text_total_int': text_total_int,
        'text_total_decimal': text_total_decimal,
    })
