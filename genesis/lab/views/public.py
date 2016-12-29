# -*-  coding: utf-8 -*-
"""
"""
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.views.decorators.cache import cache_control
from lab.models import Admission
from django.utils.translation import ugettext_lazy as _


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
