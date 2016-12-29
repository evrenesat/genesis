import json
from datetime import datetime

from django import forms
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from lab.models import Admission, ParameterKey, StateDefinition, User
from lab.models import Analyse
from django.contrib.auth import login
from lab.utils import tlower
from lab.utils import tupper


# TODO: unused why???
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
        # this is a mess, just to be able to properly handle the "iİ" problem
        qs = qs.filter(Q(patient__name__contains=tupper(by_word)) |
                       Q(patient__surname__contains=tupper(by_word)) |
                       Q(patient__name__contains=tlower(by_word)) |
                       Q(patient__surname__contains=tlower(by_word)) |
                       Q(patient__name__icontains=tlower(by_word)) |
                       Q(patient__surname__icontains=tlower(by_word)))
    elif by_no:
        qs = (qs.filter(pk=by_no) | qs.filter(patient__tcno__contains=by_no))
    return JsonResponse(
        {'items': [_get_admission(admission=adm, add_analyse=False) for adm in qs[:20]]})


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
def analyse_state_comments_for_statetype(request, pk):
    return JsonResponse(StateDefinition.comment_autocomplete_data(pk))


@staff_member_required
def get_admission(request, pk):
    return JsonResponse(_get_admission(pk))


def _get_analysis(admission):
    analyses = []
    for analyse in admission.analyse_set.all():
        try:
            analyses.append(_get_analyse(analyse, {'current_state': True}))
        except AttributeError:
            pass
    return analyses
