import json
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from django.template import Context
from django.template import Template
from django.views.decorators.cache import cache_control

from lab.models import Admission
from lab.models import Analyse

@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def analyse_check(request):
    patient_id = int(request.GET.get('pid'))
    admission_id = int(request.GET.get('aid'))
    birthdate = datetime.strptime(request.GET.get('bdt', '01.01.2001'), '%d.%m.%Y')
    try:
        admission = Admission.objects.get(patient__id=patient_id, id=admission_id,
                                          patient__birthdate=birthdate)

    except ObjectDoesNotExist:
        return HttpResponse(content=_('Wrong patient information. No record found'))
    if admission.is_approved():
        result = _('Your analyse results are ready. Please contact with your doctor.')
    else:
        result = _('Your analyses are still in progress.')
    return HttpResponse(content=result)

@login_required
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
        'note': analyse.type.footnote,
    }
    if str(analyse.admission.doctor) != str(analyse.admission.institution):
        data['institution']= analyse.admission.institution
    return data

def _render_report(pk):
    analyse = Analyse.objects.get(pk=pk)
    cnt_dict = _get_base_context(analyse)
    if analyse.result_json:
        result = analyse.get_result_dict()
        cnt_dict.update(result)
        cnt_dict['results'] = [result]
    cnt_dict['multi'] = False
    tpl, tpl_object = _load_analyse_template(analyse)
    cnt_dict['generic'] = True
    return tpl.render(Context(cnt_dict))

@login_required
def analyse_report(request, pk):
    content = _render_report(pk)
    return HttpResponse(content)


def _load_analyse_template(analyse, **kwargs):
    if analyse.template and not kwargs:
        anl_tpl = analyse.template
    else:
        if 'combo' not in kwargs:
            kwargs['combo'] = False
        anl_tpl = analyse.type.reporttemplate_set.filter(**kwargs)
        if anl_tpl:
            anl_tpl = anl_tpl[0]
        else:
            anl_tpl = None
    fh = open('templates/report_base.html')
    base_template = fh.read()
    fh.close()
    btpl = base_template.replace('{report_template}', anl_tpl.template if anl_tpl else '')
    return Template(btpl), anl_tpl

@login_required
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
                     'multi': True,
                     })
    if tpl_object:
        cnt_dict.update({
            'report_title': tpl_object.title,
            'generic': tpl_object.generic,
        })
    else:
        cnt_dict.update({
            'report_title': '',
            'generic': True,
        })

    c = Context(cnt_dict)

    return HttpResponse(tpl.render(c))

@login_required
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
