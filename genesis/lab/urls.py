# -*-  coding: utf-8 -*-
"""
"""

from django.conf.urls import url

from . import views
urlpatterns = [

    url(r'^api/get_admission/(?P<pk>\d+)/?$', views.get_admission),
    url(r'^api/get_analyse/(?P<pk>\d+)/?$', views.get_analyse),
    url(r'^api/get_admissions/$', views.get_admissions),

    url(r'^api/list_analyse_types/$', views.list_analyse_types),
    url(r'^api/list_analyse_type_states/(?P<pk>\d+)/?$', views.list_analyse_type_states),
    url(r'^api/set_analyse_state/$', views.set_analyse_state),

    url(r'^api/get_user_info/$', views.get_user_info),
    url(r'^api/switch_user/$', views.switch_user),
    url(r'^api/list_analysis/$', views.list_analysis),
    url(r'^api/analyse_state_comments_for_statetype/(?P<pk>\d+)$', views.analyse_state_comments_for_statetype),
    # TODO: this is unused, why!?
    url(r'^api/choices_for_parameter/(?P<pk>\d+)/$', views.choices_for_parameter),


    url(r'^get_admissions_by_analyses/$', views.get_admissions_by_analyses),



    url(r'^papi/analyse_check$', views.analyse_check),
    url(r'^analyse_barcode/(?P<pk>\d+)/$', views.analyse_barcode),
    url(r'^report_for_panel/(?P<group_code>\w+)/$', views.multiple_reports_for_panel),
    url(r'^analyse_report/(?P<pk>\d+)/$', views.analyse_report),
    url(r'^admission_barcode/(?P<pk>\d+)/$', views.admission_barcode),
    url(r'^multiple_reports/$', views.multiple_reports),
]

