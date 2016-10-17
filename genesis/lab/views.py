import json

from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import Context
from django.template import Template

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
    anl_tpl = analyse.type.reporttemplate_set.all()[0].template
    with open('templates/report_base.html') as fh:
        base_template = fh.read()
        btpl = base_template.replace('{report_template}', anl_tpl)
        tpl = Template(btpl)
    fh.close()
    cnt_dict = json.loads(analyse.result_json) if analyse.result_json else {}
    cnt_dict['yorum'] = analyse.comment
    c = Context(cnt_dict)

    return HttpResponse(tpl.render(c))


def admission_barcode(request, pk):
    admission = Admission.objects.get(pk=pk)
    return render(request, 'barcode_admission.html', {
        'admission': admission,
        'barcode': str(admission.id).zfill(13)
    })
