# -*-  coding: utf-8 -*-
"""
"""



from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^analyse_barcode/(?P<pk>\d+)/$', 'lab.views.analyse_barcode'),
    url(r'^analyse_report/(?P<pk>\d+)/$', 'lab.views.analyse_report'),
    url(r'^admission_barcode/(?P<pk>\d+)/$', 'lab.views.admission_barcode'),
]
