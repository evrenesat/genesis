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
        'id': analyse.id,
        'admission_id': analyse.admission_id,
        'patient_name': analyse.admission.patient.full_name,
        'admission_time': analyse.admission.timestamp,
        'institution': analyse.admission.institution,
        'barcode': str(analyse.id).zfill(13),
        'is_urgent': analyse.admission.is_urgent,
        'birthdate': analyse.admission.patient.birthdate,
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
    cnt_dict['comment'] = analyse.comment
    c = Context(cnt_dict)

    return HttpResponse(tpl.render(c))


def _load_analyse_template(analyse):
    anl_tpl = analyse.type.reporttemplate_set.all()[0].template
    fh = open('templates/report_base.html')
    base_template = fh.read()
    fh.close()
    btpl = base_template.replace('{report_template}', anl_tpl)
    return Template(btpl)


def multiple_reports(request):
    ids = request.GET.get('ids').split(',')
    analyse_results = []
    for id in ids:
        analyse = Analyse.objects.get(pk=id)
        analyse_results.append(json.loads(analyse.result_json) if analyse.result_json else {})
    tpl = _load_analyse_template(analyse)
    cnt_dict = {'results': analyse_results,
                'comment': analyse.comment}
    c = Context(cnt_dict)

    return HttpResponse(tpl.render(c))


def admission_barcode(request, pk):
    admission = Admission.objects.get(pk=pk)
    return render(request, 'barcode_admission.html', {
        'analyses': [an.get_code for an in admission.analyse_set.all()],
        'admission': admission,
        'id': admission.id,
        'admission_id': admission.id,
        'person_id': admission.patient.tcno,
        'patient_name': admission.patient.full_name,
        'admission_time': admission.timestamp,
        'institution': admission.institution,
        'barcode': str(admission.id).zfill(13),
        'is_urgent': admission.is_urgent,
        'birthdate': admission.patient.birthdate,
    })
