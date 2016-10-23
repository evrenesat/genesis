# -*-  coding: utf-8 -*-
"""
"""



from django.conf.urls import url

from lab.views import analyse_barcode, analyse_report, admission_barcode, multiple_reports
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^analyse_barcode/(?P<pk>\d+)/$', analyse_barcode),
    url(r'^analyse_report/(?P<pk>\d+)/$', analyse_report),
    url(r'^admission_barcode/(?P<pk>\d+)/$', admission_barcode),
    url(r'^multiple_reports/$', multiple_reports),
]
