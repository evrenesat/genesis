import json
from datetime import datetime

from django import forms
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core import serializers
from django.db.models import Q
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import HttpResponse
from django.template import Context
from django.views.decorators.cache import cache_control

from lab.lib import load_analyse_template, render_report, get_base_context, render_combo_report
from lab.models import Admission, ParameterKey, StateDefinition, User, Setting
from lab.models import Analyse
from django.contrib.auth import login
from lab.utils import tlower
from lab.utils import tupper


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
    by_no = int(request.GET.get('by_no', 0))
    by_word = request.GET.get('by_word', None)
    qs = Admission.objects
    if by_word:
        qs = qs.filter(Q(patient__name__contains=tupper(by_word))|Q(patient__surname__contains=tupper(by_word))|
                       Q(patient__name__contains=tlower(by_word)) | Q(patient__surname__contains=tlower(by_word))|
                       Q(patient__name__icontains=tlower(by_word)) | Q(patient__surname__icontains=tlower(by_word)))
    elif by_no:
        qs = (qs.filter(pk=by_no) | qs.filter(patient__tcno__contains=by_no))
    return JsonResponse({'items':[_get_admission(admission=adm, add_analyse=False) for adm in qs[:20]]})


def _get_analyse(analyse, state_filter=None):
    state_filter = state_filter or {}
    return {
        'id': analyse.id,
        'name': analyse.type.name,
        'admission_id': analyse.admission.id,
        'person_id': analyse.admission.patient.tcno,
        'patient_name': analyse.admission.patient.full_name(),
        'institution': analyse.admission.institution.name,
        'is_urgent': analyse.admission.is_urgent,
        'birthdate': analyse.admission.patient.birthdate,
        'timestamp': analyse.admission.timestamp,
        'category': analyse.type.category.name if analyse.type.category else '-',
        'sample_type': analyse.sample_type.name if analyse.sample_type else '-',
        'external': analyse.external_lab.name if analyse.external else '-',
        'states': list(
            analyse.state_set.filter(**state_filter).values('definition__name',
                                                                'timestamp',
                                                                'personnel__user__username',
                                                                'comment',
                                                                'group'))
    }

@staff_member_required
def get_analyse(request, pk):
    return JsonResponse(_get_analyse(Analyse.objects.get(pk=pk)))


@staff_member_required
def list_analysis(request):
    queryset = Analyse.objects.filter(**request.GET.copy())
    return JsonResponse()


@staff_member_required
def get_user_info(request):
    return JsonResponse({
        'fullname': request.user.get_full_name(),
        'username': request.user.username,
        'fist_name': request.user.first_name,
        'other_users': [{'username': u.username, 'fullname': u.get_full_name()}
                        for u in request.user.__class__.objects.exclude(pk=request.user.id,
                                                                        is_superuser=True)]
    })


@staff_member_required
def switch_user(request):
    user = User.objects.get(username=request.GET.get('username'), is_superuser=False)
    login(request, user, backend=settings.AUTHENTICATION_BACKENDS[0])
    return JsonResponse({'result': 'success'})


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
        # if len(admissions) == 20:
        #     break

    data = {'admissions': []}
    for admission in Admission.objects.filter(id__in=list(admissions)).order_by('-is_urgent'):
        data['admissions'].append({
            'title': admission.patient.full_name(),
            'state': admission.analyse_state(),
            'id': admission.id,
            'admission_id': admission.id,
            'person_id': admission.patient.tcno,
            'patient_name': admission.patient.full_name(),
            'institution': admission.institution.name,
            'is_urgent': admission.is_urgent,
            'birthdate': admission.patient.birthdate,
            'timestamp': admission.timestamp,
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
            analyses.append(_get_analyse(analyse, {'current_state':True}))
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
        'title': admission.patient.full_name(),
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
    print_analyses = request.GET.get('print_analyses', False)
    admission = Admission.objects.get(pk=pk)
    analyses = set()
    num_of_analyses = 0
    analyse_ids = []
    for analyse in admission.analyse_set.all():
        try:
            num_of_analyses += 1
            if print_analyses and analyse.type.barcode_count:
                analyse_ids.append(str(analyse.id))
            print(analyse.type.category, '||', analyse.sample_type)
            analyses.add((analyse.type.category.get_code(),
                          analyse.sample_type.get_code(),
                          analyse.external_lab.get_code() if analyse.external else ''
                          )
                         )
        except AttributeError:
            pass
    context = {
        'num_of_analyses': num_of_analyses,
        'barcode_num_copies': Setting.get_val('bcpno', 1),
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
        'birthdate': admission.patient.birthdate}

    if print_analyses and analyse_ids:
        context.update({'analyse_set': ','.join(analyse_ids),
                        'next': analyse_ids[0],
                        })
    return render(request, 'barcode_admission.html', context)


@staff_member_required
def analyse_barcode(request, pk):
    # return admission_barcode(request,
    #                          Analyse.objects.filter(pk=pk).values_list('admission_id', flat=True)[
    #                              0])
    _set = request.GET.get('set', '')
    next = None
    set_list = _set.split(',')
    if _set:
        try:
            next = set_list[set_list.index(str(pk)) + 1]
        except IndexError:
            pass
    analyse = Analyse.objects.get(pk=pk)
    return render(request, 'barcode_analyse.html', {
        'analyse': analyse,
        'id': analyse.id,
        'barcode_num_copies': analyse.type.barcode_count,
        'admission_id': analyse.admission_id,
        'patient_name': analyse.admission.patient.full_name(),
        'admission_time': analyse.admission.timestamp,
        'institution': analyse.admission.institution,
        'barcode': '9' + (str(analyse.id).zfill(12))[1:],
        'is_urgent': analyse.admission.is_urgent,
        'birthdate': analyse.admission.patient.birthdate,
        'analyse_set': _set,
        'next': next,
    })


class Report(forms.Form):
    from_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'vDateField'}),
                                required=False)
    to_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'vDateField'}), required=False)
