# -*-  coding: utf-8 -*-
"""
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render
from lab.lib import render_combo_report
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
    nxt = None
    set_list = _set.split(',')
    if _set:
        try:
            nxt = set_list[set_list.index(str(pk)) + 1]
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
        'next': nxt,
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
