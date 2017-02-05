# -*-  coding: utf-8 -*-
"""
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render
from lab.lib import render_combo_report, render_report
from lab.models import Admission, Analyse
from lab.models import Setting


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
                analyse_ids.extend(['%s-%s' % (analyse.id, group) for group in range(1,analyse.no_of_groups+1)])
            # print(analyse.type.category, '||', analyse.sample_type)
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
        context['analyse_set'] = ','.join(analyse_ids)
        context['next'], context['next_group'] = analyse_ids[0].split('-')
    return render(request, 'barcode_admission.html', context)


@staff_member_required
def analyse_barcode(request, pk, group=1):
    # return admission_barcode(request,
    #                          Analyse.objects.filter(pk=pk).values_list('admission_id', flat=True)[
    #                              0])
    # 12-1,12-2,12-3
    _set = request.GET.get('set', '')
    nxt = None
    nxt_grp = None

    analyse = Analyse.objects.get(pk=pk)
    if not _set and analyse.no_of_groups > 1:
        _set = ','.join(['%s-%s' % (analyse.id, group) for group in range(1, analyse.no_of_groups + 1)])
    if _set:
        set_list = _set.split(',')
        try:
            nxt, nxt_grp = set_list[set_list.index('%s-%s' % (pk, group)) + 1].split('-')
        except IndexError:
            pass

    return render(request, 'barcode_analyse.html', {
        'analyse': analyse,
        'id': analyse.id,
        'group': group,
        'no_of_groups': analyse.no_of_groups,
        'barcode_num_copies': analyse.type.barcode_count,
        'admission_id': analyse.admission_id,
        'patient_name': analyse.admission.patient.full_name(),
        'admission_time': analyse.admission.timestamp,
        'institution': analyse.admission.institution,
        'barcode': '9%s%s' % (group, str(analyse.id).zfill(11)[1:]),
        'is_urgent': analyse.admission.is_urgent,
        'birthdate': analyse.admission.patient.birthdate,
        'analyse_set': _set,
        'next': nxt,
        'next_group': nxt_grp,
    })


@staff_member_required
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
def multiple_reports_for_panel_grouper(request, pk):
    ids = Analyse.objects.filter(grouper_id=pk).values_list('id', flat=True)
    content = render_combo_report(ids, grouper=Analyse.objects.get(pk=pk))
    return HttpResponse(content)


@staff_member_required
def analyse_report(request, pk):
    content = render_report(pk)
    return HttpResponse(content)
