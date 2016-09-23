# -*-  coding: utf-8 -*-
"""
"""
import os,sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "genesis.settings")
import django
django.setup()
from lab.models import *


anlyzes = {}
sample_medium = {}
sample_amount = {}

samples = {}
methods = {}
categories = {}

def process_row(row):
    name = row[1]
    current_samples = set(row[2].split('/'))
    current_mediums = row[16].split(',')
    if name not in anlyzes:
        assert name, Exception(row)
        a = {
            'name': name,
            'samples': current_samples,
            'mediums': current_mediums,
            'process_time': row[23],
            'method': row[27],
            'amount': "%s %s" % (row[30], row[31]),
            'price': int(
                row[35].replace('TL', '').strip().replace('.00', '').replace(',', '') or 0),
        }
        anlyzes[name] = a
    else:
        a = anlyzes[name]
        a['samples'].add(row[2])

    if a['method'] not in methods:
        methods[a['method']] = Method(name=a['method'].title())
        methods[a['method']].save()
        categories[a['method']] = Category(name=a['method'].title())
        categories[a['method']].save()

    for s in current_samples:
        if s not in sample_amount and row[30]:
            sample_amount[s] = a['amount']
        if s not in sample_medium:
            sample_medium[s] = set(current_mediums)
        else:
            sample_medium[s].update(current_mediums)


import csv

with open('data.csv') as csvfile:
    for row in csv.reader(csvfile, delimiter=',', quotechar='"'):
        if row[1]:
            process_row(row)

for name, mediums in sample_medium.items():
    if name and name not in samples:
        samples[name], new = SampleType.objects.get_or_create(name=name.title())
        samples[name].amount = sample_amount[name]
        samples[name].save()
        for m in mediums:
            medium, new = MediumType.objects.get_or_create(name=m.title())
            medium.save()
            samples[name].medium.add(medium)
        samples[name].save()

for a in anlyzes.values():

    at = AnalyseType(name=a['name'],
                     process_time=a['process_time'] or 0,
                     category=categories[a['method']],
                     method=methods[a['method']],
                     price=a['price']
                     )
    at.save()
    for s in a['samples']:
        if s:
            at.sample_type.add(samples[s])
    at.save()
