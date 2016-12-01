# -*-  coding: utf-8 -*-
"""
"""

from django.conf.urls import url

from com import views

urlpatterns = [
    url(r'^print_invoice/(?P<pk>\d+)/$', views.print_invoice_by_admission),
    url(r'^print_invoice_by_id/(?P<pk>\d+)/$', views.print_invoice_by_id),
    url(r'^next_invoice_id/$', views.next_invoice_id),
    url(r'^invoice_id_of_admission/(?P<pk>\d+)/$', views.invoice_id_of_admission),
]
