import json
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context
from django.views.decorators.cache import cache_control

from lab.lib import load_analyse_template, render_report, get_base_context, render_combo_report
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


@login_required
def analyse_report(request, pk):
    content = render_report(pk)
    return HttpResponse(content)



@login_required
def multiple_reports(request):
    ids = request.GET.get('ids').split(',')
    content = render_combo_report(ids)
    return HttpResponse(content)

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
