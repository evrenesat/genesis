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
        'patient_name': analyse.admission.patient.full_name(),
        'admission_time': analyse.admission.timestamp,
        'institution': analyse.admission.institution,
        'barcode': str(analyse.id).zfill(13),
        'is_urgent': analyse.admission.is_urgent,
        'birthdate': analyse.admission.patient.birthdate,
    })


def _get_base_context(analyse):
    data = {
        'patient_name': analyse.admission.patient.full_name(30),
        'report_date': analyse.approve_time,
        'admission_date': analyse.admission.timestamp,
        'birthdate': analyse.admission.patient.birthdate,
        'short_result': analyse.short_result,
        'indications': analyse.admission.indications,
        'pregnancy_week': analyse.admission.week,
        'admission_id': analyse.admission.id,
        'doctor': analyse.admission.doctor,

        'sample_amount': analyse.sample_amount,
        'sample_type': analyse.sample_type,
        'comment': analyse.comment,
        'approved': analyse.approved,
        'approver': analyse.approver,
        'analyser': analyse.analyser,
        'finished': analyse.finished,
    }
    if str(analyse.admission.doctor) != str(analyse.admission.institution):
        data['institution']= analyse.admission.institution
    return data


def analyse_report(request, pk):
    analyse = Analyse.objects.get(pk=pk)
    cnt_dict = _get_base_context(analyse)
    if analyse.result_json:
        result = analyse.get_result_dict()
        cnt_dict.update(result)
        cnt_dict['results'] = [result]
    c = Context(cnt_dict)
    tpl, tpl_object = _load_analyse_template(analyse)
    return HttpResponse(tpl.render(c))


def _load_analyse_template(analyse, **kwargs):
    if analyse.template and not kwargs:
        anl_tpl = analyse.template
    else:
        anl_tpl = analyse.type.reporttemplate_set.filter(**kwargs)[0]
    fh = open('templates/report_base.html')
    base_template = fh.read()
    fh.close()
    btpl = base_template.replace('{report_template}', anl_tpl.template)
    return Template(btpl), anl_tpl


def multiple_reports(request):
    ids = request.GET.get('ids').split(',')
    analyse_results = []
    for id in ids:
        analyse = Analyse.objects.get(pk=id)
        result = analyse.get_result_dict()
        analyse_results.append(result)
    tpl, tpl_object = _load_analyse_template(analyse, combo=True)
    cnt_dict = _get_base_context(analyse)
    cnt_dict.update({'results': analyse_results,
                     'comment': analyse.comment,
                     'short_result': analyse.short_result,
                     'report_title': tpl_object.title
                     })

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
        'patient_name': admission.patient.full_name(),
        'admission_time': admission.timestamp,
        'institution': admission.institution,
        'barcode': str(admission.id).zfill(13),
        'is_urgent': admission.is_urgent,
        'birthdate': admission.patient.birthdate,
    })
