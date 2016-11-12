# -*-  coding: utf-8 -*-
"""
"""
from django.template import Context
from django.template import Template

from lab.models import Analyse


def get_base_context(analyse):
    data = {
        'patient_name': analyse.admission.patient.full_name(30),
        'report_date': analyse.approve_time,
        'admission_date': analyse.admission.timestamp,
        'birthdate': analyse.admission.patient.birthdate,
        'short_result': analyse.short_result,
        'indications': analyse.admission.indications,
        'pregnancy_week': analyse.admission.week,
        'admission_id': analyse.admission.id,
        'doctor': analyse.admission.doctor,

        'sample_amount': analyse.sample_amount,
        'sample_type': analyse.sample_type,
        'comment': analyse.comment,
        'approved': analyse.approved,
        'approver': analyse.approver,
        'analyser': analyse.analyser,
        'finished': analyse.finished,
        'note': analyse.type.footnote,
    }
    if str(analyse.admission.doctor) != str(analyse.admission.institution):
        data['institution']= analyse.admission.institution
    return data

def render_report(pk, signed=False):
    analyse = Analyse.objects.get(pk=pk)
    cnt_dict = get_base_context(analyse)
    if analyse.result_json:
        result = analyse.get_result_dict()
        cnt_dict.update(result)
        cnt_dict['results'] = [result]
    cnt_dict.update({'multi': False,
                     'with_sign': signed})
    tpl, tpl_object = load_analyse_template(analyse)
    cnt_dict['generic'] = True
    return tpl.render(Context(cnt_dict))

def render_combo_report(ids, signed=False):
    analyse_results = []
    for id in ids:
        analyse = Analyse.objects.get(pk=id)
        result = analyse.get_result_dict()
        analyse_results.append(result)
    tpl, tpl_object = load_analyse_template(analyse, combo=True)
    cnt_dict = get_base_context(analyse)
    cnt_dict.update({'results': analyse_results,
                     'comment': analyse.comment,
                     'short_result': analyse.short_result,
                     'multi': True,
                     'with_sign': signed,
                     })
    if tpl_object:
        cnt_dict.update({
            'report_title': tpl_object.title,
            'generic': tpl_object.generic,
        })
    else:
        cnt_dict.update({
            'report_title': '',
            'generic': True,
        })

    c = Context(cnt_dict)
    return tpl.render(c)



def load_analyse_template(analyse, **kwargs):
    if analyse.template and not kwargs:
        anl_tpl = analyse.template
    else:
        if 'combo' not in kwargs:
            kwargs['combo'] = False
        anl_tpl = analyse.type.reporttemplate_set.filter(**kwargs)
        if anl_tpl:
            anl_tpl = anl_tpl[0]
        else:
            anl_tpl = None
    fh = open('templates/report_base.html')
    base_template = fh.read()
    fh.close()
    btpl = base_template.replace('{report_template}', anl_tpl.template if anl_tpl else '')
    return Template(btpl), anl_tpl
