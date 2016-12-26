import json
from datetime import datetime

from django import forms
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
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
from lab.models import Admission, ParameterKey, StateDefinition, User
from lab.models import Analyse
from django.contrib.auth import login

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


@staff_member_required
def analyse_barcode(request, pk):
    return admission_barcode(request,
                             Analyse.objects.filter(pk=pk).values_list('admission_id', flat=True)[
                                 0])
    analyse = Analyse.objects.get(pk=pk)
    return render(request, 'barcode_analyse.html', {
        'analyse': analyse,
        'id': analyse.id,
        'admission_id': analyse.admission_id,
        'patient_name': analyse.admission.patient.full_name(),
        'admission_time': analyse.admission.timestamp,
        'institution': analyse.admission.institution,
        'barcode': str(analyse.id).zfill(11),
        'is_urgent': analyse.admission.is_urgent,
        'birthdate': analyse.admission.patient.birthdate,
    })


@staff_member_required
def analyse_report(request, pk):
    content = render_report(pk)
    return HttpResponse(content)


@staff_member_required
def choices_for_parameter(request, pk):
    pk = ParameterKey.objects.get(parametervalue=pk)
    return JsonResponse({
        'presets': json.loads(pk.presets),
        'has_preset': True if pk.presets else False
    })


@staff_member_required
def get_admissions(request):
    queryset = Admission.objects.filter(**request.GET.copy())
    return JsonResponse([_get_admission(admission=adm, add_analyse=False) for adm in queryset])


@staff_member_required
def get_analyses(request):
    queryset = Analyse.objects.filter(**request.GET.copy())
    return HttpResponse(serializers.serialize('json', queryset[:10]),
                        content_type='application/json')

@staff_member_required
def get_user_info(request):
    return JsonResponse({
        'fullname': request.user.get_full_name(),
        'username': request.user.username,
        'fist_name': request.user.first_name,
        'other_users': [{'username':u.username, 'fullname':u.get_full_name()}
                        for u in request.user.__class__.objects.exclude(pk=request.user.id, is_superuser=True)]
    })

@staff_member_required
def switch_user(request):

    user = User.objects.get(username=request.GET.get('username'), is_superuser=False)
    login(request, user, backend=settings.AUTHENTICATION_BACKENDS[0])
    return JsonResponse({'result':'success'})


@staff_member_required
def get_admissions_by_analyses(request):
    """
    for dashboard boxes
    Args:
        request:

    Returns:

    """
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


@staff_member_required
def analyse_state_comments_for_statetype(request, pk):
    return JsonResponse(StateDefinition.comment_autocomplete_data(pk))


@login_required
def multiple_reports(request):
    ids = request.GET.get('ids').split(',')
    content = render_combo_report(ids)
    return HttpResponse(content)


@staff_member_required
def multiple_reports_for_panel(request, group_code):
    ids = Analyse.objects.filter(group_relation=group_code).values_list('id', flat=True)
    content = render_combo_report(ids)
    return HttpResponse(content)


@staff_member_required
def get_admission(request, pk):
    return JsonResponse(_get_admission(pk))


def _get_analysis(admission):
    analyses = []
    for analyse in admission.analyse_set.all():
        try:
            analyses.append({
                'id': analyse.id,
                'name': analyse.type.name,
                'category': analyse.type.category.name,
                'sample_type': analyse.sample_type.name,
                'external': analyse.external_lab.name if analyse.external else '',
                'states': list(
                    analyse.state_set.filter(current_state=True).values('definition__name',
                                                                        'group'))
            })
        except AttributeError:
            pass
    return analyses


def _get_admission(pk=None, admission=None, add_analyse=True):
    admission = admission or Admission.objects.get(pk=pk)
    analyses = _get_analysis(admission) if add_analyse else []
    return {
        'analyses': analyses,
        'states': admission.analyse_state(raw=True),
        'id': admission.id,
        'admission_id': admission.id,
        'person_id': admission.patient.tcno,
        'patient_name': admission.patient.full_name(),
        'institution': admission.institution.name,
        'is_urgent': admission.is_urgent,
        'birthdate': admission.patient.birthdate,
        'timestamp': admission.timestamp,
    }


@staff_member_required
def admission_barcode(request, pk):
    admission = Admission.objects.get(pk=pk)
    analyses = set()
    for analyse in admission.analyse_set.all():
        try:
            print(analyse.type.category, '||', analyse.sample_type)
            analyses.add((analyse.type.category.get_code(),
                          analyse.sample_type.get_code(),
                          analyse.external_lab.get_code() if analyse.external else ''
                          )
                         )
        except AttributeError:
            pass

    return render(request, 'barcode_admission.html', {
        'analyses': analyses,
        'admission': admission,
        'id': admission.id,
        'admission_id': admission.id,
        'person_id': admission.patient.tcno,
        'patient_name': admission.patient.full_name(),
        'admission_time': admission.timestamp,
        'institution': admission.institution,
        'barcode': str(admission.id).zfill(12),
        'is_urgent': admission.is_urgent,
        'birthdate': admission.patient.birthdate,
    })


class Report(forms.Form):
    from_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'vDateField'}),
                                required=False)
    to_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'vDateField'}), required=False)
