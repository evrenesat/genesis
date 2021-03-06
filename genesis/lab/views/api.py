import json
from datetime import datetime, timedelta

from collections import defaultdict
from django import forms
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Sum, Max, Min, Avg, Count, Q
from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from lab.models import Admission, ParameterKey, StateDefinition, User, AnalyseType, State, \
    ValidationError, Institution
from lab.models import Analyse
from django.contrib.auth import login, logout
from lab.utils import tlower
from lab.utils import tupper
from django.utils import timezone


class JsonError(Exception):
    pass


def _error(msg):
    return JsonResponse({'result': 'Error', 'error': msg})


# TODO: unused why???
@staff_member_required
def choices_for_parameter(request, pk):
    pk = ParameterKey.objects.get(parametervalue=pk)
    return JsonResponse({
        'presets': json.loads(pk.presets),
        'has_preset': True if pk.presets else False
    })


@staff_member_required
def list_analyse_types(request):
    return JsonResponse(
        {'analyse_types': list(AnalyseType.objects.values('name', 'code', 'id', 'category__name'))})


@staff_member_required
def list_analyse_type_states(request, pk):
    return JsonResponse(_list_analyse_type_states(type_id=pk))


def _list_analyse_type_states(**kw):
    if 'analyse_id' in kw:
        kw['analyse'] = Analyse.objects.get(pk=kw['analyse_id'])

    if 'analyse' in kw:
        ids = kw['analyse'].applicable_states_ids()
    elif 'type_id' in kw:
        ids = AnalyseType.objects.get(pk=kw['type_id']).applicable_states_ids()
    elif 'type' in kw:
        ids = kw['type'].applicable_states_ids()

    return {'analyse_type_states':
        list(StateDefinition.objects.filter(pk__in=ids).values(
            'accept', 'approve', 'category', 'explanation', 'finish', 'first',
            'id', 'name', 'order', 'require_double_check'))}


@csrf_exempt
@staff_member_required
def set_analyse_state(request):
    try:
        data = _parse_request_data(request)
        result = _save_state(data)
        if data['analyse'].group_relation == 'GRP':
            for analyse in data['analyse'].analyse_set.all():
                data['analyse_id'] = analyse.id
                _save_state(data)
        return JsonResponse(result)
    except JsonError as e:
        return _error(str(e))


def _parse_request_data(request):
    analyse_id = request.POST.get('analyse')
    analyse_type_id = request.POST.get('analyse_type', None)
    group = int(request.POST.get('group', 1))
    state_id = request.POST.get('state', None)
    definition_id = request.POST.get('state_definition', 0) or None
    admission_id = request.POST.get('admission', None)
    comment = request.POST.get('comment', '')
    if analyse_id:
        analyse = Analyse.objects.get(pk=analyse_id)
        if analyse_type_id and not analyse.type_id != analyse_type_id:
            raise JsonError(_('Selected anaylse type and given analyse does not match'))
    else:
        try:  # to get the analyse from admission by selected type
            analyse = Analyse.objects.get(admission_id=admission_id, type_id=analyse_type_id,
                                                external=False)
            analyse_id = analyse.id
        except ObjectDoesNotExist:
            raise JsonError(_('No analyse found for given admission in selected analyse type'))
    return locals()


def _save_state(kw):
    if kw.get('state_id'):
        state = State.objects.get(pk=kw['state_id'])
    elif kw.get('definition_id'):
        state = State(definition_id=kw['definition_id'], analyse_id=kw['analyse_id'], group=kw['group'])
    else:
        raise JsonError(_('Incomplete data received'))
    if kw.get('comment'):
        state.comment = kw['comment']
    try:
        if state.definition.finish:
            state.analyse.mark_finished(kw['request'])
        if state.definition.approve:
            state.analyse.mark_approved(kw['request'])
    except ValidationError:
        raise JsonError(_("You don't have the required permissions to complete this action."))

    state.personnel = kw['request'].user.profile
    state.save()
    return {'result': 'Success', 'state_id': state.id, 'analyse_id': kw['analyse_id']}


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
        'type': analyse.type_id,
        'name': analyse.type.name,
        'admission_id': analyse.admission.id,
        'person_id': analyse.admission.patient.tcno,
        'patient_name': analyse.admission.patient.full_name(),
        'institution': analyse.admission.institution.name,
        'no_of_groups': analyse.no_of_groups,
        'is_urgent': analyse.admission.is_urgent,
        'finished': analyse.finished,
        'approved': analyse.approved,
        'group_relation': analyse.group_relation,
        'is_grouper': analyse.group_relation == 'GRP',
        'grouper': analyse.grouper_id,
        'birthdate': analyse.admission.patient.birthdate,
        'timestamp': analyse.admission.timestamp,
        'category': analyse.type.category.name if analyse.type.category else '-',
        'sample_type': analyse.sample_type.name if analyse.sample_type else '-',
        'external': analyse.external_lab.name if analyse.external else '-',
        'states': list(
            analyse.state_set.filter(**state_filter).values('definition__name',
                                                            'timestamp',
                                                            'id',
                                                            'personnel__user__username',
                                                            'comment',
                                                            'group'))
    }


