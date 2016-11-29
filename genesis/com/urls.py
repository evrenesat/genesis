# -*-  coding: utf-8 -*-
"""
"""



from django.conf.urls import url

from com.views import print_invoice
from . import views

urlpatterns = [
    url(r'^print_invoice/(?P<pk>\d+)/$', print_invoice),
]
