import json
from datetime import datetime

from django.core import serializers
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context
from django.views.decorators.cache import cache_control

from lab.lib import load_analyse_template, render_report, get_base_context, render_combo_report
from lab.models import Admission, ParameterKey, StateDefinition
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
def choices_for_parameter(request, pk):
    pk = ParameterKey.objects.get(parametervalue=pk)
    return JsonResponse({
        'presets': json.loads(pk.presets),
        'has_preset': True if pk.presets else False
    })


@login_required
def get_admissions(request):
    queryset = Admission.objects.filter(**request.GET.copy())
    return HttpResponse(serializers.serialize('json', queryset[:10]),
                        content_type='application/json')


@login_required
def get_analyses(request):
    queryset = Analyse.objects.filter(**request.GET.copy())
    return HttpResponse(serializers.serialize('json', queryset[:10]),
                        content_type='application/json')


@login_required
def get_admissions_by_analyses(request):
    admissions = set()
    query = dict(
        (k, (v == 'True' if v in ('False', 'True') else v)) for k, v in request.GET.items())
    for adm_id in Analyse.objects.filter(**query).values_list('admission_id', flat=True):
        admissions.add(adm_id)
        if len(admissions) == 10:
            break

    data = {'admissions': []}
    for adm in Admission.objects.filter(id__in=list(admissions)):
        data['admissions'].append({
            'title': adm.patient.full_name(),
            'state': adm.analyse_state(),
            'id': adm.id,
        })
    return JsonResponse(data)

@login_required
def analyse_state_comments_for_statetype(request, pk):
    return JsonResponse(StateDefinition.comment_autocomplete_data(pk))


@login_required
def multiple_reports(request):
    ids = request.GET.get('ids').split(',')
    content = render_combo_report(ids)
    return HttpResponse(content)


@login_required
def multiple_reports_for_panel(request, group_code):
    ids = Analyse.objects.filter(group_relation=group_code).values_list('id', flat=True)
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
