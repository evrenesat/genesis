from django.shortcuts import render, render_to_response
from django.http import HttpResponse

from lab.models import Admission
from lab.models import Analyse


def index(request):
    return HttpResponse("foo")


def analyse_barcode(request, pk):
    analyse = Analyse.objects.get(pk=pk)
    return render(request, 'barcode_analyse.html', {
        'analyse': analyse,
        'barcode': str(analyse.id).zfill(13)
    })

def analyse_report(request, pk):
    analyse = Analyse.objects.get(pk=pk)
    return render(request, 'barcode_analyse.html', {
        'analyse': analyse,
        'barcode': str(analyse.id).zfill(13)
    })


def admission_barcode(request, pk):
    admission = Admission.objects.get(pk=pk)
    return render(request, 'barcode_admission.html', {
        'analyse': admission,
        'barcode': str(admission.id).zfill(13)
    })
