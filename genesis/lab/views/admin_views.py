# -*-  coding: utf-8 -*-
"""
"""
from django import forms
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.http import JsonResponse
from lab.lib import render_report
from lab.models import Admission
from lab.models import Analyse


@staff_member_required
def analyse_report(request, pk):
    content = render_report(pk)
    return HttpResponse(content)


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




class Report(forms.Form):
    from_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'vDateField'}),
                                required=False)
    to_date = forms.DateField(widget=forms.TextInput(attrs={'class': 'vDateField'}), required=False)

