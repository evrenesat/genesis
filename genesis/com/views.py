from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from com.models import Invoice
from lab.models import Admission

TAX_RATE = Decimal(8)


@login_required
def print_invoice(request, pk):
    admission = Admission.objects.get(pk=pk)
    institute = admission.institution
    amount = admission.admissionpricing.final_amount

    total = (amount * TAX_RATE) / 100
    invoice, is_new = Invoice.objects.get_or_create(name=institute.name,
                                                    address=institute.address,
                                                    amount=amount,
                                                    total=total,
                                                    tax=TAX_RATE)
    if is_new:
        invoice.admission.add(admission)
        invoice.save()
        for item in admission.invoiceitem_set.all():
            item.invoice = invoice
            item.save()
    return render(request, 'invoice.html', {
        'admission': admission,
        'items': admission.invoiceitem_set.all(),
        'invoice': invoice,
        'invoice_no': invoice.id,
    })
