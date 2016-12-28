# -*-  coding: utf-8 -*-
"""
"""

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^get_admission/(?P<pk>\d+)/?$', views.get_admission),
    url(r'^get_analyse/(?P<pk>\d+)/?$', views.get_analyse),
    url(r'^get_admissions/$', views.get_admissions),
    url(r'^get_user_info/$', views.get_user_info),
    url(r'^switch_user/$', views.switch_user),
    url(r'^list_analysis/$', views.list_analysis),
    url(r'^get_admissions_by_analyses/$', views.get_admissions_by_analyses),
    url(r'^choices_for_parameter/(?P<pk>\d+)/$', views.choices_for_parameter),
    url(r'^analyse_state_comments_for_statetype/(?P<pk>\d+)$',
        views.analyse_state_comments_for_statetype),
    url(r'^analyse_check$', views.analyse_check),
    url(r'^analyse_barcode/(?P<pk>\d+)/$', views.analyse_barcode),
    url(r'^report_for_panel/(?P<group_code>\w+)/$', views.multiple_reports_for_panel),
    url(r'^analyse_report/(?P<pk>\d+)/$', views.analyse_report),
    url(r'^admission_barcode/(?P<pk>\d+)/$', views.admission_barcode),
    url(r'^multiple_reports/$', views.multiple_reports),
]