@staff_member_required
def get_analyse(request, pk):
    analyse = Analyse.objects.get(pk=pk)
    selected_definition_id = int(request.GET.get('selected_definition_id', 0))
    analyse_dict = _get_analyse(analyse)
    if request.GET.get('add_type_states', None):
        analyse_dict.update(_list_analyse_type_states(analyse=analyse))
    if selected_definition_id:
        analyse_dict.update({'comments':
                                 StateDefinition.comment_autocomplete_data(selected_definition_id)})
    return JsonResponse(analyse_dict)


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
        # 'other_users': [{'username': u.username, 'fullname': u.get_full_name()}
        'other_users': [u.username
                        for u in
                        request.user.__class__.objects.filter(is_active=True, is_staff=True)]
    })


@staff_member_required
def switch_user(request):
    user = User.objects.get(username=request.GET.get('username'), is_superuser=False)
    login(request, user, backend=settings.AUTHENTICATION_BACKENDS[0])
    return JsonResponse({'result': 'success'})


@staff_member_required
def logout_user(request):
    logout(request)
    return JsonResponse({'result': 'success'})


@staff_member_required
def analyse_state_comments_for_statetype(request, pk):
    return JsonResponse(StateDefinition.comment_autocomplete_data(pk))


@staff_member_required
def get_admission(request, pk):
    return JsonResponse(_get_admission(pk, add_analyse=True))


def _get_analysis(admission):
    analyses = []
    # .exclude(group_relation='GRP'):
    for analyse in admission.analyse_set.order_by('-grouper'):
        try:
            analyses.append(_get_analyse(analyse, {'current_state': True}))
        except AttributeError:
            pass
    return analyses


############## STATS & GRAPHS #####################

def _compile_timeseries(input):
    data = defaultdict(int)
    for id, timestamp in input:
        data[timestamp.strftime("%d/%m/%Y")] += 1
    return list(data.items())


# FIXME: Expanding week and month to prevent empty charts
A_W_EARLIER_DELTA = 20
A_M_EARLIER_DELTA = 45


def _most_popular():
    now = timezone.now()

    a_w_earlier = now - timedelta(days=A_W_EARLIER_DELTA)
    a_m_earlier = now - timedelta(days=A_M_EARLIER_DELTA)
    result = {
        'Son 30 Günde En Çok İstenen Testler': {'data': list(
            AnalyseType.objects.filter(analyse__timestamp__range=(a_m_earlier, now)).annotate(
                usage=Count('analyse')).order_by('-usage').values_list('code', 'usage')[:10]),
            'type': 'Pie'},
        'Son 30 Günde En Çok Hasta Gönderen Kurumlar': {'data': list(
            Institution.objects.filter(admission__timestamp__range=(a_m_earlier, now)).annotate(
                usage=Count('admission')).order_by('-usage').values_list('name', 'usage')[:10]),
            'type': 'Pie'},
        'Son 7 Günde En Çok İstenen Testler': {'data': list(
            AnalyseType.objects.filter(analyse__timestamp__range=(a_w_earlier, now)).annotate(
                usage=Count('analyse')).order_by('-usage').values_list('code', 'usage')[:10]),
            'type': 'Pie'},
        'Son 7 Günde En Çok Hasta Gönderen Kurumlar': {'data': list(
            Institution.objects.filter(admission__timestamp__range=(a_w_earlier, now)).annotate(
                usage=Count('admission')).order_by('-usage').values_list('name', 'usage')[:10]),
            'type': 'Pie'},
    }

    return result


@staff_member_required
def dashboard_stats(request):
    data = {}
    data.update(_most_popular())
    data['chart_list'] = list(data.keys())

    now = timezone.now()
    a_w_earlier = now - timedelta(days=A_W_EARLIER_DELTA)
    a_m_earlier = now - timedelta(days=A_M_EARLIER_DELTA)

    series_data = Analyse.objects.filter(timestamp__range=(a_m_earlier, now)).values_list('id',
                                                                                          'timestamp')
    data['Günlük Toplamlar'] = {'data': _compile_timeseries(series_data), 'type': 'Bar'}
    data['chart_list'].append('Günlük Toplamlar')
    return JsonResponse(data)

############## ENDOF STATS & GRAPHS ###############
