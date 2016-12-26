# -*-  coding: utf-8 -*-
"""
"""
import os, sys, re

from django.db import transaction

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "genesis.settings")
import django

django.setup()
from lab.models import *


def line_processor(l):
    return re.sub("^(\d+[\.|-])", "", l.strip().replace('-', ''))


def data_entry(d):
    dot_sep = d.split('.')
    full_name = dot_sep.pop().split(' ')
    title = '.'.join(dot_sep)
    surname = full_name.pop()
    name = ' '.join(full_name)
    ins = Institution(name=d, type=30)
    ins.save()
    doc = Doctor(name=name, surname=surname, title=title, institution=ins)
    doc.save()
    print(doc, ins)


with open(sys.argv[1]) as fh:
    with transaction.atomic():
        for line in fh:
            proc_line = line_processor(line)
            if proc_line:
                data_entry(proc_line)
