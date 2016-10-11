import barcode
from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("foo")


def get_anlyse_barcode(request, anylse_id):
    EAN = barcode.get_barcode_class('ean13')
    ean = EAN(u'5901234123457')
    return ean.raw()
